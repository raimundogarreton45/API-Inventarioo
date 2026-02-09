"""
SERVICIO: ALERTAS POR EMAIL CON RESEND

Envía emails usando Resend (3,000 emails gratis/mes).
Resend es más simple y generoso que SendGrid.
"""

import resend
from app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
resend.api_key = settings.resend_api_key


def enviar_alerta_stock_bajo(
    email_destino: str,
    producto_nombre: str,
    sku: str,
    stock_actual: int,
    stock_minimo: int
) -> bool:
    """Envía un email de alerta cuando un producto tiene stock bajo."""
    
    asunto = f"⚠️ Alerta: Stock Bajo - {producto_nombre}"
    
    contenido_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #d9534f;">⚠️ Alerta de Stock Bajo</h2>
                <p>Hola,</p>
                <p>Tu producto ha alcanzado el stock mínimo:</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #d9534f; margin: 20px 0;">
                    <p><strong>Producto:</strong> {producto_nombre}</p>
                    <p><strong>SKU:</strong> {sku}</p>
                    <p><strong>Stock Actual:</strong> <span style="color: #d9534f; font-size: 18px;">{stock_actual}</span> unidades</p>
                    <p><strong>Stock Mínimo:</strong> {stock_minimo} unidades</p>
                </div>
                <p>Te recomendamos reabastecer este producto lo antes posible.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #777;">
                    Este es un mensaje automático de tu sistema de inventario.
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        params = {
            "from": settings.resend_from_email,
            "to": [email_destino],
            "subject": asunto,
            "html": contenido_html,
        }
        
        resend.Emails.send(params)
        logger.info(f"✅ Alerta enviada a {email_destino} para producto {sku}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al enviar email: {str(e)}")
        return False


def probar_envio_email(email_destino: str) -> bool:
    """Prueba que Resend está configurado correctamente."""
    try:
        params = {
            "from": settings.resend_from_email,
            "to": [email_destino],
            "subject": "Prueba de Sistema de Inventario",
            "html": "<p>Este es un email de prueba. Tu sistema está configurado correctamente. ✅</p>",
        }
        
        resend.Emails.send(params)
        logger.info(f"✅ Email de prueba enviado a {email_destino}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error en prueba: {str(e)}")
        return False
