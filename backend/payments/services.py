"""
Servicio de envío de emails con productos - Datos con Alex
===========================================================
Versión Producción - Gmail SMTP

Usa Django EmailBackend conectado a Gmail SMTP para enviar
emails con archivos adjuntos a cualquier destinatario.

CONFIGURACIÓN REQUERIDA EN .env o variables de entorno:
- EMAIL_HOST_USER: Tu email de Gmail
- EMAIL_HOST_PASSWORD: App Password de Gmail (16 caracteres)

IMPORTANTE: Los archivos deben existir en backend/files/
===========================================================
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Optional

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURACIÓN DE PRODUCTOS
# =============================================================================

# Mapeo de product_id a archivos (puede ser uno o varios)
# IMPORTANTE: Los IDs deben coincidir EXACTAMENTE con los del frontend (data/planillas.ts)
PRODUCT_FILES: dict[str, list[str]] = {
    'tracker-habitos': ['tracker-habitos.xlsx'],
    'planificador-financiero': ['planificador-financiero.xlsx'],
    'pack-productividad': ['tracker-habitos.xlsx', 'planificador-financiero.xlsx'],
}


# =============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# =============================================================================

def validate_email_config() -> dict[str, Any]:
    """
    Valida que las variables de entorno críticas para email estén configuradas.
    
    Returns:
        Dict con estado de configuración y errores si los hay.
    """
    errors: list[str] = []
    warnings: list[str] = []
    
    email_host_user = os.environ.get('EMAIL_HOST_USER', '')
    email_host_password = os.environ.get('EMAIL_HOST_PASSWORD', '')
    
    if not email_host_user:
        errors.append("EMAIL_HOST_USER no está configurado")
    elif '@' not in email_host_user:
        warnings.append("EMAIL_HOST_USER no parece ser un email válido")
    
    if not email_host_password:
        errors.append("EMAIL_HOST_PASSWORD no está configurado")
    elif len(email_host_password) < 10:
        warnings.append("EMAIL_HOST_PASSWORD parece muy corto (¿es un App Password?)")
    
    is_valid = len(errors) == 0
    
    if errors:
        for error in errors:
            logger.critical(f"[EMAIL CONFIG] ❌ {error}")
    if warnings:
        for warning in warnings:
            logger.warning(f"[EMAIL CONFIG] ⚠️ {warning}")
    
    return {
        "valid": is_valid,
        "email_configured": bool(email_host_user),
        "password_configured": bool(email_host_password),
        "errors": errors,
        "warnings": warnings
    }


# =============================================================================
# FUNCIONES DE ARCHIVOS
# =============================================================================

def get_product_files(product_id: str) -> list[str]:
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
        filenames = [f"{product_id}.xlsx"]
    
    base_path = Path(settings.BASE_DIR) / 'files'
    return [str(base_path / f) for f in filenames]


def validate_product_files(product_id: str) -> dict[str, Any]:
    """
    Valida que los archivos de un producto existan.
    Útil para diagnóstico.
    
    Returns:
        Dict con información de cada archivo
    """
    file_paths = get_product_files(product_id)
    result: dict[str, Any] = {
        "product_id": product_id,
        "files": []
    }
    
    for path in file_paths:
        file_info = {
            "path": path,
            "filename": os.path.basename(path),
            "exists": os.path.exists(path),
            "size": os.path.getsize(path) if os.path.exists(path) else 0
        }
        result["files"].append(file_info)
    
    return result


# =============================================================================
# ENVÍO DE EMAIL - FUNCIÓN PRINCIPAL
# =============================================================================

class OrderData:
    """Interfaz para datos de orden (Type Hint helper)."""
    course_id: str
    course_title: str
    first_name: str
    email: str


def send_product_email(order: Any) -> bool:
    """
    Envía el email con el/los producto(s) adjunto(s) usando Django EmailBackend (Gmail SMTP).
    
    Args:
        order: Objeto con atributos: course_id, course_title, first_name, email
        
    Returns:
        True si el email se envió correctamente, False en caso contrario.
        
    Raises:
        No levanta excepciones - todos los errores se loguean y retorna False.
    """
    # 0. Validar configuración antes de intentar enviar
    config_check = validate_email_config()
    if not config_check["valid"]:
        logger.critical("[EMAIL ABORTED] Configuración de email inválida. Revisar variables de entorno.")
        return False
    
    try:
        # 1. Validar datos del destinatario
        recipient_email: str = getattr(order, 'email', '')
        customer_name: str = getattr(order, 'first_name', 'Cliente')
        product_id: str = getattr(order, 'course_id', '')
        product_title: str = getattr(order, 'course_title', 'Producto Digital')
        
        if not recipient_email or '@' not in recipient_email:
            logger.error(f"[EMAIL ABORTED] Email de destinatario inválido: '{recipient_email}'")
            return False
        
        if not product_id:
            logger.error("[EMAIL ABORTED] No se especificó product_id/course_id")
            return False
        
        # 2. Obtener archivos del producto
        file_paths = get_product_files(product_id)
        
        # 3. Construir HTML del email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #22c55e; margin-bottom: 20px;">🎉 ¡Gracias por tu compra!</h1>
                <p style="font-size: 16px;">Hola <strong>{customer_name}</strong>,</p>
                <p style="font-size: 16px;">Tu pedido <strong>{product_title}</strong> está confirmado.</p>
                <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #22c55e;">
                    <p style="margin: 0; font-size: 16px;">
                        📎 <strong>Tus archivos están adjuntos a este correo.</strong>
                    </p>
                </div>
                <p style="font-size: 14px; color: #666;">¿Alguna duda? Respondé directamente a este email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999; text-align: center;">
                    Datos con Alex · Tu compañero de productividad
                </p>
            </div>
        </body>
        </html>
        """

        # 4. Crear objeto EmailMessage
        from_email: str = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
        reply_to: str = settings.EMAIL_HOST_USER
        
        email = EmailMessage(
            subject=f"🎉 Tu compra: {product_title}",
            body=html_content,
            from_email=from_email,
            to=[recipient_email],
            reply_to=[reply_to] if reply_to else None
        )
        email.content_subtype = "html"

        # 5. Adjuntar archivos
        attachments_count: int = 0
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    email.attach_file(file_path)
                    attachments_count += 1
                    logger.info(f"[EMAIL] ✅ Adjuntado: {os.path.basename(file_path)}")
                except Exception as attach_error:
                    logger.error(f"[EMAIL] ❌ Error adjuntando {file_path}: {attach_error}")
            else:
                logger.error(f"[EMAIL] ❌ Archivo NO encontrado: {file_path}")

        if attachments_count == 0:
            logger.critical(f"[EMAIL ABORTED] No hay archivos válidos para enviar. Producto: {product_id}")
            return False

        # 6. ENVIAR
        logger.info(f"[EMAIL] 📤 Enviando a {recipient_email}...")
        email.send(fail_silently=False)
        
        logger.info(f"[EMAIL SUCCESS] ✅ Email enviado a {recipient_email} vía Gmail SMTP ({attachments_count} adjuntos)")
        return True

    except Exception as e:
        logger.exception(f"[EMAIL FAILED] ❌ Error crítico enviando email: {str(e)}")
        return False


# =============================================================================
# UTILIDADES DE DIAGNÓSTICO
# =============================================================================

def test_email_connection() -> dict[str, Any]:
    """
    Prueba la configuración de email sin enviar nada.
    Útil para verificar que las credenciales están bien.
    
    Returns:
        Dict con estado de la configuración
    """
    config = validate_email_config()
    
    return {
        "service": "Gmail SMTP",
        "host": os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
        "port": os.environ.get('EMAIL_PORT', '587'),
        "tls_enabled": os.environ.get('EMAIL_USE_TLS', 'True'),
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "config_valid": config["valid"],
        "errors": config["errors"],
        "warnings": config["warnings"]
    }


def list_available_products() -> dict[str, Any]:
    """
    Lista todos los productos configurados con estado de archivos.
    
    Returns:
        Dict con lista de productos y su disponibilidad
    """
    result: dict[str, Any] = {"products": []}
    
    for product_id in PRODUCT_FILES.keys():
        validation = validate_product_files(product_id)
        all_exist = all(f["exists"] for f in validation["files"])
        
        result["products"].append({
            "id": product_id,
            "files_count": len(validation["files"]),
            "all_files_exist": all_exist,
            "ready": all_exist,
            "details": validation["files"]
        })
    
    return result
