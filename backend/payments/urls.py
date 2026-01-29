"""
URLs para el módulo de pagos con Mercado Pago
"""

from django.urls import path
from . import views
from . import views_debug

app_name = 'payments'

urlpatterns = [
    # POST /api/payments/create-preference/
    # Crea una preferencia de pago y retorna el init_point
    path('create-preference/', views.create_preference, name='create_preference'),
    
    # GET /api/payments/validate/
    # Valida un pago exitoso usando los parámetros de MP
    path('validate/', views.pago_exitoso, name='pago_exitoso'),
    
    # GET /api/payments/download/<order_id>/
    # Descarga el archivo del curso (solo si pago aprobado)
    path('download/<int:order_id>/', views.download_file, name='download_file'),
    
    # POST /api/payments/webhook/
    # Recibe notificaciones de Mercado Pago
    path('webhook/', views.webhook, name='webhook'),
    path('health/', views_debug.health_check),
    path('env-check/', views_debug.env_check),
]
