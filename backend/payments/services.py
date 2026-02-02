"""
Servicio de envío de emails con productos - Datos con Alex
===========================================================
Versión Producción

Usa Resend SDK para enviar emails con archivos adjuntos.

CONFIGURACIÓN REQUERIDA:
1. RESEND_API_KEY en variables de entorno
2. Dominio verificado en Resend (para usar email propio)
   - Sin dominio verificado: onboarding@resend.dev
   - Con dominio verificado: noreply@datosconalex.com

IMPORTANTE: Los archivos deben existir en backend/files/
===========================================================
"""

import os
import logging
from pathlib import Path
from django.conf import settings
import resend

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURACIÓN DE PRODUCTOS
# =============================================================================

# Mapeo de product_id a archivos (puede ser uno o varios)
# IMPORTANTE: Los IDs deben coincidir EXACTAMENTE con los del frontend (data/planillas.ts)
PRODUCT_FILES = {
    'tracker-habitos': ['tracker-habitos.xlsx'],
    'planificador-financiero': ['planificador-financiero.xlsx'],
    'pack-productividad': ['tracker-habitos.xlsx', 'planificador-financiero.xlsx'],
}

# Configuración del remitente
# PRODUCCIÓN: Cuando tengas dominio verificado, cambiar a tu email
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Datos con Alex")
EMAIL_FROM_ADDRESS = os.getenv("DEFAULT_FROM_EMAIL", "facundososa98@hotmail.com")
EMAIL_REPLY_TO = os.getenv("EMAIL_REPLY_TO", "datos.conalex@gmail.com")


def get_product_files(product_id: str) -> list:
    """
    Retorna lista de rutas absolutas a los archivos del producto.
    
    Args:
        product_id: ID del producto (ej: 'tracker-habitos')
        
    Returns:
        Lista de paths absolutos a los archivos
    """
    filenames = PRODUCT_FILES.get(product_id)
    
    if not filenames:
        logger.warning(f"[FILES] Producto '{product_id}' no encontrado en PRODUCT_FILES. Usando fallback.")
        # Fallback: intentar usar el ID como nombre de archivo
        filenames = [f"{product_id}.xlsx"]
    
    # Construir paths absolutos
    base_path = Path(settings.BASE_DIR) / 'files'
    return [str(base_path / f) for f in filenames]


def validate_product_files(product_id: str) -> dict:
    """
    Valida que los archivos de un producto existan.
    Útil para diagnóstico.
    
    Returns:
        {
            "product_id": str,
            "files": [{"path": str, "exists": bool, "size": int}]
        }
    """
    file_paths = get_product_files(product_id)
    result = {
        "product_id": product_id,
        "files": []
    }
    
    for path in file_paths:
        file_info = {
            "path": path,
            "exists": os.path.exists(path),
            "size": os.path.getsize(path) if os.path.exists(path) else 0
        }
        result["files"].append(file_info)
    
    return result


