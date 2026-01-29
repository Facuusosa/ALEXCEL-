import os
import logging
from django.conf import settings
from .models import Order
import resend

logger = logging.getLogger(__name__)

# Mapeo de product_id a archivo
PRODUCT_FILES = {
    'tracker-habitos': 'tracker-habitos.xlsx',
    'planificador-financiero': 'planificador-financiero.xlsx',
    'pack-productividad': 'pack-productividad.zip',  # Contiene ambos archivos
}

def get_product_file_path(product_id: str) -> str:
    """
    Retorna la ruta al archivo del producto según su ID.
    Si no existe, usa un archivo genérico de prueba.
    """
    filename = PRODUCT_FILES.get(product_id, 'demo-product.xlsx')
    return os.path.join(settings.BASE_DIR, 'files', filename)


def send_product_email(order: Order) -> bool:
    """
    Envía el email automatizado con el producto adjunto usando RESEND SDK.
    
    Args:
        order (Order): Orden aprobada con datos del cliente.
        
    Returns:
        bool: True si el envío fue exitoso.
    """
    try:
        # Configurar API Key
        resend.api_key = os.getenv("RESEND_API_KEY")
        if not resend.api_key:
            logger.error("Falta RESEND_API_KEY en variables de entorno")
            return False
            
        # 1. Definir Ruta del Archivo
        file_path = get_product_file_path(order.course_id)
        file_exists = os.path.exists(file_path)
        
        # En Railway el filesystem es read-only, no intentamos crear archivos si no existen
        if not file_exists:
            logger.warning(f"[EMAIL] Archivo no encontrado: {file_path}")
        
        # 2. Template del Email
        subject = f"🎉 Tu compra: {order.course_title} - Datos con Alex"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; border-bottom: 3px solid #22c55e; padding-bottom: 20px; }}
                .content {{ padding: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Gracias por tu compra!</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{order.first_name}</strong>,</p>
                    <p>Tu pago por <strong>{order.course_title}</strong> ha sido confirmado.</p>
                    <p>Adjunto a este correo encontrarás el archivo para descargar.</p>
                    <p>Si tienes alguna duda, responde a este correo.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 3. Preparar adjuntos
        attachments = []
        if file_exists:
            try:
                with open(file_path, "rb") as f:
                    # Convertir bytes a lista de enteros para Resend
                    attachment_content = list(f.read())
                
                attachments.append({
                    "filename": os.path.basename(file_path),
                    "content": attachment_content
                })
                logger.info(f"[EMAIL] Archivo leído para adjuntar: {file_path}")
            except Exception as e:
                logger.error(f"[EMAIL] Error leyendo archivo: {e}")
        
        # 4. Enviar con Resend
        # IMPORTANTE: free tier solo envía desde onboarding@resend.dev
        params = {
            "from": "Datos con Alex <onboarding@resend.dev>",
            "to": [order.email],
            "subject": subject,
            "html": html_content,
            "reply_to": "datos.conalex@gmail.com", # Tu email real
            "attachments": attachments
        }
        
        r = resend.Emails.send(params)
        logger.info(f"[EMAIL SUCCESS] Resend ID: {r.get('id')}")
        return True

    except Exception as e:
        # Debug directo a consola para Railway
        print(f"!!!! RESEND ERROR !!!!: {str(e)}")
        logger.error(f"[EMAIL ERROR] Fallo al enviar con Resend: {str(e)}")
        return False
