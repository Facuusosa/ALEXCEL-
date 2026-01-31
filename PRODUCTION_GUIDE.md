# 🚀 Guía de Producción - Datos con Alex

## Estado Actual del Sistema

✅ **Backend (Django en Railway)**
- Endpoint de preferencias de pago funcionando
- Webhook refactorizado como fuente de verdad
- Servicio de email con Resend SDK
- Logging estructurado para diagnóstico

✅ **Frontend (React/Vite en Vercel)**
- Checkout integrado con Mercado Pago
- Páginas de resultado de pago (éxito, fallo, pendiente)
- URLs dinámicas según entorno

---

## 📋 Checklist Pre-Producción

### 1. Credenciales de Mercado Pago

- [ ] Ir a [Panel de Desarrolladores MP](https://www.mercadopago.com.ar/developers/panel/app)
- [ ] Seleccionar tu aplicación
- [ ] **Credenciales > Producción**
- [ ] Copiar el **Access Token** (empieza con `APP_USR-`)
- [ ] ⚠️ NUNCA usar token que empiece con `TEST-` para producción

### 2. Variables de Entorno en Railway

Ir a: **Railway Dashboard > Tu Proyecto > Variables**

| Variable | Valor de Ejemplo | Descripción |
|----------|-----------------|-------------|
| `MP_ACCESS_TOKEN` | `APP_USR-8416...` | Token de producción de MP |
| `DJANGO_SECRET_KEY` | `cambiar-por-key-segura` | Key única para Django |
| `ALLOWED_HOSTS` | `alexcel-backend-production.up.railway.app` | Tu dominio de Railway |
| `DEBUG` | `False` | ⚠️ SIEMPRE False en producción |
| `FRONTEND_URL` | `https://datosconalex.vercel.app` | URL de tu frontend |
| `RESEND_API_KEY` | `re_e2mS7DQE_...` | API Key de Resend |
| `EMAIL_FROM_NAME` | `Datos con Alex` | Nombre del remitente |
| `EMAIL_FROM_ADDRESS` | `onboarding@resend.dev` | Email del remitente |
| `EMAIL_REPLY_TO` | `datos.conalex@gmail.com` | Email para respuestas |

### 3. Variables de Entorno en Vercel

Ir a: **Vercel Dashboard > Tu Proyecto > Settings > Environment Variables**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `VITE_API_URL` | `https://alexcel-backend-production.up.railway.app` | URL del backend |

### 4. Configurar Webhook en Mercado Pago

1. Ir a [Webhooks MP](https://www.mercadopago.com.ar/developers/panel/webhooks)
2. Crear nuevo webhook
3. URL: `https://alexcel-backend-production.up.railway.app/api/payments/webhook/`
4. Eventos: Marcar **Pagos**
5. Guardar

### 5. Verificar Archivos de Producto

En Railway, verificar que existan en `backend/files/`:
- [ ] `tracker-habitos.xlsx`
- [ ] `planificador-financiero.xlsx`

⚠️ Si faltan archivos, el email se enviará pero sin adjunto.

---

## 🧪 Prueba de Integración Completa

### Paso 1: Verificar Backend
```bash
curl https://alexcel-backend-production.up.railway.app/api/payments/health/
# Esperado: {"status": "ok", ...}
```

### Paso 2: Verificar Email (endpoint de debug)
```bash
curl https://alexcel-backend-production.up.railway.app/api/payments/env-check/
# Verifica que RESEND_API_KEY esté configurada
```

### Paso 3: Compra de Prueba Real

1. Ir a tu frontend en Vercel
2. Seleccionar un producto (ej: Tracker de Hábitos por $1)
3. Completar formulario con:
   - Nombre: Tu nombre
   - Email: **TU EMAIL REAL** (para recibir el producto)
   - DNI: Cualquier número válido
4. Pagar con Mercado Pago (tarjeta real o dinero en cuenta)
5. Esperar redirección a `/pago-exitoso`
6. Verificar email (revisar spam también)

### Paso 4: Revisar Logs en Railway

1. Railway Dashboard > Tu Proyecto > **View Logs**
2. Buscar eventos como:
   ```
   [PAYMENT_EVENT] {"event": "PREFERENCE_CREATED", ...}
   [PAYMENT_EVENT] {"event": "EMAIL_SENT_SUCCESS", ...}
   ```

---

## 🔧 Troubleshooting

### El email no llega

1. **Verificar RESEND_API_KEY**: ¿Está configurada en Railway?
2. **Verificar logs**: Buscar `[EMAIL]` en los logs de Railway
3. **Verificar archivos**: ¿Existen los `.xlsx` en `backend/files/`?
4. **Revisar spam**: Resend a veces cae en spam inicialmente
5. **Dominio verificado**: Sin dominio verificado, solo puedes enviar a emails de tu cuenta Resend

### El pago no redirige bien

1. **Verificar FRONTEND_URL**: ¿Está bien configurada en Railway?
2. **Verificar logs**: Buscar la respuesta de `create_preference`
3. **Probar con `sandbox_init_point`**: En desarrollo usa el sandbox

### Error de CORS

1. Verificar que `ALLOWED_HOSTS` incluya tu dominio de Railway
2. El middleware CORS está configurado para aceptar todos los orígenes

### Error 502 al validar pago

1. **Verificar MP_ACCESS_TOKEN**: ¿Es el token correcto?
2. **Verificar logs**: El error específico debería aparecer

---

## 📊 Flujo de Datos

```
Usuario → Checkout → Backend (create_preference)
                           ↓
                    Mercado Pago ← Preferencia creada
                           ↓
              Usuario paga en MP ← Redirección
                           ↓
         ┌─────────────────┴─────────────────┐
         ↓                                   ↓
   /pago-exitoso                         Webhook MP
   (método primario)                  (backup async)
         ↓                                   ↓
   validate endpoint                   Validar pago
         ↓                                   ↓
   Enviar email ←────────────────────→ Enviar email
         ↓                               (si no enviado)
   Resend API
         ↓
   Cliente recibe Excel 📧
```

---

## 💰 Costos de Producción

| Servicio | Plan | Costo |
|----------|------|-------|
| Railway | Starter | ~$5/mes (según uso) |
| Vercel | Hobby | Gratis |
| Resend | Free | 100 emails/día gratis |
| Mercado Pago | N/A | Comisión por venta (~5%) |

---

## 📞 Soporte

- **Mercado Pago**: [Documentación](https://www.mercadopago.com.ar/developers/es/docs)
- **Resend**: [Docs](https://resend.com/docs)
- **Railway**: [Docs](https://docs.railway.app/)

---

*Última actualización: Enero 2026*
