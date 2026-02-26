import os
import resend
from app.models.product import Product
from app.models.user import User
from sqlalchemy.orm import Session

resend.api_key = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")


async def enviar_alerta_stock_bajo(producto: Product, user: User, db: Session):
    if not ALERT_EMAIL:
        return
    
    if not producto or producto.alerta_enviada:
        return
    
    stock_critico = producto.stock_actual < (producto.stock_minimo * 0.5)
    stock_bajo = producto.stock_actual <= producto.stock_minimo
    
    if not (stock_critico or stock_bajo):
        producto.alerta_enviada = False
        db.commit()
        return
    
    asunto = f"Stock Bajo: {producto.nombre}"
    mensaje = f"El producto {producto.nombre} tiene stock bajo. Stock actual: {producto.stock_actual}"
    
    try:
        resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": ALERT_EMAIL,
            "subject": asunto,
            "html": mensaje
        })
        
        producto.alerta_enviada = True
        db.commit()
        
    except Exception as e:
        print(f"Error al enviar email: {str(e)}")