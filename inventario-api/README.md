# 🏪 API de Inventario para PYME

Sistema de control de inventario diseñado para pequeñas empresas chilenas.

## 📋 Características

- ✅ **Gestión de Productos**: CRUD completo
- 💰 **Registro de Ventas**: Descuento automático de stock
- ⚠️ **Alertas por Email**: Notificaciones cuando el stock está bajo
- 🔐 **Autenticación Segura**: JWT + API Keys
- 👥 **Multi-usuario**: Cada usuario gestiona su propio inventario
- 📊 **Estadísticas**: Resumen de ventas y productos más vendidos
- 📥 **Importación Masiva**: Desde Excel y Google Sheets
- 💵 **100% GRATIS**: Deploy gratuito permanente

---

## 🚀 Deploy Rápido (100% GRATIS)

**Sigue la guía completa:** [DEPLOY_GRATIS.md](DEPLOY_GRATIS.md)

**Stack gratuito:**
- ✅ Railway (hosting) - 500 horas/mes gratis
- ✅ Supabase (base de datos) - Gratis permanente
- ✅ Resend (emails) - 3,000/mes gratis

**Tiempo total:** 20-30 minutos

---

## 💻 Desarrollo Local

### Requisitos

- Python 3.11+
- PostgreSQL (usaremos Supabase gratis)
- Cuenta de Resend (emails gratis)

### 1. Clonar Proyecto

```bash
cd inventario-api
```

### 2. Crear Entorno Virtual

```bash
# Crear
python -m venv venv

# Activar
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# Supabase (gratis)
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres

# Seguridad (genera con: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=tu_clave_secreta

# Resend (gratis - 3,000 emails/mes)
RESEND_API_KEY=re_xxxxxxxxxxxxx
RESEND_FROM_EMAIL=onboarding@resend.dev
```

### 5. Correr Localmente

```bash
python start_server.py
```

API disponible en: http://localhost:8000
Documentación: http://localhost:8000/docs

---

## 📖 Uso de la API

### 1. Registrar Usuario

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.cl",
    "password": "mipassword123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@ejemplo.cl",
    "password": "mipassword123"
  }'
```

Guarda el `access_token`.

### 3. Crear Producto

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{
    "nombre": "Coca Cola 1.5L",
    "sku": "BEB-001",
    "stock_actual": 50,
    "stock_minimo": 10
  }'
```

### 4. Registrar Venta

```bash
curl -X POST http://localhost:8000/sales \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{
    "producto_id": 1,
    "cantidad": 5
  }'
```

### 5. Importar desde Excel

```bash
# Descargar plantilla
curl -X GET http://localhost:8000/import/excel/template \
  --output plantilla.xlsx

# Importar
curl -X POST http://localhost:8000/import/excel \
  -H "Authorization: Bearer TU_TOKEN" \
  -F "archivo=@plantilla.xlsx"
```

---

## 🔐 Autenticación

### Opción 1: JWT Token (Recomendado)

1. Login → Obtén `access_token`
2. Envía en cada request:
   ```
   Authorization: Bearer eyJhbGc...
   ```
3. Expira en 30 días

### Opción 2: API Key

1. Obtén tu API Key al registrarte
2. Envía en cada request:
   ```
   Authorization: Bearer sk_abc123...
   ```
3. No expira nunca

---

## 📧 Configurar Resend (Emails Gratis)

### Paso 1: Crear Cuenta

1. Ve a https://resend.com
2. Sign up gratis
3. Verifica tu email

### Paso 2: API Key

1. Ve a **API Keys**
2. Click **"Create API Key"**
3. Copia la key: `re_xxxxx`

### Paso 3: Configurar Email

**Para pruebas:**
```env
RESEND_FROM_EMAIL=onboarding@resend.dev
```

**Para producción:**
1. Verifica tu dominio en Resend
2. Usa: `alertas@tudominio.com`

---

## 🗄️ Configurar Supabase (BD Gratis)

### Paso 1: Crear Proyecto

1. Ve a https://supabase.com
2. Click "New Project"
3. Elige región: South America
4. Crea password segura

### Paso 2: Obtener URL

1. Settings → Database
2. Copia "Connection string (URI)"
3. Reemplaza `[YOUR-PASSWORD]`

---

## 📁 Estructura del Proyecto

```
inventario-api/
├── app/
│   ├── main.py              # App principal
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión BD
│   ├── auth.py              # Autenticación
│   │
│   ├── models/              # Modelos BD
│   ├── schemas/             # Validación
│   ├── routes/              # Endpoints
│   └── services/            # Lógica de negocio
│
├── requirements.txt         # Dependencias
├── Procfile                 # Railway
├── runtime.txt              # Python version
├── .env.example             # Ejemplo config
│
├── README.md                # Este archivo
├── DEPLOY_GRATIS.md         # Guía deploy
├── ARQUITECTURA.md          # Explicación técnica
└── PITCH_VENTAS.md          # Material de ventas
```

---

## 🎯 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/register` | Registrar usuario |
| POST | `/auth/login` | Iniciar sesión |
| GET | `/auth/me` | Ver perfil |
| POST | `/products` | Crear producto |
| GET | `/products` | Listar productos |
| PUT | `/products/{id}/stock` | Actualizar stock |
| POST | `/sales` | Registrar venta |
| GET | `/sales` | Listar ventas |
| POST | `/import/excel` | Importar Excel |
| GET | `/import/excel/template` | Descargar plantilla |

**Documentación interactiva:** `/docs`

---

## 🧪 Probar la API

```bash
python test_api.py
```

Esto ejecuta pruebas completas de todos los endpoints.

---

## 💰 Costos

### Plan Gratis (Recomendado)

| Servicio | Límite | Costo |
|----------|--------|-------|
| Railway | 500 hrs/mes | $0 |
| Supabase | 500MB + 2GB transfer | $0 |
| Resend | 3,000 emails/mes | $0 |
| **TOTAL** | | **$0/mes** |

**Suficiente para:**
- 10-50 clientes activos
- ~100 emails/día
- ~100,000 productos

---

## 📚 Documentación Adicional

- [DEPLOY_GRATIS.md](DEPLOY_GRATIS.md) - Deploy paso a paso
- [ARQUITECTURA.md](ARQUITECTURA.md) - Explicación técnica
- [PITCH_VENTAS.md](PITCH_VENTAS.md) - Cómo vender esto
- [INTEGRACIONES_MARKETPLACES.md](INTEGRACIONES_MARKETPLACES.md) - ML, Instagram, etc
- [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) - Importar desde Sheets

---

## ❓ Problemas Comunes

### "Module not found"

```bash
pip install -r requirements.txt
```

### "Database connection failed"

Verifica que `DATABASE_URL` sea correcta en `.env`

### "Email not sent"

Verifica `RESEND_API_KEY` y usa `onboarding@resend.dev` para pruebas

---

## 🚀 Deploy Producción

**Sigue la guía completa:** [DEPLOY_GRATIS.md](DEPLOY_GRATIS.md)

**Resumen:**
1. Crear BD en Supabase (2 min)
2. Crear cuenta Resend (2 min)
3. Subir código a GitHub (5 min)
4. Deploy en Railway (10 min)
5. ✅ API online gratis

---

## 📄 Licencia

MIT License - Uso libre

---

**¿Preguntas? Abre un issue en GitHub o contacta al desarrollador.**

**¡Éxito con tu inventario! 🎉**
