"""
Endpoints de diagnóstico y debug para el sistema de pagos.
==========================================================
Estos endpoints ayudan a verificar que todo esté configurado correctamente.

IMPORTANTE: En producción, considerar restringir acceso a estos endpoints.
==========================================================
"""

from django.http import JsonResponse
from django.conf import settings
import os
import logging

from .services import test_resend_connection, list_available_products, validate_product_files

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Verificación básica de que el backend está corriendo.
    GET /api/payments/health/
    """
    mp_token = os.getenv('MP_ACCESS_TOKEN', '')
    is_production = mp_token.startswith('APP_USR-')
    
    return JsonResponse({
        "status": "ok",
        "message": "Backend running - Datos con Alex",
        "production_mode": is_production,
        "token_type": "production" if is_production else "sandbox/test"
    })


def env_check(request):
    """
    Verificación de variables de entorno configuradas.
    GET /api/payments/env-check/
    
    Útil para diagnosticar problemas de configuración en Railway.
    """
    mp_token = os.getenv('MP_ACCESS_TOKEN', '')
    resend_key = os.getenv('RESEND_API_KEY', '')
    frontend_url = os.getenv('FRONTEND_URL', 'Not Set')
    
    return JsonResponse({
        "environment": {
            "DEBUG": os.getenv('DEBUG', 'Not Set'),
            "FRONTEND_URL": frontend_url,
        },
        "mercado_pago": {
            "token_configured": bool(mp_token),
            "token_prefix": mp_token[:15] + "..." if len(mp_token) > 15 else "Too short",
            "is_production": mp_token.startswith('APP_USR-'),
        },
        "email_resend": {
            "api_key_configured": bool(resend_key),
            "api_key_prefix": resend_key[:10] + "..." if len(resend_key) > 10 else "Not Set",
            "from_name": os.getenv('EMAIL_FROM_NAME', 'Datos con Alex'),
            "from_address": os.getenv('EMAIL_FROM_ADDRESS', 'onboarding@resend.dev'),
            "reply_to": os.getenv('EMAIL_REPLY_TO', 'datos.conalex@gmail.com'),
        },
        "django": {
            "allowed_hosts": os.getenv('ALLOWED_HOSTS', 'Not Set'),
            "secret_key_set": bool(os.getenv('DJANGO_SECRET_KEY')),
        }
    })


def products_check(request):
    """
    Verificación de productos y archivos disponibles.
    GET /api/payments/products-check/
    
    Muestra todos los productos configurados y si sus archivos existen.
    """
    return JsonResponse(list_available_products())


def test_email(request):
    """
    Prueba de envío de email con Resend.
    GET /api/payments/test-email/?to=tu@email.com
    
    NOTA: Solo funciona si RESEND_API_KEY está configurada.
    """
    import resend
    
    destinatario = request.GET.get('to')
    if not destinatario:
        return JsonResponse({
            "status": "error", 
            "message": "Falta parámetro 'to'. Uso: /api/payments/test-email/?to=tu@email.com"
        }, status=400)
    
    # Verificar configuración
    resend_check = test_resend_connection()
    if not resend_check.get("success"):
        return JsonResponse({
            "status": "error",
            "message": "Resend no está configurado",
            "details": resend_check
        }, status=500)
    
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        from_name = os.getenv('EMAIL_FROM_NAME', 'Datos con Alex')
        from_address = os.getenv('EMAIL_FROM_ADDRESS', 'onboarding@resend.dev')
        
        result = resend.Emails.send({
            "from": f"{from_name} <{from_address}>",
            "to": [destinatario],
            "subject": "🧪 Prueba de Email - Datos con Alex",
            "html": """
                <div style="font-family: sans-serif; padding: 20px; background: #1a1a1a; color: white; border-radius: 10px;">
                    <h2 style="color: #22c55e;">✅ Email de Prueba Exitoso</h2>
                    <p>Si estás leyendo esto, el sistema de emails funciona correctamente.</p>
                    <p style="color: #888; font-size: 12px;">Enviado desde el backend de Datos con Alex</p>
                </div>
            """,
            "reply_to": os.getenv('EMAIL_REPLY_TO', 'datos.conalex@gmail.com')
        })
        
        email_id = result.get('id') if isinstance(result, dict) else None
        
        return JsonResponse({
            "status": "ok",
            "message": f"Email de prueba enviado a {destinatario}",
            "resend_id": email_id,
            "from": f"{from_name} <{from_address}>"
        })
        
    except Exception as e:
        logger.exception("Error en test_email")
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }, status=500)


def system_status(request):
    """
    Estado completo del sistema.
    GET /api/payments/system-status/
    
    Resumen de todos los checks para verificar que el sistema está listo.
    """
    mp_token = os.getenv('MP_ACCESS_TOKEN', '')
    resend_key = os.getenv('RESEND_API_KEY', '')
    frontend_url = os.getenv('FRONTEND_URL', '')
    
    # Verificar productos
    products = list_available_products()
    all_products_ready = all(
        p.get("all_files_exist", False) 
        for p in products.get("products", [])
    )
    
    # Calcular status general
    checks = {
        "mp_token_production": mp_token.startswith('APP_USR-'),
        "resend_configured": bool(resend_key),
        "frontend_url_set": bool(frontend_url),
        "all_products_ready": all_products_ready,
        "debug_off": os.getenv('DEBUG', 'True').lower() != 'true',
    }
    
    all_ok = all(checks.values())
    
    return JsonResponse({
        "ready_for_production": all_ok,
        "checks": checks,
        "products": products,
        "recommendation": "🚀 Sistema listo para producción" if all_ok else "⚠️ Revisar checks fallidos"
    })

