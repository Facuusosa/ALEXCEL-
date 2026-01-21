"""
URL configuration for ALEXCEL backend
"""

from django.urls import path, include

urlpatterns = [
    path('api/payments/', include('payments.urls')),
]
