"""
URLs para el módulo de pagos con Mercado Pago
==============================================
Datos con Alex - Sistema de Pagos
"""

from django.urls import path
from . import views
from . import views_debug

app_name = 'payments'

urlpatterns = [
    # ==========================================================================
    # ENDPOINTS PRINCIPALES
    # ==========================================================================
    
    # POST /api/payments/create-preference/
    # Crea una preferencia de pago y retorna el init_point
    path('create-preference/', views.create_preference, name='create_preference'),
    
    # GET /api/payments/validate/?payment_id=xxx
    # Valida un pago exitoso usando los parámetros de MP
    path('validate/', views.pago_exitoso, name='pago_exitoso'),
    
    # POST /api/payments/webhook/
    # Recibe notificaciones de Mercado Pago (backup)
    path('webhook/', views.webhook, name='webhook'),
    
    # GET /api/payments/download/<order_id>/
    # Legacy - ya no funciona (archivos van por email)
    path('download/<int:order_id>/', views.download_file, name='download_file'),
    
    # ==========================================================================
    # ENDPOINTS DE DIAGNÓSTICO
    # ==========================================================================
    
    # GET /api/payments/health/
    # Verificación básica de que el backend corre
    path('health/', views_debug.health_check, name='health_check'),
    
    # GET /api/payments/env-check/
    # Verificación de variables de entorno
    path('env-check/', views_debug.env_check, name='env_check'),
    
    # GET /api/payments/products-check/
    # Verificación de productos y archivos
    path('products-check/', views_debug.products_check, name='products_check'),
    
    # GET /api/payments/test-email/?to=email@example.com
    # Enviar email de prueba
    path('test-email/', views_debug.test_email, name='test_email'),
    
    # GET /api/payments/system-status/
    # Estado completo del sistema
    path('system-status/', views_debug.system_status, name='system_status'),
]

