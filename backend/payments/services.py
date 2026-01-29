import os
import logging
from django.conf import settings
from .models import Order
import resend

logger = logging.getLogger(__name__)

# Mapeo de product_id a archivos (puede ser uno o varios)
PRODUCT_FILES = {
    'tracker-habitos': ['tracker-habitos.xlsx'],
    'planificador-financiero': ['planificador-financiero.xlsx'],
    'pack-productividad': ['tracker-habitos.xlsx', 'planificador-financiero.xlsx'],  # AMBOS archivos
}

def get_product_files(product_id: str) -> list:
    """
    Retorna lista de rutas a los archivos del producto según su ID.
    """
    filenames = PRODUCT_FILES.get(product_id, ['demo-product.xlsx'])
    return [os.path.join(settings.BASE_DIR, 'files', f) for f in filenames]


def send_product_email(order: Order) -> bool:
    """
    Envía el email automatizado con el/los producto(s) adjunto(s) usando RESEND SDK.
    
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
            
        # 1. Obtener archivos del producto
        file_paths = get_product_files(order.course_id)
        
        # 2. Template del Email
        subject = f"🎉 Tu compra: {order.course_title} - Datos con Alex"
        
        # Texto dinámico según cantidad de archivos
        archivo_texto = "los archivos adjuntos" if len(file_paths) > 1 else "el archivo adjunto"
        
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
                    <p>Adjunto a este correo encontrarás {archivo_texto} para descargar.</p>
                    <p>Si tienes alguna duda, responde a este correo.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 3. Preparar adjuntos (MÚLTIPLES si es pack)
        attachments = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        attachment_content = list(f.read())
                    
                    attachments.append({
                        "filename": os.path.basename(file_path),
                        "content": attachment_content
                    })
                    logger.info(f"[EMAIL] Archivo adjuntado: {file_path}")
                except Exception as e:
                    logger.error(f"[EMAIL] Error leyendo archivo {file_path}: {e}")
            else:
                logger.warning(f"[EMAIL] Archivo no encontrado: {file_path}")
        
        # 4. Enviar con Resend
        params = {
            "from": "Datos con Alex <onboarding@resend.dev>",
            "to": [order.email],
            "subject": subject,
            "html": html_content,
            "reply_to": "facundososa98@hotmail.com",
            "attachments": attachments
        }
        
        r = resend.Emails.send(params)
        logger.info(f"[EMAIL SUCCESS] Resend ID: {r.get('id')} - Adjuntos: {len(attachments)}")
        return True

    except Exception as e:
        print(f"!!!! RESEND ERROR !!!!: {str(e)}")
        logger.error(f"[EMAIL ERROR] Fallo al enviar con Resend: {str(e)}")
        return False
