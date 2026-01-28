"""
Vistas para integración con Mercado Pago - Flujo de Redirect (Checkout Pro)

Este módulo maneja:
1. Creación de preferencias de pago (create_preference) - SIN DB (Stateless)
2. Validación de pagos exitosos (pago_exitoso) + entrega del archivo
3. Webhook para notificaciones de Mercado Pago (webhook)

NOTA PARA VERCEL: Se eliminó la escritura en SQLite (Order.objects.create)
porque Vercel tiene sistema de archivos de solo lectura.
Los datos del cliente viajan en la metadata de Mercado Pago.
"""

import json
import os
import time
from types import SimpleNamespace
from pathlib import Path
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import mercadopago
from dotenv import load_dotenv

import logging
from .services import send_product_email

logger = logging.getLogger(__name__)

# Cargar variables de entorno desde el directorio backend
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / '.env')

# Inicializar SDK de Mercado Pago
sdk = mercadopago.SDK(os.getenv('MP_ACCESS_TOKEN'))

# URL del frontend para redirecciones
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Ruta al archivo del curso
COURSE_FILE_PATH = os.getenv('COURSE_FILE_PATH', str(BACKEND_DIR / 'files' / 'curso-excel.zip'))


@csrf_exempt
@require_http_methods(["POST"])
def create_preference(request):
    """
    Crea un ID de preferencia en Mercado Pago.
    NO GUARDA EN DB (Stateless para Vercel).
    Guarda datos del usuario en 'metadata' de MP.
    """
    try:
        data = json.loads(request.body)
        
        # Campos requeridos
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        document = data.get('document', '').strip()
        email = data.get('email', '').strip()
        course_id = data.get('course_id', 'curso-excel')
        title = data.get('title', 'Curso AIExcel')
        price = float(data.get('price', 0))
        quantity = int(data.get('quantity', 1))

        if not all([first_name, last_name, email, price]):
             return JsonResponse({'success': False, 'error': 'Faltan datos requeridos'}, status=400)

        # Generar ID temporal (timestamp)
        temp_order_id = int(time.time())

        # Crear preferencia en Mercado Pago con METADATA
        preference_data = {
            "items": [
                {
                    "id": course_id,
                    "title": title,
                    "currency_id": "ARS",
                    "unit_price": price,
                    "quantity": quantity,
                    "description": f"Acceso: {title}",
                    "category_id": "learnings",
                }
            ],
            "back_urls": {
                "success": f"{FRONTEND_URL}/pago-exitoso",
                "failure": f"{FRONTEND_URL}/pago-fallido",
                "pending": f"{FRONTEND_URL}/pago-pendiente",
            },
            # auto_return SOLO funciona con URLs públicas (https), NO con localhost
            **({"auto_return": "approved"} if FRONTEND_URL.startswith("https") else {}),
            "external_reference": str(temp_order_id),
            "statement_descriptor": "ALEXCEL",
            "payer": {
                "name": first_name,
                "surname": last_name,
                "email": email,
                 "identification": {
                    "type": "DNI",
                    "number": document.replace('.', '').replace('-', '')
                }
            },
            # AQUI GUARDAMOS LOS DATOS PARA RECUPERARLOS LUEGO
            "metadata": {
                "customer_first_name": first_name,
                "customer_email": email,
                "course_id": course_id,
                "course_title": title,
                "price": price
            }
        }
        
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})
        
        # Log detallado para debug
        logger.info(f"MP Response Status: {preference_response.get('status')}")
        logger.info(f"MP Response: {preference_response}")
        
        if "id" not in preference:
            error_msg = preference_response.get("response", {}).get("message", "Error desconocido")
            logger.error(f"MP Error Full: {preference_response}")
            return JsonResponse({'success': False, 'error': f'Error MP: {error_msg}'}, status=500)
            
        return JsonResponse({
            'success': True,
            'init_point': preference.get('init_point'),
            'sandbox_init_point': preference.get('sandbox_init_point'),
            'preference_id': preference.get('id'),
            'order_id': temp_order_id
        })
        
    except Exception as e:
        logger.exception("Error create_preference")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pago_exitoso(request):
    """
    Valida pago y envía email consultando a Mercado Pago (Stateless).
    """
    try:
        payment_id = request.GET.get('payment_id') or request.GET.get('collection_id')
        
        if not payment_id:
            return JsonResponse({'success': False, 'error': 'Falta payment_id'}, status=400)
            
        # Consultar a Mercado Pago para sacar los datos (Metadata)
        try:
            payment_response = sdk.payment().get(payment_id)
            if payment_response["status"] != 200:
                return JsonResponse({'success': False, 'error': 'Error MP'}, status=502)
            
            payment_data = payment_response.get("response", {})
            status = payment_data.get("status")
            
            # Leer metadata (MP convierte a snake_case)
            metadata = payment_data.get("metadata", {})
            
            # Reconstruir objeto 'fake order' para el servicio de email
            fake_order = SimpleNamespace(
                id=payment_data.get("external_reference", "000"),
                first_name=metadata.get("customer_first_name", "Cliente"),
                email=metadata.get("customer_email", ""),
                course_title=metadata.get("course_title", "Producto Digital"),
                course_id=metadata.get("course_id", "tracker-habitos"),
                price=metadata.get("price", 0),
                status=status
            )
            
        except Exception as e:
            logger.exception(f"Error recuperando pago {payment_id}")
            return JsonResponse({'success': False, 'error': 'Error de conexión'}, status=502)

        if status == 'approved':
            # ENVIAR EMAIL
            email_sent = False
            if fake_order.email:
                email_sent = send_product_email(fake_order)
            
            return JsonResponse({
                'success': True,
                'status': 'approved',
                'payment_id': payment_id,
                'email_sent': email_sent,
                'message': '¡Pago exitoso! Te enviamos un email con la descarga.'
            })
        else:
            return JsonResponse({
                'success': False, 
                'status': status,
                'message': 'El pago no está aprobado.'
            })

    except Exception as e:
        logger.exception("Error pago_exitoso")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def download_file(request, order_id):
    """
    Endpoint legacy. No funciona en Vercel sin DB.
    """
    return JsonResponse({'error': 'Usa el link enviado a tu email.'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """
    Webhook simplificado (Log only).
    """
    return JsonResponse({'status': 'ok'})
