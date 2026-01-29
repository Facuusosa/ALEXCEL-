
from django.http import JsonResponse
import os

def health_check(request):
    return JsonResponse({"status": "ok", "message": "Backend is running!"})

def env_check(request):
    token = os.getenv('MP_ACCESS_TOKEN')
    frontend = os.getenv('FRONTEND_URL')
    return JsonResponse({
        "has_mp_token": bool(token),
        "frontend_url_set": bool(frontend),
        "frontend_url_value": frontend if frontend else "Not Set", # Seguro mostrar URL pública
        "token_prefix": token[:10] if token else "None"
    })