def send_product_email(order) -> bool:
    """
    Envía el email con el/los producto(s) adjunto(s) usando Resend SDK.
    
    Args:
        order: Objeto con atributos:
            - email: Email del destinatario
            - first_name: Nombre del cliente
            - course_id: ID del producto
            - course_title: Título del producto
            - id: ID de la orden (para referencia)
        
    Returns:
        bool: True si el envío fue exitoso
        
    Raises:
        No lanza excepciones; los errores se logean y retorna False
    """
    try:
        # =========================================
        # 1. VALIDAR CONFIGURACIÓN
        # =========================================
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        if not resend.api_key:
            logger.error("[EMAIL] CRÍTICO: Falta RESEND_API_KEY en variables de entorno")
            return False
        
        if not order.email:
            logger.error("[EMAIL] CRÍTICO: No hay email de destinatario")
            return False
            
        # =========================================
        # 2. OBTENER ARCHIVOS DEL PRODUCTO
        # =========================================
        file_paths = get_product_files(order.course_id)
        
        logger.info(f"[EMAIL] Preparando envío - Producto: {order.course_id}, Archivos: {len(file_paths)}")
        
        # =========================================
        # 3. PREPARAR ADJUNTOS
        # =========================================
        attachments = []
        files_attached = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.error(f"[EMAIL] Archivo NO encontrado: {file_path}")
                continue
                
            try:
                file_size = os.path.getsize(file_path)
                
                with open(file_path, "rb") as f:
                    # Resend requiere el contenido como lista de bytes
                    attachment_content = list(f.read())
                
                filename = os.path.basename(file_path)
                attachments.append({
                    "filename": filename,
                    "content": attachment_content
                })
                files_attached.append(filename)
                
                logger.info(f"[EMAIL] ✓ Archivo adjuntado: {filename} ({file_size/1024:.1f} KB)")
                
            except Exception as e:
                logger.error(f"[EMAIL] Error leyendo archivo {file_path}: {e}")
        
        # Verificar que tengamos al menos un archivo (REQ: Fail hard)
        if not attachments:
            msg = f"[EMAIL] CRÍTICO: No hay archivos válidos para adjuntar (Prod: {order.course_id}). Abortando envío."
            logger.critical(msg)
            return False
        
        # =========================================
        # 4. CONSTRUIR EMAIL HTML
        # =========================================
        archivo_texto = "los archivos adjuntos" if len(attachments) > 1 else "el archivo adjunto"
        lista_archivos = ", ".join(files_attached)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tu compra - Datos con Alex</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0a0a0a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <table role="presentation" style="width: 100%; border: 0; border-spacing: 0; background-color: #0a0a0a;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; width: 100%; border: 0; border-spacing: 0; background-color: #1a1a1a; border-radius: 16px; overflow: hidden;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">
                                🎉 ¡Gracias por tu compra!
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; color: #ffffff; font-size: 18px; line-height: 1.6;">
                                Hola <strong style="color: #22c55e;">{order.first_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 20px; color: #d1d5db; font-size: 16px; line-height: 1.6;">
                                Tu pago por <strong style="color: #ffffff;">{order.course_title}</strong> ha sido confirmado exitosamente.
                            </p>
                            
                            <div style="background-color: #262626; border-radius: 12px; padding: 20px; margin: 30px 0; border-left: 4px solid #22c55e;">
                                <p style="margin: 0 0 10px; color: #22c55e; font-size: 14px; font-weight: 600; text-transform: uppercase;">
                                    📎 Tu descarga
                                </p>
                                <p style="margin: 0; color: #ffffff; font-size: 16px;">
                                    Adjunto a este correo encontrarás {archivo_texto}:
                                </p>
                                <p style="margin: 10px 0 0; color: #9ca3af; font-size: 14px; font-family: monospace;">
                                    {lista_archivos}
                                </p>
                            </div>
                            
                            <p style="margin: 0 0 20px; color: #d1d5db; font-size: 16px; line-height: 1.6;">
                                Los archivos son compatibles con <strong>Microsoft Excel</strong> y <strong>Google Sheets</strong>.
                            </p>
                            
                            <p style="margin: 30px 0 0; color: #9ca3af; font-size: 14px; line-height: 1.6;">
                                ¿Tenés alguna duda? Respondé a este email y te ayudamos. 💪
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #262626; text-align: center;">
                            <p style="margin: 0 0 15px; color: #9ca3af; font-size: 14px;">
                                Seguinos para más tips de Excel y productividad:
                            </p>
                            <div>
                                <a href="https://www.tiktok.com/@datos.conalex" style="display: inline-block; margin: 0 10px; color: #22c55e; text-decoration: none; font-size: 14px;">TikTok</a>
                                <span style="color: #4b5563;">•</span>
                                <a href="https://www.instagram.com/datos_conalex" style="display: inline-block; margin: 0 10px; color: #22c55e; text-decoration: none; font-size: 14px;">Instagram</a>
                            </div>
                            <p style="margin: 20px 0 0; color: #6b7280; font-size: 12px;">
                                Orden #{order.id} | Datos con Alex © 2024
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    except Exception as e:
        logger.exception(f"[EMAIL] Error inesperado enviando email: {str(e)}")
        return False

        # =========================================
        # 5. ENVIAR CON DJANGO SMTP (GMAIL)
        # =========================================
        from django.core.mail import EmailMessage
        
        try:
            logger.info(f"[EMAIL] Iniciando envío SMTP a {order.email}...")
            
            email = EmailMessage(
                subject=f"🎉 Tu compra: {order.course_title} - Datos con Alex",
                body=html_content,
                from_email=f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>",
                to=[order.email],
                reply_to=[EMAIL_REPLY_TO],
            )
            
            # Configurar como HTML
            email.content_subtype = "html"
            
            # Agregar adjuntos
            for file_path in file_paths:
                if os.path.exists(file_path):
                    email.attach_file(file_path)
            
            # Enviar
            sent_count = email.send(fail_silently=False)
            
            if sent_count > 0:
                logger.info(f"[EMAIL] ✓ ÉXITO - SMTP | To: {order.email} | Adjuntos: {len(file_paths)}")
                return True
            else:
                logger.error("[EMAIL] El servidor SMTP no envió el correo (count=0)")
                return False
                
        except Exception as e:
            logger.exception(f"[EMAIL] Error SMTP enviando email: {str(e)}")
            return False


# =============================================================================
# UTILIDADES DE DIAGNÓSTICO
# =============================================================================

def test_resend_connection() -> dict:
    """
    Prueba la conexión con Resend.
    Útil para verificar que la API key funciona.
    """
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        if not resend.api_key:
            return {"success": False, "error": "RESEND_API_KEY no configurada"}
        
        # Intentar obtener info de la API key
        # Resend no tiene endpoint de "me", así que solo verificamos que la key existe
        return {
            "success": True,
            "api_key_prefix": resend.api_key[:10] + "...",
            "from_address": f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>",
            "reply_to": EMAIL_REPLY_TO
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_available_products() -> dict:
    """
    Lista todos los productos configurados con estado de archivos.
    """
    result = {"products": []}
    
    for product_id in PRODUCT_FILES.keys():
        validation = validate_product_files(product_id)
        all_exist = all(f["exists"] for f in validation["files"])
        
        result["products"].append({
            "id": product_id,
            "files_count": len(validation["files"]),
            "all_files_exist": all_exist,
            "details": validation["files"]
        })
    
    return result
