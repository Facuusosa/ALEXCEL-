# 🛒 Integración Mercado Pago - ALEXCEL

Este documento explica cómo configurar y ejecutar la integración de pagos con Mercado Pago.

---

## 📁 Estructura del Proyecto

```
ALEXCEL/
├── backend/                    # Backend Django
│   ├── config/                 # Configuración Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── payments/               # App de pagos
│   │   ├── views.py           # Endpoints de MP
│   │   └── urls.py
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── pages/
│   └── CheckoutPage.tsx        # Checkout refactorizado
├── .env.example                # Variables frontend
└── vite-env.d.ts               # Tipos TypeScript
```

---

## 🚀 Configuración Paso a Paso

### 1. Obtener Credenciales de Mercado Pago

1. Ir a [Mercado Pago Developers](https://www.mercadopago.com.ar/developers/panel/app)
2. Crear una aplicación (si no tenés una)
3. Ir a **Credenciales** → **Credenciales de prueba**
4. Copiar el **Access Token** de prueba (empieza con `TEST-`)

### 2. Configurar el Backend Django

```bash
# Navegar al backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (copiar del ejemplo)
cp .env.example .env
```

**Editar `backend/.env`:**
```env
MP_ACCESS_TOKEN=TEST-tu-access-token-aqui
DJANGO_SECRET_KEY=genera-una-clave-segura
FRONTEND_URL=http://localhost:5173
DEBUG=True
```

**Iniciar el servidor Django:**
```bash
python manage.py runserver 8000
```

El backend estará en: `http://localhost:8000`

### 3. Configurar el Frontend

```bash
# En la raíz del proyecto
cp .env.example .env
```

**Editar `.env`:**
```env
VITE_API_URL=http://localhost:8000
```

**Iniciar el servidor Vite:**
```bash
npm run dev
```

El frontend estará en: `http://localhost:5173`

---

## 🔌 Endpoints de la API

### `POST /api/payments/create-preference/`

Crea una preferencia de pago y retorna la URL de redirect.

**Request:**
```json
{
  "course_id": "excel-principiantes",
  "title": "Excel para Principiantes",
  "price": 24.50,
  "quantity": 1,
  "buyer_email": "usuario@email.com"
}
```

**Response:**
```json
{
  "success": true,
  "init_point": "https://www.mercadopago.com.ar/checkout/...",
  "sandbox_init_point": "https://sandbox.mercadopago.com.ar/checkout/...",
  "preference_id": "123456789-xxxxx"
}
```

### `GET /api/payments/validate/`

Valida un pago usando el ID recibido de Mercado Pago.

**Query Parameters:**
- `payment_id`: ID del pago

**Response:**
```json
{
  "success": true,
  "status": "approved",
  "amount": 24.50,
  "course_id": "excel-principiantes"
}
```

### `POST /api/payments/webhook/`

Recibe notificaciones automáticas de Mercado Pago.

---

## 🧪 Probar Pagos

### Tarjetas de Prueba

Mercado Pago provee tarjetas de prueba para testing:

| Tarjeta | Número | CVV | Vencimiento |
|---------|--------|-----|-------------|
| Mastercard | 5031 7557 3453 0604 | 123 | 11/25 |
| Visa | 4509 9535 6623 3704 | 123 | 11/25 |
| Amex | 3711 803032 57522 | 1234 | 11/25 |

### Documento de Prueba
- **DNI:** 12345678

### Usuarios de Prueba
Podés crear usuarios de prueba desde el panel de desarrolladores para simular compradores y vendedores.

---

## 📝 Flujo Completo

```
1. Usuario hace clic en "Pagar con Mercado Pago"
       ↓
2. Frontend envía POST a /api/payments/create-preference/
       ↓
3. Backend crea preferencia en MP y retorna init_point
       ↓
4. Frontend redirige al usuario a Mercado Pago
       ↓
5. Usuario completa el pago en MP
       ↓
6. MP redirige al usuario a /?payment=success&payment_id=XXX
       ↓
7. Frontend detecta parámetros y valida con /api/payments/validate/
       ↓
8. Backend consulta el pago en MP y confirma
       ↓
9. Usuario ve mensaje de éxito y es redirigido al dashboard
```

---

## 🔒 Seguridad en Producción

1. **Usar HTTPS** en el backend
2. **Cambiar a credenciales de producción** (no `TEST-`)
3. **Validar webhook** con firma de Mercado Pago
4. **Almacenar pagos en base de datos**
5. **Implementar idempotencia** para evitar duplicados

---

## 🐛 Troubleshooting

### Error: "CORS blocked"
- Verificar que `CORS_ALLOWED_ORIGINS` en `settings.py` incluya tu URL de frontend

### Error: "Error de conexión"
- Verificar que el backend esté corriendo en el puerto 8000
- Verificar que `VITE_API_URL` apunte al backend correcto

### Error: "Error al crear preferencia"
- Verificar que el `MP_ACCESS_TOKEN` sea válido
- Verificar que el token sea de **prueba** si estás probando

---

## 📚 Referencias

- [Documentación oficial Mercado Pago](https://www.mercadopago.com.ar/developers/es/docs)
- [SDK Python MP](https://github.com/mercadopago/sdk-python)
- [Checkout Pro](https://www.mercadopago.com.ar/developers/es/docs/checkout-pro/landing)
