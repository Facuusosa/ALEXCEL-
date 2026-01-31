"""
Vistas para integración con Mercado Pago - Flujo de Redirect (Checkout Pro)
=============================================================================
VERSIÓN PRODUCCIÓN - "Datos con Alex"

Este módulo maneja:
1. create_preference - Crea preferencias de pago con metadata del cliente
2. pago_exitoso - Valida pagos por redirección y envía emails
3. webhook - FUENTE DE VERDAD para notificaciones de Mercado Pago (backup)

ARQUITECTURA STATELESS:
- No usamos base de datos para órdenes
- Los datos del cliente viajan en la metadata de Mercado Pago
- El webhook actúa como backup si pago_exitoso falla

IMPORTANTE PARA PRODUCCIÓN:
- MP_ACCESS_TOKEN debe ser APP_USR-xxxx (no TEST-xxxx)
- FRONTEND_URL debe apuntar al dominio de Vercel
- RESEND_API_KEY debe estar configurada
=============================================================================
"""

import json
import os
import time
import hashlib
import hmac
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

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / '.env')

# Inicializar SDK de Mercado Pago
MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN', '')
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# URL del frontend para redirecciones (Railway/Vercel)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Modo debug (desactivar en producción)
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# Cache simple en memoria para evitar envío duplicado de emails
# En producción real, usar Redis o similar
_processed_payments = set()


def is_production_token():
    """Verifica si estamos usando credenciales de producción."""
    return MP_ACCESS_TOKEN.startswith('APP_USR-')


def log_payment_event(event_type: str, payment_id: str, details: dict):
    """Log estructurado para monitoreo en Railway."""
    log_data = {
        "event": event_type,
        "payment_id": payment_id,
        "production": is_production_token(),
        **details
    }
    logger.info(f"[PAYMENT_EVENT] {json.dumps(log_data)}")


