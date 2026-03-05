"""
SERVICIO: VENTAS

Contiene la lógica de negocio para registrar ventas.

FLUJO IMPORTANTE:
1. Verificar que el producto existe
2. Verificar que hay suficiente stock
3. Descontar el stock
4. Crear el registro de venta
5. Verificar si necesita enviar alerta de stock bajo
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.models import Sale, Product, User
from app.schemas import SaleCreate
from app.services.alert_service import enviar_alerta_stock_bajo
import logging
import asyncio

logger = logging.getLogger(__name__)


async def registrar_venta(db: Session, venta: SaleCreate, user: User):
    """
    Registra una nueva venta y descuenta el stock automáticamente.
    
    PROCESO:
    1. Buscar el producto
    2. Verificar que pertenece al usuario
    3. Verificar que hay stock suficiente
    4. Descontar el stock
    5. Crear el registro de venta
    6. Verificar si necesita enviar alerta
    
    Args:
        db: Sesión de base de datos
        venta_data: Datos de la venta (producto_id, cantidad)
        usuario: Usuario actual
    
    Retorna:
        tuple: (Sale, alerta_enviada)
            - Sale: Registro de venta creado
            - alerta_enviada: True si se envió alerta de stock bajo
    
    Raises:
        HTTPException: Si el producto no existe, no pertenece al usuario,
                      o no hay stock suficiente
    """
    
    # ============================================
    # 1. BUSCAR EL PRODUCTO
    # ============================================
    
    producto = db.query(Product).filter(
        Product.id == venta_data.producto_id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {venta_data.producto_id} no encontrado"
        )
    
    
    # ============================================
    # 2. VERIFICAR QUE PERTENECE AL USUARIO
    # ============================================
    
    if producto.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para vender este producto"
        )
    
    
    # ============================================
    # 3. VERIFICAR STOCK SUFICIENTE
    # ============================================
    
    if not producto.puede_vender(venta_data.cantidad):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Disponible: {producto.stock_actual}, Solicitado: {venta_data.cantidad}"
        )
    
    
    # ============================================
    # 4. DESCONTAR EL STOCK
    # ============================================
    
    stock_anterior = producto.stock_actual
    producto.stock_actual -= venta_data.cantidad
    
    logger.info(
        f"📉 Stock de {producto.sku} descontado: {stock_anterior} → {producto.stock_actual}"
    )
    
    
    # ============================================
    # 5. CREAR EL REGISTRO DE VENTA
    # ============================================
    
    nueva_venta = Sale(
        producto_id=producto.id,
        cantidad=venta_data.cantidad
    )
    
    db.add(nueva_venta)
    
    
    # ============================================
    # 6. VERIFICAR SI NECESITA ENVIAR ALERTA
    # ============================================
    
    alerta_enviada = False
    
    if producto.necesita_alerta():
        # Programar envío de alerta (función async) en background
        await enviar_alerta_stock_bajo(
        producto=producto,
        user=user,
        db=db
        )
        producto.alerta_enviada = True
        alerta_enviada = True
        logger.warning(
            f"⚠️ Stock de {producto.sku} bajo mínimo. Alerta programada a {usuario.email}"
        )
    
    
    # ============================================
    # 7. GUARDAR TODO EN LA BASE DE DATOS
    # ============================================
    
    db.commit()
    db.refresh(nueva_venta)
    db.refresh(producto)
    
    logger.info(
        f"✅ Venta registrada: {venta_data.cantidad} unidades de {producto.sku}"
    )
    
    return nueva_venta, alerta_enviada


def listar_ventas(
    db: Session, 
    usuario: User, 
    producto_id: int = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Sale]:
    """
    Lista las ventas de un usuario.
    
    Args:
        db: Sesión de base de datos
        usuario: Usuario actual
        producto_id: Si se especifica, filtra por producto
        skip: Número de ventas a saltar (paginación)
        limit: Máximo número de ventas a devolver
    
    Retorna:
        List[Sale]: Lista de ventas
    """
    # Query base: ventas de productos del usuario
    query = db.query(Sale).join(Product).filter(
        Product.usuario_id == usuario.id
    )
    
    # Filtrar por producto si se especificó
    if producto_id:
        query = query.filter(Sale.producto_id == producto_id)
    
    # Ordenar por fecha (más recientes primero)
    query = query.order_by(Sale.fecha.desc())
    
    # Aplicar paginación
    ventas = query.offset(skip).limit(limit).all()
    
    logger.info(f"📊 Usuario {usuario.email} listó {len(ventas)} ventas")
    return ventas


def obtener_venta(db: Session, venta_id: int, usuario: User) -> Sale:
    """
    Obtiene una venta específica.
    
    Args:
        db: Sesión de base de datos
        venta_id: ID de la venta
        usuario: Usuario actual
    
    Retorna:
        Sale: Venta encontrada
    
    Raises:
        HTTPException: Si la venta no existe o no pertenece al usuario
    """
    venta = db.query(Sale).join(Product).filter(
        Sale.id == venta_id,
        Product.usuario_id == usuario.id
    ).first()
    
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venta {venta_id} no encontrada"
        )
    
    return venta


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def obtener_estadisticas_ventas(db: Session, usuario: User) -> dict:
    """
    Obtiene estadísticas de ventas del usuario.
    
    Args:
        db: Sesión de base de datos
        usuario: Usuario actual
    
    Retorna:
        dict: Estadísticas (total_ventas, productos_mas_vendidos, etc.)
    """
    from sqlalchemy import func
    
    # Total de ventas
    total_ventas = db.query(func.count(Sale.id)).join(Product).filter(
        Product.usuario_id == usuario.id
    ).scalar()
    
    # Total de unidades vendidas
    total_unidades = db.query(func.sum(Sale.cantidad)).join(Product).filter(
        Product.usuario_id == usuario.id
    ).scalar() or 0
    
    # Producto más vendido
    producto_mas_vendido = db.query(
        Product.nombre,
        func.sum(Sale.cantidad).label('total')
    ).join(Sale).filter(
        Product.usuario_id == usuario.id
    ).group_by(Product.nombre).order_by(func.sum(Sale.cantidad).desc()).first()
    
    return {
        "total_ventas": total_ventas,
        "total_unidades_vendidas": total_unidades,
        "producto_mas_vendido": {
            "nombre": producto_mas_vendido[0] if producto_mas_vendido else None,
            "cantidad": producto_mas_vendido[1] if producto_mas_vendido else 0
        }
    }
