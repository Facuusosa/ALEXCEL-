# 🔴 REPORTE DE INCIDENTE: Gmail SMTP Rechaza Credenciales

**Fecha:** 2 de Febrero, 2026 - 22:03  
**Estado:** ❌ SIN RESOLVER - Requiere análisis  
**Prioridad:** CRÍTICA

---

## 1. RESUMEN DEL PROBLEMA

Gmail SMTP está rechazando **todas** las App Passwords generadas para la cuenta `facuu2009@gmail.com`, a pesar de que la verificación en 2 pasos está activa y las contraseñas se generan correctamente.

### Error exacto:
```
smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted. 
For more information, go to https://support.google.com/mail/?p=BadCredentials')
```

---

## 2. CONTEXTO TÉCNICO

### Objetivo
Configurar envío de emails vía Gmail SMTP para entregar productos digitales después de pagos con Mercado Pago.

### Configuración actual
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'facuu2009@gmail.com'
EMAIL_HOST_PASSWORD = '<app_password>'  # Múltiples intentos
```

### Código de prueba utilizado
```python
import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('facuu2009@gmail.com', '<app_password>')
print('Login exitoso')
server.quit()
```

---

## 3. APP PASSWORDS PROBADAS

Todas fueron generadas desde https://myaccount.google.com/apppasswords

| Intento | App Password (sin espacios) | Resultado |
|---------|----------------------------|-----------|
| 1 | `elidcglgawjcnoij` | ❌ 535 BadCredentials |
| 2 | `kfbnintvtznkxzbh` | ❌ 535 BadCredentials |
| 3 | `nfukpyvyydurnoxa` | ❌ 535 BadCredentials |
| 4 | `btafmwrulnuayceu` | ❌ 535 BadCredentials |

---

## 4. VERIFICACIONES REALIZADAS

### ✅ Confirmado correcto:
- Verificación en 2 pasos: **ACTIVA** (desde 21 de enero)
- Cuenta: `facuu2009@gmail.com` (cuenta personal, no Workspace)
- App Passwords se crean exitosamente en el panel de Google
- Las passwords se generan desde la cuenta correcta (probado en ventana incógnito)
- Puerto y servidor: `smtp.gmail.com:587` con TLS

### ❌ Falla persistente:
- Todas las App Passwords son rechazadas inmediatamente
- Error consistente: `535 5.7.8 BadCredentials`
- No hay variación en el error sin importar qué password se use

---

## 5. HIPÓTESIS

1. **Bloqueo de seguridad en la cuenta**: Google puede tener un bloqueo temporal por múltiples intentos fallidos o actividad sospechosa.

2. **Configuración de cuenta avanzada**: Puede haber alguna configuración de seguridad adicional que bloquea SMTP.

3. **Restricción geográfica o de IP**: El servidor/máquina local puede estar bloqueado.

4. **Problema con la cuenta específica**: Algo único de esta cuenta impide el uso de SMTP.

---

## 6. PASOS SUGERIDOS PARA GEMINI

### Opción A: Investigar la cuenta de Gmail
1. Revisar "Actividad de seguridad reciente" en la cuenta
2. Verificar si hay alertas de seguridad pendientes
3. Revisar configuración de "Acceso de aplicaciones menos seguras" (aunque debería no aplicar con App Passwords)
4. Verificar si la cuenta tiene restricciones de administrador

### Opción B: Alternativas a Gmail SMTP
1. **Brevo (ex-Sendinblue)**: Gratis hasta 300 emails/día, no requiere verificación de dominio
2. **SendGrid**: Gratis hasta 100 emails/día
3. **Mailgun**: Gratis para desarrollo
4. **Amazon SES**: Muy barato en producción

### Opción C: Volver a Resend con dominio verificado
Si el usuario tiene acceso a configurar DNS para `datosconalex.com`, puede completar la verificación de dominio en Resend.

---

## 7. ESTADO DEL CÓDIGO

El código está **completamente preparado** para usar Gmail SMTP:

- ✅ `backend/payments/services.py` - Usa `django.core.mail.EmailMessage`
- ✅ `backend/config/settings.py` - Configuración SMTP lista
- ✅ `backend/payments/views.py` - Dispara email al aprobar pago
- ✅ `.env` - Variables de entorno configuradas

**Solo falta resolver el problema de autenticación con Gmail.**

---

## 8. ARCHIVOS RELEVANTES

```
backend/
├── .env                          # Credenciales (con App Password actual)
├── config/settings.py            # Configuración Django + Email
├── payments/
│   ├── services.py               # send_product_email() - listo para Gmail
│   ├── views.py                  # Webhook + pago_exitoso
│   └── views_debug.py            # Endpoints de diagnóstico
└── files/
    ├── tracker-habitos.xlsx      # ✅ Existe
    └── planificador-financiero.xlsx  # ✅ Existe
```

---

## 9. PREGUNTA PARA GEMINI

¿Por qué Gmail SMTP rechaza App Passwords válidas generadas correctamente desde una cuenta con verificación en 2 pasos activa? ¿Qué configuración adicional de la cuenta de Google podría estar causando esto?

---

**Generado por:** Antigravity AI  
**Para análisis de:** Gemini