# =============================================================================
# CREATE PREFERENCE - Inicia el flujo de pago
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_preference(request):
    """
    Crea un ID de preferencia en Mercado Pago.
    
    STATELESS: Los datos del cliente se guardan en 'metadata' de MP,
    no en base de datos local.
    
    Request Body:
    {
        "first_name": "Juan",
        "last_name": "Pérez",
        "document": "12345678",
        "email": "cliente@email.com",
        "course_id": "tracker-habitos",
        "title": "Tracker de Hábitos",
        "price": 1.00,
        "quantity": 1
    }
    
    Response:
    {
        "success": true,
        "init_point": "https://www.mercadopago.com.ar/checkout/...",
        "preference_id": "xxx-xxx-xxx",
        "order_id": 1234567890
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validar campos requeridos
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        document = data.get('document', '').strip()
        email = data.get('email', '').strip().lower()
        course_id = data.get('course_id', 'tracker-habitos')
        title = data.get('title', 'Producto Digital')
        price = float(data.get('price', 0))
        quantity = int(data.get('quantity', 1))

        # Validaciones básicas
        if not all([first_name, last_name, email, price]):
            return JsonResponse({
                'success': False, 
                'error': 'Faltan datos requeridos (nombre, apellido, email, precio)'
            }, status=400)
        
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False, 
                'error': 'Email inválido'
            }, status=400)
        
        if price <= 0:
            return JsonResponse({
                'success': False, 
                'error': 'El precio debe ser mayor a 0'
            }, status=400)

        # Generar ID de referencia (timestamp único)
        temp_order_id = int(time.time() * 1000)  # Milisegundos para mayor unicidad

        # Construir preferencia de Mercado Pago
        preference_data = {
            "items": [
                {
                    "id": course_id,
                    "title": title,
                    "currency_id": "ARS",
                    "unit_price": price,
                    "quantity": quantity,
                    "description": f"Archivo Excel: {title}",
                    "category_id": "learnings",
                }
            ],
            "back_urls": {
                "success": f"{FRONTEND_URL}/pago-exitoso",
                "failure": f"{FRONTEND_URL}/pago-fallido",
                "pending": f"{FRONTEND_URL}/pago-pendiente",
            },
            "auto_return": "approved",
            "external_reference": str(temp_order_id),
            "statement_descriptor": "DATOS CON ALEX",
            "payer": {
                "name": first_name,
                "surname": last_name,
                "email": email,
                "identification": {
                    "type": "DNI",
                    "number": document.replace('.', '').replace('-', '').replace(' ', '')
                }
            },
            # METADATA CRÍTICA - Aquí viajan los datos del cliente
            "metadata": {
                "customer_first_name": first_name,
                "customer_last_name": last_name,
                "customer_email": email,
                "course_id": course_id,
                "course_title": title,
                "price": price,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Log de inicio
        log_payment_event("PREFERENCE_CREATING", str(temp_order_id), {
            "email": email,
            "course": course_id,
            "price": price,
            "frontend_url": FRONTEND_URL
        })
        
        # Crear preferencia en MP
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})
        
        if "id" not in preference:
            error_msg = preference_response.get("response", {}).get("message", "Error desconocido de Mercado Pago")
            logger.error(f"[MP_ERROR] create_preference failed: {preference_response}")
            return JsonResponse({
                'success': False, 
                'error': f'Error MP: {error_msg}'
            }, status=500)
        
        log_payment_event("PREFERENCE_CREATED", str(temp_order_id), {
            "preference_id": preference.get('id'),
            "init_point": preference.get('init_point', '')[:50] + "..."
        })
            
        # Respuesta exitosa
        # PRODUCCIÓN: usamos init_point
        # SANDBOX: usamos sandbox_init_point
        response_data = {
            'success': True,
            'preference_id': preference.get('id'),
            'order_id': temp_order_id
        }
        
        if is_production_token():
            response_data['init_point'] = preference.get('init_point')
        else:
            response_data['init_point'] = preference.get('sandbox_init_point')
            response_data['sandbox_init_point'] = preference.get('sandbox_init_point')
            
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': 'JSON inválido en el request'
        }, status=400)
    except Exception as e:
        logger.exception("[CRITICAL] Error en create_preference")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# PAGO EXITOSO - Validación por redirección (usuario presente)
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def pago_exitoso(request):
    """
    Valida el pago consultando a MP y envía el email.
    
    Este endpoint se llama cuando:
    1. MP redirige al usuario después de pagar
    2. El frontend llama para validar y disparar el envío de email
    
    Query Params (enviados por MP):
    - payment_id o collection_id
    - status
    - external_reference
    
    IMPORTANTE: Este es el método PRIMARIO de entrega.
    El webhook es backup.
    """
    try:
        # Obtener payment_id de los parámetros
        payment_id = request.GET.get('payment_id') or request.GET.get('collection_id')
        
        if not payment_id:
            logger.warning("[VALIDATE] Llamada sin payment_id")
            return JsonResponse({
                'success': False, 
                'error': 'Falta payment_id en la URL'
            }, status=400)
        
        log_payment_event("VALIDATE_START", payment_id, {
            "source": "pago_exitoso",
            "params": dict(request.GET)
        })
        
        # Consultar a Mercado Pago para obtener datos REALES del pago
        try:
            payment_response = sdk.payment().get(payment_id)
            
            if payment_response.get("status") != 200:
                logger.error(f"[MP_ERROR] get payment {payment_id}: {payment_response}")
                return JsonResponse({
                    'success': False, 
                    'error': 'Error al consultar el pago con Mercado Pago'
                }, status=502)
            
            payment_data = payment_response.get("response", {})
            status = payment_data.get("status")
            
            # Extraer metadata (MP convierte keys a snake_case)
            metadata = payment_data.get("metadata", {})
            
            log_payment_event("PAYMENT_DATA_RETRIEVED", payment_id, {
                "status": status,
                "amount": payment_data.get("transaction_amount"),
                "metadata_keys": list(metadata.keys())
            })
            
        except Exception as e:
            logger.exception(f"[CRITICAL] Error recuperando pago {payment_id}")
            return JsonResponse({
                'success': False, 
                'error': 'Error de conexión con Mercado Pago'
            }, status=502)

        # Solo procesamos pagos APROBADOS
        if status == 'approved':
            # Verificar si ya procesamos este pago (evitar doble envío)
            if payment_id in _processed_payments:
                logger.info(f"[SKIP] Payment {payment_id} ya fue procesado")
                return JsonResponse({
                    'success': True,
                    'status': 'approved',
                    'payment_id': payment_id,
                    'email_sent': True,
                    'message': '¡Pago exitoso! El email ya fue enviado anteriormente.'
                })
            
            # Construir objeto order para el servicio de email
            customer_email = metadata.get("customer_email", "")
            
            # Validar que tenemos email del cliente
            if not customer_email:
                logger.error(f"[ERROR] No hay email en metadata para payment {payment_id}")
                return JsonResponse({
                    'success': True,
                    'status': 'approved',
                    'payment_id': payment_id,
                    'email_sent': False,
                    'email_error': 'No se encontró el email del cliente en la metadata',
                    'message': '¡Pago exitoso! Pero no pudimos enviar el email. Contactanos a datos.conalex@gmail.com'
                })
            
            fake_order = SimpleNamespace(
                id=payment_data.get("external_reference", payment_id),
                first_name=metadata.get("customer_first_name", "Cliente"),
                email=customer_email,
                course_title=metadata.get("course_title", "Producto Digital"),
                course_id=metadata.get("course_id", "tracker-habitos"),
                price=metadata.get("price", payment_data.get("transaction_amount", 0)),
                status=status
            )
            
            # Enviar email con producto
            email_sent = False
            email_error = None
            
            try:
                logger.info(f"[EMAIL] Enviando a {fake_order.email} - Producto: {fake_order.course_id}")
                email_sent = send_product_email(fake_order)
                
                if email_sent:
                    _processed_payments.add(payment_id)
                    log_payment_event("EMAIL_SENT_SUCCESS", payment_id, {
                        "to": fake_order.email,
                        "product": fake_order.course_id
                    })
                else:
                    log_payment_event("EMAIL_SENT_FAILED", payment_id, {
                        "to": fake_order.email
                    })
                    
            except Exception as email_ex:
                email_error = str(email_ex)
                logger.error(f"[CRITICAL] Email error for {payment_id}: {email_error}")
                log_payment_event("EMAIL_EXCEPTION", payment_id, {
                    "error": email_error
                })
            
            return JsonResponse({
                'success': True,
                'status': 'approved',
                'payment_id': payment_id,
                'email_sent': email_sent,
                'email_error': email_error,
                'customer_email': customer_email[:3] + "***",  # Mostrar parcialmente por privacidad
                'message': '¡Pago exitoso! Revisá tu email (y la carpeta de spam).' if email_sent 
                          else '¡Pago exitoso! Hubo un problema enviando el email, contactanos a datos.conalex@gmail.com'
            })
        
        elif status == 'pending':
            return JsonResponse({
                'success': False,
                'status': 'pending',
                'message': 'Tu pago está pendiente de acreditación. Te avisaremos cuando se confirme.'
            })
        
        elif status == 'in_process':
            return JsonResponse({
                'success': False,
                'status': 'in_process',
                'message': 'Tu pago está siendo procesado. Recibirás el producto una vez se confirme.'
            })
        
        else:
            return JsonResponse({
                'success': False, 
                'status': status,
                'message': f'El pago no fue aprobado. Estado: {status}'
            })

    except Exception as e:
        logger.exception("[CRITICAL] Error en pago_exitoso")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# DOWNLOAD FILE - Legacy endpoint
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def download_file(request, order_id):
    """
    Endpoint legacy - No funciona en arquitectura stateless.
    Los archivos se entregan por email.
    """
    return JsonResponse({
        'error': 'Este endpoint ya no está disponible. El archivo fue enviado a tu email.'
    }, status=410)


# =============================================================================
# WEBHOOK - Fuente de verdad y backup (Mercado Pago notifica aquí)
# =============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def webhook(request):
    """
    Webhook de Mercado Pago - FUENTE DE VERDAD para notificaciones.
    
    Este endpoint actúa como BACKUP cuando:
    1. El usuario cierra la ventana antes de pago_exitoso
    2. Hay un error en el frontend
    3. El pago se aprueba después (ej: transferencia bancaria)
    
    MP envía notificaciones cuando:
    - Se crea un pago
    - Se actualiza el estado de un pago
    - Se realiza una devolución
    
    IMPORTANTE: Siempre responder 200 OK para que MP no reintente.
    """
    # GET request = MP verificando que el webhook existe
    if request.method == 'GET':
        return JsonResponse({'status': 'webhook active', 'production': is_production_token()})
    
    try:
        # Parsear body del webhook
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}
        
        # Log del webhook recibido
        notification_type = body.get('type', 'unknown')
        action = body.get('action', 'unknown')
        
        log_payment_event("WEBHOOK_RECEIVED", "N/A", {
            "type": notification_type,
            "action": action,
            "body_keys": list(body.keys())
        })
        
        # Solo procesamos notificaciones de pago
        if notification_type != 'payment':
            logger.info(f"[WEBHOOK] Ignorando notificación tipo: {notification_type}")
            return JsonResponse({'status': 'ignored', 'reason': 'not a payment notification'})
        
        # Obtener el ID del pago
        data = body.get('data', {})
        payment_id = data.get('id') or body.get('data.id')
        
        if not payment_id:
            logger.warning("[WEBHOOK] No payment_id en la notificación")
            return JsonResponse({'status': 'ignored', 'reason': 'no payment_id'})
        
        payment_id = str(payment_id)
        
        # Verificar si ya procesamos este pago
        if payment_id in _processed_payments:
            logger.info(f"[WEBHOOK] Payment {payment_id} ya procesado, skipping")
            return JsonResponse({'status': 'already_processed'})
        
        log_payment_event("WEBHOOK_PROCESSING", payment_id, {"action": action})
        
        # Consultar detalles del pago a MP
        try:
            payment_response = sdk.payment().get(payment_id)
            
            if payment_response.get("status") != 200:
                logger.error(f"[WEBHOOK] Error obteniendo pago {payment_id}: {payment_response}")
                return JsonResponse({'status': 'error', 'reason': 'mp_api_error'}, status=200)
            
            payment_data = payment_response.get("response", {})
            status = payment_data.get("status")
            metadata = payment_data.get("metadata", {})
            
            log_payment_event("WEBHOOK_PAYMENT_STATUS", payment_id, {
                "status": status,
                "amount": payment_data.get("transaction_amount")
            })
            
        except Exception as e:
            logger.exception(f"[WEBHOOK] Error consultando MP para {payment_id}")
            return JsonResponse({'status': 'error', 'reason': str(e)}, status=200)
        
        # Solo procesamos pagos aprobados
        if status != 'approved':
            logger.info(f"[WEBHOOK] Payment {payment_id} status={status}, no action needed")
            return JsonResponse({'status': 'noted', 'payment_status': status})
        
        # Obtener email del cliente
        customer_email = metadata.get("customer_email", "")
        
        if not customer_email:
            logger.error(f"[WEBHOOK] No email en metadata para {payment_id}")
            return JsonResponse({
                'status': 'error', 
                'reason': 'no_customer_email',
                'action': 'manual_intervention_required'
            }, status=200)
        
        # Construir orden para envío de email
        fake_order = SimpleNamespace(
            id=payment_data.get("external_reference", payment_id),
            first_name=metadata.get("customer_first_name", "Cliente"),
            email=customer_email,
            course_title=metadata.get("course_title", "Producto Digital"),
            course_id=metadata.get("course_id", "tracker-habitos"),
            price=metadata.get("price", payment_data.get("transaction_amount", 0)),
            status=status
        )
        
        # Enviar email
        try:
            logger.info(f"[WEBHOOK] Enviando email a {customer_email} para payment {payment_id}")
            email_sent = send_product_email(fake_order)
            
            if email_sent:
                _processed_payments.add(payment_id)
                log_payment_event("WEBHOOK_EMAIL_SUCCESS", payment_id, {
                    "to": customer_email,
                    "product": fake_order.course_id
                })
                return JsonResponse({'status': 'processed', 'email_sent': True})
            else:
                log_payment_event("WEBHOOK_EMAIL_FAILED", payment_id, {
                    "to": customer_email
                })
                return JsonResponse({'status': 'processed', 'email_sent': False})
                
        except Exception as e:
            logger.exception(f"[WEBHOOK] Error enviando email para {payment_id}")
            log_payment_event("WEBHOOK_EMAIL_EXCEPTION", payment_id, {
                "error": str(e)
            })
            return JsonResponse({
                'status': 'error', 
                'reason': 'email_failed',
                'error': str(e)
            }, status=200)
        
    except Exception as e:
        logger.exception("[CRITICAL] Error general en webhook")
        # SIEMPRE responder 200 para que MP no reintente
        return JsonResponse({'status': 'error', 'reason': str(e)}, status=200)
