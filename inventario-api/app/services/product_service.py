"""
SERVICIO: PRODUCTOS

Contiene toda la lógica de negocio relacionada con productos.

SEPARACIÓN DE RESPONSABILIDADES:
- Routes (routes/products.py): Recibe peticiones HTTP
- Service (este archivo): Ejecuta la lógica de negocio
- Models (models/product.py): Define estructura de datos
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional

from app.models import Product, User
from app.schemas import ProductCreate, ProductUpdate, StockUpdate
from app.services.alert_service import enviar_alerta_stock_bajo
import logging
import asyncio

logger = logging.getLogger(__name__)


def crear_producto(db: Session, producto_data: ProductCreate, usuario: User) -> Product:
    """
    Crea un nuevo producto en la base de datos.
    
    Args:
        db: Sesión de base de datos
        producto_data: Datos del producto a crear
        usuario: Usuario dueño del producto
    
    Retorna:
        Product: Producto creado
    
    Raises:
        HTTPException: Si el SKU ya existe
    """
    try:
        # Crear instancia del modelo Product
        nuevo_producto = Product(
            nombre=producto_data.nombre,
            sku=producto_data.sku,
            stock_actual=producto_data.stock_actual,
            stock_minimo=producto_data.stock_minimo,
            usuario_id=usuario.id
        )
        
        # Guardar en la base de datos
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)  # Actualiza el objeto con datos de la BD (como el ID)
        
        logger.info(f"✅ Producto creado: {nuevo_producto.sku} por usuario {usuario.email}")
        return nuevo_producto
    
    except IntegrityError:
        db.rollback()
        # IntegrityError ocurre cuando el SKU ya existe (unique constraint)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con el SKU '{producto_data.sku}'"
        )


def listar_productos(
    db: Session, 
    usuario: User, 
    skip: int = 0, 
    limit: int = 100,
    stock_bajo: Optional[bool] = None
) -> List[Product]:
    """
    Lista los productos de un usuario.
    
    Args:
        db: Sesión de base de datos
        usuario: Usuario actual
        skip: Número de productos a saltar (para paginación)
        limit: Máximo número de productos a devolver
        stock_bajo: Si True, solo devuelve productos con stock bajo
    
    Retorna:
        List[Product]: Lista de productos
    """
    # Query base: productos del usuario
    query = db.query(Product).filter(Product.usuario_id == usuario.id)
    
    # Filtrar por stock bajo si se especificó
    if stock_bajo is True:
        # Productos donde stock_actual <= stock_minimo
        query = query.filter(Product.stock_actual <= Product.stock_minimo)
    
    # Aplicar paginación y devolver
    productos = query.offset(skip).limit(limit).all()
    
    logger.info(f"📋 Usuario {usuario.email} listó {len(productos)} productos")
    return productos


def obtener_producto(db: Session, producto_id: int, usuario: User) -> Product:
    """
    Obtiene un producto específico.
    
    Args:
        db: Sesión de base de datos
        producto_id: ID del producto
        usuario: Usuario actual
    
    Retorna:
        Product: Producto encontrado
    
    Raises:
        HTTPException: Si el producto no existe o no pertenece al usuario
    """
    producto = db.query(Product).filter(
        Product.id == producto_id,
        Product.usuario_id == usuario.id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {producto_id} no encontrado"
        )
    
    return producto


def actualizar_producto(
    db: Session, 
    producto_id: int, 
    producto_data: ProductUpdate, 
    usuario: User
) -> Product:
    """
    Actualiza un producto existente.
    
    Args:
        db: Sesión de base de datos
        producto_id: ID del producto a actualizar
        producto_data: Nuevos datos del producto
        usuario: Usuario actual
    
    Retorna:
        Product: Producto actualizado
    """
    # Obtener el producto (esto verifica que existe y pertenece al usuario)
    producto = obtener_producto(db, producto_id, usuario)
    
    # Actualizar solo los campos que se enviaron
    update_data = producto_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(producto, field, value)
    
    # Si el stock se actualizó y ahora está por encima del mínimo,
    # resetear la bandera de alerta
    if "stock_actual" in update_data:
        if producto.stock_actual > producto.stock_minimo:
            producto.alerta_enviada = False
    
    db.commit()
    db.refresh(producto)
    
    logger.info(f"✏️ Producto {producto.sku} actualizado por {usuario.email}")
    return producto


def actualizar_stock(
    db: Session, 
    producto_id: int, 
    stock_data: StockUpdate, 
    usuario: User
) -> Product:
    """
    Actualiza solo el stock de un producto.
    
    Esta función también verifica si necesita enviar alerta.
    
    Args:
        db: Sesión de base de datos
        producto_id: ID del producto
        stock_data: Nuevo valor de stock
        usuario: Usuario actual
    
    Retorna:
        Product: Producto con stock actualizado
    """
    producto = obtener_producto(db, producto_id, usuario)
    
    # Guardar el stock anterior para logging
    stock_anterior = producto.stock_actual
    
    # Actualizar el stock
    producto.stock_actual = stock_data.stock_actual
    
    # Si el stock subió por encima del mínimo, resetear alerta
    if producto.stock_actual > producto.stock_minimo:
        producto.alerta_enviada = False
        logger.info(f"🔄 Stock de {producto.sku} recuperado. Resetear alerta.")
    
    # Si el stock está bajo Y no se ha enviado alerta, enviarla
    elif producto.necesita_alerta():
        # Programar envío de alerta (función async) en background
        asyncio.create_task(
            enviar_alerta_stock_bajo(producto=producto, user=usuario, db=db)
        )
        producto.alerta_enviada = True
        logger.warning(f"⚠️ Stock bajo en {producto.sku}. Alerta programada.")
    
    db.commit()
    db.refresh(producto)
    
    logger.info(
        f"📦 Stock de {producto.sku} actualizado: {stock_anterior} → {producto.stock_actual}"
    )
    
    return producto


def eliminar_producto(db: Session, producto_id: int, usuario: User) -> None:
    """
    Elimina un producto.
    
    Args:
        db: Sesión de base de datos
        producto_id: ID del producto a eliminar
        usuario: Usuario actual
    
    Raises:
        HTTPException: Si el producto no existe o no pertenece al usuario
    """
    producto = obtener_producto(db, producto_id, usuario)
    
    db.delete(producto)
    db.commit()
    
    logger.info(f"🗑️ Producto {producto.sku} eliminado por {usuario.email}")
