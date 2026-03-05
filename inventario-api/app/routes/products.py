"""
RUTAS: PRODUCTOS

Define todos los endpoints relacionados con productos.

ENDPOINTS:
- POST /products          → Crear producto
- GET /products           → Listar productos
- GET /products/{id}      → Obtener un producto
- PUT /products/{id}      → Actualizar producto
- PUT /products/{id}/stock → Actualizar solo el stock
- PATCH /products/{id}/reponer → Reponer stock (sumar cantidad)
- DELETE /products/{id}   → Eliminar producto
"""

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Product, Sale
from app.schemas import (
    ProductCreate, 
    ProductUpdate, 
    StockUpdate,
    ProductResponse, 
    ProductListResponse
)
from app.services import (
    crear_producto,
    listar_productos,
    obtener_producto,
    actualizar_producto,
    actualizar_stock,
    eliminar_producto
)

logger = logging.getLogger(__name__)

# Crear el router
router = APIRouter(
    prefix="/products",
    tags=["Productos"]
)


# ============================================
# CREAR PRODUCTO
# ============================================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
    description="""
    Crea un nuevo producto en el inventario.
    
    **Campos requeridos:**
    - nombre: Nombre descriptivo del producto
    - sku: Código único del producto (no se puede repetir)
    - stock_actual: Cantidad inicial en inventario
    - stock_minimo: Cantidad mínima antes de enviar alerta
    
    **Requiere autenticación.**
    """
)
def crear_nuevo_producto(
    producto: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para crear un producto.
    
    El producto se asocia automáticamente al usuario autenticado.
    """
    return crear_producto(db, producto, current_user)


# ============================================
# LISTAR PRODUCTOS
# ============================================

@router.get(
    "",
    response_model=ProductListResponse,
    summary="Listar productos",
    description="""
    Lista todos los productos del usuario autenticado.
    
    **Filtros disponibles:**
    - stock_bajo: Si es true, solo muestra productos con stock bajo el mínimo
    
    **Paginación:**
    - skip: Número de productos a saltar
    - limit: Máximo de productos a devolver
    
    **Requiere autenticación.**
    """
)
def listar_mis_productos(
    skip: int = Query(0, ge=0, description="Productos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de productos"),
    stock_bajo: Optional[bool] = Query(None, description="Filtrar por stock bajo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para listar productos.
    
    Devuelve solo los productos del usuario autenticado.
    """
    productos = listar_productos(db, current_user, skip, limit, stock_bajo)
    
    return {
        "total": len(productos),
        "products": productos
    }


# ============================================
# OBTENER UN PRODUCTO
# ============================================

@router.get(
    "/{producto_id}",
    response_model=ProductResponse,
    summary="Obtener un producto específico",
    description="""
    Obtiene los detalles de un producto por su ID.
    
    **Requiere autenticación.**
    Solo se puede ver productos propios.
    """
)
def obtener_detalle_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para obtener un producto específico.
    """
    return obtener_producto(db, producto_id, current_user)


# ============================================
# ACTUALIZAR PRODUCTO (COMPLETO)
# ============================================

@router.put(
    "/{producto_id}",
    response_model=ProductResponse,
    summary="Actualizar un producto",
    description="""
    Actualiza los datos de un producto existente.
    
    Puedes actualizar cualquiera de estos campos:
    - nombre
    - sku
    - stock_actual
    - stock_minimo
    
    **Requiere autenticación.**
    Solo puedes actualizar tus propios productos.
    """
)
def actualizar_datos_producto(
    producto_id: int,
    producto: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para actualizar un producto.
    """
    return actualizar_producto(db, producto_id, producto, current_user)


# ============================================
# ACTUALIZAR SOLO EL STOCK
# ============================================

@router.put(
    "/{producto_id}/stock",
    response_model=ProductResponse,
    summary="Actualizar el stock de un producto",
    description="""
    Actualiza únicamente el stock de un producto.
    
    Este endpoint es útil cuando recibes mercancía nueva
    y quieres aumentar el stock manualmente.
    
    **Nota:** El stock también se descuenta automáticamente
    al registrar ventas usando POST /sales
    
    **Requiere autenticación.**
    """
)
def actualizar_stock_producto(
    producto_id: int,
    stock: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para actualizar solo el stock.
    
    Si el nuevo stock está por encima del mínimo,
    se resetea la bandera de alerta.
    
    Si el nuevo stock está bajo el mínimo Y no se ha enviado alerta,
    se envía un email automáticamente.
    """
    return actualizar_stock(db, producto_id, stock, current_user)


# ============================================
# REPONER STOCK (SUMAR CANTIDAD)
# ============================================

@router.patch(
    "/{producto_id}/reponer",
    response_model=ProductResponse,
    summary="Reponer stock de un producto",
    description="""
    Suma una cantidad al stock actual del producto.
    
    **Diferencia con PUT /stock:**
    - PUT /stock: Reemplaza el stock con un nuevo valor
    - PATCH /reponer: Suma una cantidad al stock actual
    
    **Ejemplo:**
    Si el producto tiene 5 unidades y envías cantidad=10,
    el stock quedará en 15 unidades.
    
    **Requiere autenticación.**
    Solo se puede reponer stock de productos propios.
    """
)
def reponer_stock_producto(
    producto_id: int,
    cantidad: int = Query(..., ge=1, description="Cantidad a reponer (debe ser positiva)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para reponer stock de un producto.
    
    Suma la cantidad especificada al stock actual.
    """
    # Buscar el producto
    producto = db.query(Product).filter(
        Product.id == producto_id,
        Product.usuario_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {producto_id} no encontrado"
        )
    
    # Reponer stock (sumar)
    stock_anterior = producto.stock_actual
    producto.stock_actual += cantidad
    
    # Si el stock vuelve a estar sobre el mínimo, resetear la alerta
    if producto.stock_actual >= producto.stock_minimo:
        producto.alerta_enviada = False
    
    db.commit()
    db.refresh(producto)
    
    logger.info(
        f"📦 Stock de {producto.sku} repuesto: {stock_anterior} → {producto.stock_actual} (+{cantidad})"
    )
    
    # ✅ RETORNAR CON TODOS LOS CAMPOS REQUERIDOS
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "sku": producto.sku,
        "stock_actual": producto.stock_actual,
        "stock_minimo": producto.stock_minimo,
        "usuario_id": producto.usuario_id,  # ✅ ESTO FALTABA
        "alerta_enviada": producto.alerta_enviada,
        "created_at": producto.created_at,
        "updated_at": producto.updated_at
    }


# ============================================
# ELIMINAR PRODUCTO (CON MANEJO DE VENTAS)
# ============================================

@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto",
    description="""
    Elimina un producto del inventario.
    
    Si el producto tiene ventas asociadas, estas se desvinculan
    automáticamente antes de eliminar el producto.
    
    ⚠️ **ADVERTENCIA:** Esta acción no se puede deshacer.
    
    **Requiere autenticación.**
    Solo puedes eliminar tus propios productos.
    """
)
def eliminar_producto_endpoint(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para eliminar un producto.
    
    Maneja la eliminación de ventas asociadas automáticamente.
    """
    # Buscar el producto
    producto = db.query(Product).filter(
        Product.id == producto_id,
        Product.usuario_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {producto_id} no encontrado"
        )
    
    # ✅ DESVINCULAR VENTAS EN UNA SOLA OPERACIÓN
    num_ventas = db.query(Sale).filter(Sale.producto_id == producto_id).update(
        {"producto_id": None},
        synchronize_session=False
    )
    
    if num_ventas > 0:
        logger.warning(
            f"🔗 {num_ventas} ventas desvinculadas del producto {producto.sku}"
        )
    
    # Eliminar el producto
    db.delete(producto)
    db.commit()
    
    logger.info(f"🗑️ Producto {producto.sku} eliminado por {current_user.email}")
    
    return None  # 204 No Content no devuelve body