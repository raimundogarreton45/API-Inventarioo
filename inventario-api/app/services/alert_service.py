# ═══════════════════════════════════════════════════════════

# ARCHIVO: app/services/alert_service.py

# ARREGLADO: Comillas normales (sin tipográficas)

# ═══════════════════════════════════════════════════════════

import os
import resend
from app.models.product import Product
from app.models.user import User
from sqlalchemy.orm import Session

# Configurar Resend

resend.api_key = os.getenv("RESEND_API_KEY")

RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

async def check_and_send_alerts(producto: Product, user: User, db: Session):
“””
Verifica si un producto está bajo en stock y envía alerta.
SIEMPRE envía al ALERT_EMAIL configurado en Railway.
“””

```
# Si no hay ALERT_EMAIL configurado, no enviar
if not ALERT_EMAIL:
    print("⚠️ ALERT_EMAIL no configurado, no se enviarán alertas")
    return

# Si el producto ya no existe, salir
if not producto:
    return

# Verificar si el stock está bajo
stock_critico = producto.stock_actual < (producto.stock_minimo * 0.5)
stock_bajo = producto.stock_actual <= producto.stock_minimo

if not (stock_critico or stock_bajo):
    # Stock OK, resetear flag de alerta
    producto.alerta_enviada = False
    db.commit()
    return

# Si ya se envió alerta, no enviar de nuevo
if producto.alerta_enviada:
    return

# Determinar tipo de alerta
if stock_critico:
    asunto = f"🚨 STOCK CRÍTICO: {producto.nombre}"
    mensaje = f"""
    <h2>⚠️ Alerta de Stock Crítico</h2>
    <p>El producto <strong>{producto.nombre}</strong> tiene stock crítico.</p>
    <ul>
        <li><strong>SKU:</strong> {producto.sku}</li>
        <li><strong>Stock actual:</strong> {producto.stock_actual} unidades</li>
        <li><strong>Stock mínimo:</strong> {producto.stock_minimo} unidades</li>
    </ul>
    <p style="color: red; font-weight: bold;">⚠️ Es urgente reponer este producto.</p>
    <p>Usuario: {user.nombre} ({user.email})</p>
    """
else:
    asunto = f"⚠️ Stock Bajo: {producto.nombre}"
    mensaje = f"""
    <h2>📦 Alerta de Stock Bajo</h2>
    <p>El producto <strong>{producto.nombre}</strong> está llegando al stock mínimo.</p>
    <ul>
        <li><strong>SKU:</strong> {producto.sku}</li>
        <li><strong>Stock actual:</strong> {producto.stock_actual} unidades</li>
        <li><strong>Stock mínimo:</strong> {producto.stock_minimo} unidades</li>
    </ul>
    <p>Considera reponer pronto este producto.</p>
    <p>Usuario: {user.nombre} ({user.email})</p>
    """

# Enviar email
try:
    resend.Emails.send({
        "from": RESEND_FROM_EMAIL,
        "to": ALERT_EMAIL,
        "subject": asunto,
        "html": mensaje
    })
    
    # Marcar como enviada
    producto.alerta_enviada = True
    db.commit()
    
    print(f"✅ Alerta enviada para {producto.sku} a {ALERT_EMAIL}")
    
except Exception as e:
    print(f"❌ Error al enviar email: {str(e)}")
```