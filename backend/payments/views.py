"""
Vistas para integración con Mercado Pago - Flujo de Redirect (Checkout Pro)

Este módulo maneja:
1. Creación de preferencias de pago (create_preference)
2. Validación de pagos exitosos (pago_exitoso)
3. Webhook para notificaciones de Mercado Pago (webhook)
"""

import json
import os
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import mercadopago
from dotenv import load_dotenv

# Cargar variables de entorno desde el directorio backend
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / '.env')

# Inicializar SDK de Mercado Pago
sdk = mercadopago.SDK(os.getenv('MP_ACCESS_TOKEN'))

# URL del frontend para redirecciones
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')


@csrf_exempt
@require_http_methods(["POST"])
def create_preference(request):
    """
    Crea una preferencia de pago en Mercado Pago y retorna el init_point (URL de redirect).
    
    Request Body:
    {
        "course_id": "excel-principiantes",
        "title": "Excel para Principiantes",
        "price": 24.50,
        "quantity": 1,
        "buyer_email": "usuario@email.com"  # Opcional
    }
    
    Response:
    {
        "success": true,
        "init_point": "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=...",
        "preference_id": "123456789-xxxxxxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
    """
    try:
        # Parsear el body de la request
        data = json.loads(request.body)
        
        course_id = data.get('course_id', 'curso-default')
        title = data.get('title', 'Curso AIExcel')
        price = float(data.get('price', 0))
        quantity = int(data.get('quantity', 1))
        buyer_email = data.get('buyer_email')
        
        # Validar precio
        if price <= 0:
            return JsonResponse({
                'success': False,
                'error': 'El precio debe ser mayor a 0'
            }, status=400)
        
        # Construir el objeto de preferencia
        preference_data = {
            "items": [
                {
                    "id": course_id,
                    "title": title,
                    "currency_id": "ARS",  # Pesos Argentinos
                    "unit_price": price,
                    "quantity": quantity,
                    "description": f"Acceso completo al curso: {title}",
                    "category_id": "learnings",  # Categoría de cursos/educación
                }
            ],
            # URLs de retorno
            "back_urls": {
                "success": f"{FRONTEND_URL}/?payment=success",
                "failure": f"{FRONTEND_URL}/?payment=failure",
                "pending": f"{FRONTEND_URL}/?payment=pending",
            },
            # Redirigir automáticamente después del pago
            "auto_return": "approved",
            # ID externo para vincular con tu sistema
            "external_reference": f"alexcel_{course_id}_{int(price*100)}",
            # Configuración adicional
            "statement_descriptor": "ALEXCEL",  # Nombre que aparece en el resumen del comprador
            "expires": False,  # La preferencia no expira
            # Excluir métodos de pago que no queremos (opcional)
            # "payment_methods": {
            #     "excluded_payment_types": [
            #         {"id": "ticket"}  # Excluir pagos en efectivo
            #     ]
            # }
        }
        
        # Agregar email del comprador si está disponible
        if buyer_email:
            preference_data["payer"] = {
                "email": buyer_email
            }
        
        # URL de notificación webhook (opcional pero recomendado)
        # preference_data["notification_url"] = f"{os.getenv('BACKEND_URL')}/api/payments/webhook/"
        
        # Crear la preferencia en Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})
        
        if "id" not in preference:
            return JsonResponse({
                'success': False,
                'error': 'Error al crear la preferencia de pago',
                'details': preference_response
            }, status=500)
        
        # Retornar el init_point para redirect
        return JsonResponse({
            'success': True,
            'init_point': preference.get('init_point'),  # URL para producción
            'sandbox_init_point': preference.get('sandbox_init_point'),  # URL para testing
            'preference_id': preference.get('id')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en el body de la request'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pago_exitoso(request):
    """
    Valida un pago exitoso usando el payment_id recibido de Mercado Pago.
    
    Query Parameters (enviados por MP al redirigir):
    - collection_id / payment_id: ID del pago
    - collection_status / status: Estado del pago
    - external_reference: Referencia externa que enviamos
    - preference_id: ID de la preferencia
    
    Response:
    {
        "success": true,
        "payment_id": "123456789",
        "status": "approved",
        "status_detail": "accredited",
        "course_id": "excel-principiantes",
        "amount": 24.50
    }
    """
    try:
        # Obtener parámetros de la URL (Mercado Pago los envía como query params)
        payment_id = request.GET.get('payment_id') or request.GET.get('collection_id')
        status = request.GET.get('status') or request.GET.get('collection_status')
        external_reference = request.GET.get('external_reference')
        preference_id = request.GET.get('preference_id')
        
        if not payment_id:
            return JsonResponse({
                'success': False,
                'error': 'No se recibió el ID del pago'
            }, status=400)
        
        # Consultar el pago en Mercado Pago para validar
        payment_response = sdk.payment().get(payment_id)
        payment_info = payment_response.get("response", {})
        
        if not payment_info:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró información del pago'
            }, status=404)
        
        # Extraer información del pago
        payment_status = payment_info.get('status')
        payment_status_detail = payment_info.get('status_detail')
        transaction_amount = payment_info.get('transaction_amount')
        
        # Verificar que el pago fue aprobado
        if payment_status != 'approved':
            return JsonResponse({
                'success': False,
                'error': f'El pago no fue aprobado. Estado: {payment_status}',
                'status': payment_status,
                'status_detail': payment_status_detail
            }, status=400)
        
        # Parsear el external_reference para obtener el course_id
        course_id = None
        if external_reference and external_reference.startswith('alexcel_'):
            parts = external_reference.split('_')
            if len(parts) >= 2:
                course_id = parts[1]
        
        # TODO: Aquí deberías:
        # 1. Registrar la compra en tu base de datos
        # 2. Dar acceso al usuario al curso
        # 3. Enviar email de confirmación
        
        return JsonResponse({
            'success': True,
            'payment_id': payment_id,
            'status': payment_status,
            'status_detail': payment_status_detail,
            'amount': transaction_amount,
            'course_id': course_id,
            'external_reference': external_reference,
            'message': '¡Pago procesado exitosamente!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """
    Webhook para recibir notificaciones de Mercado Pago.
    
    Mercado Pago envía notificaciones cuando:
    - Se crea un pago
    - Se aprueba un pago
    - Se rechaza un pago
    - Se cancela un pago
    
    Es importante implementar esto para casos donde el usuario cierra el browser
    antes de ser redirigido de vuelta.
    """
    try:
        # Obtener el tipo de notificación
        topic = request.GET.get('topic') or request.GET.get('type')
        resource_id = request.GET.get('id') or request.GET.get('data.id')
        
        # Parsear body si existe
        body = {}
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                pass
        
        # Si es una notificación de pago
        if topic == 'payment' or body.get('type') == 'payment':
            payment_id = resource_id or body.get('data', {}).get('id')
            
            if payment_id:
                # Consultar el pago
                payment_response = sdk.payment().get(payment_id)
                payment_info = payment_response.get("response", {})
                
                if payment_info.get('status') == 'approved':
                    # TODO: Procesar el pago aprobado
                    # - Registrar en base de datos
                    # - Dar acceso al curso
                    # - Enviar emails
                    print(f"[WEBHOOK] Pago aprobado: {payment_id}")
                    print(f"[WEBHOOK] Monto: {payment_info.get('transaction_amount')}")
                    print(f"[WEBHOOK] Referencia: {payment_info.get('external_reference')}")
        
        # Siempre responder 200 OK para que MP sepa que recibimos la notificación
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        # Aunque haya error, respondemos 200 para evitar reintentos infinitos
        print(f"[WEBHOOK ERROR] {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})
