# 🚀 Guía de Deploy 100% GRATIS

## Stack Completamente Gratuito

| Servicio | Propósito | Plan Gratis | Suficiente para |
|----------|-----------|-------------|-----------------|
| **Railway.app** | Hosting API | 500 horas/mes | ~20 días online 24/7 |
| **Supabase** | Base de datos | Gratis permanente | 500MB + 2GB transferencia |
| **Resend** | Emails | 3,000/mes | ~100 emails/día |
| **GitHub** | Repositorio | Ilimitado | Código fuente |

**Total costo:** $0/mes

---

## 📋 Prerrequisitos

- [ ] Cuenta de GitHub (gratis)
- [ ] Cuenta de Railway (gratis, sin tarjeta)
- [ ] Cuenta de Supabase (gratis)
- [ ] Cuenta de Resend (gratis)

**Tiempo total:** 20-30 minutos

---

## 🔧 Paso 1: Crear Base de Datos en Supabase

### 1.1 Crear Proyecto

1. Ve a https://supabase.com
2. Click en **"Start your project"**
3. Sign in con GitHub
4. Click en **"New project"**

**Configuración:**
- **Name:** inventario-pyme
- **Database Password:** (genera una segura, guárdala)
- **Region:** South America (São Paulo) - lo más cercano a Chile
- **Pricing Plan:** Free

5. Click **"Create new project"**
6. Espera 2-3 minutos mientras se crea

### 1.2 Obtener URL de Conexión

1. En tu proyecto, ve a **Settings** (⚙️) → **Database**
2. Scroll hasta **"Connection string"**
3. Selecciona la pestaña **"URI"**
4. Copia la URI (algo como):
   ```
   postgresql://postgres.abcdefgh:PASSWORD@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   ```
5. Reemplaza `[YOUR-PASSWORD]` con tu password real
6. **GUARDA ESTA URL** - la necesitarás

### 1.3 Verificar Conexión (Opcional)

En Supabase, ve a **SQL Editor** y ejecuta:
```sql
SELECT version();
```

Deberías ver la versión de PostgreSQL. ✅

---

## 📧 Paso 2: Configurar Resend para Emails

### 2.1 Crear Cuenta

1. Ve a https://resend.com
2. Click en **"Get Started"**
3. Sign up con email o GitHub
4. Verifica tu email

### 2.2 Crear API Key

1. Ve a **API Keys** en el menú
2. Click **"Create API Key"**
3. **Name:** inventario-api
4. **Permission:** Full Access (o solo "Sending access")
5. Click **"Add"**
6. **COPIA LA API KEY** (solo la verás una vez)
   - Formato: `re_123abc...`

### 2.3 Configurar Email de Origen

**Opción A: Para Pruebas (Sin verificación)**
- Usa: `onboarding@resend.dev`
- Funciona inmediatamente
- Solo para desarrollo

**Opción B: Tu Dominio (Producción)**
1. Ve a **Domains**
2. Click **"Add Domain"**
3. Ingresa tu dominio (ej: `tuempresa.cl`)
4. Agrega los registros DNS que te muestra
5. Espera verificación (5-30 minutos)
6. Usa: `alertas@tuempresa.cl`

**Opción C: Gratis sin Dominio (Recomendado para empezar)**
- Usa `onboarding@resend.dev`
- 3,000 emails/mes gratis
- Suficiente para testing y primeros clientes

---

## 🚂 Paso 3: Deploy en Railway

### 3.1 Preparar Código en GitHub

1. **Si no tienes Git instalado:**
   ```bash
   # Windows: Descarga de https://git-scm.com
   # Mac: brew install git
   # Linux: sudo apt install git
   ```

2. **Crear repositorio local:**
   ```bash
   cd inventario-api
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Crear repositorio en GitHub:**
   - Ve a https://github.com/new
   - **Repository name:** inventario-api
   - Visibilidad: **Private** (recomendado)
   - Click **"Create repository"**

4. **Subir código:**
   ```bash
   git remote add origin https://github.com/TU-USUARIO/inventario-api.git
   git branch -M main
   git push -u origin main
   ```

### 3.2 Conectar con Railway

1. Ve a https://railway.app
2. Click **"Start a New Project"**
3. Click **"Deploy from GitHub repo"**
4. Autoriza Railway en GitHub
5. Selecciona tu repositorio **inventario-api**
6. Railway detectará automáticamente Python y empezará el deploy

### 3.3 Configurar Variables de Entorno

1. En Railway, click en tu proyecto
2. Ve a **Variables**
3. Click **"New Variable"**

Agrega estas variables (una por una):

```bash
# Base de datos
DATABASE_URL=postgresql://postgres.abcdefgh:PASSWORD@aws-0-sa-east-1.pooler.supabase.com:6543/postgres

# Seguridad (genera con: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=tu_clave_secreta_generada_aqui

# Resend
RESEND_API_KEY=re_tu_api_key_de_resend
RESEND_FROM_EMAIL=onboarding@resend.dev

# Configuración
ENVIRONMENT=production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

4. Click **"Deploy"** si no se deployó automáticamente

### 3.4 Obtener URL de tu API

1. En Railway, ve a **Settings**
2. Scroll hasta **"Domains"**
3. Click **"Generate Domain"**
4. Railway te dará una URL como:
   ```
   https://inventario-api-production-xxxx.up.railway.app
   ```
5. **GUARDA ESTA URL** - es tu API pública

### 3.5 Verificar que Funciona

Abre en tu navegador:
```
https://TU-URL.railway.app/
```

Deberías ver:
```json
{
  "mensaje": "🏪 API de Inventario para PYME",
  "version": "1.0.0",
  "status": "✅ Funcionando"
}
```

**Documentación:**
```
https://TU-URL.railway.app/docs
```

---

## ✅ Paso 4: Verificar Todo Funciona

### 4.1 Crear Usuario

```bash
curl -X POST https://TU-URL.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test User",
    "email": "test@ejemplo.cl",
    "password": "password123"
  }'
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "nombre": "Test User",
  "email": "test@ejemplo.cl",
  "api_key": "sk_abc123...",
  "created_at": "2024-02-07T..."
}
```

### 4.2 Login

```bash
curl -X POST https://TU-URL.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.cl",
    "password": "password123"
  }'
```

Guarda el `access_token` de la respuesta.

### 4.3 Crear Producto

```bash
curl -X POST https://TU-URL.railway.app/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "nombre": "Coca Cola 1.5L",
    "sku": "BEB-001",
    "stock_actual": 10,
    "stock_minimo": 20
  }'
```

### 4.4 Probar Alerta de Email

Como creaste el producto con stock_actual (10) menor que stock_minimo (20), deberías recibir un email de alerta.

**Revisa tu email** (el que configuraste en Resend).

---

## 🔄 Actualizar la API

### Cuando hagas cambios en el código:

```bash
git add .
git commit -m "Descripción de cambios"
git push
```

Railway detectará el cambio y deployará automáticamente. ⚡

---

## 📊 Monitoreo

### Railway Dashboard

- **CPU/Memory:** Ver uso de recursos
- **Logs:** Ver logs en tiempo real
- **Metrics:** Gráficos de uso

### Supabase Dashboard

- **Table Editor:** Ver tus datos
- **SQL Editor:** Ejecutar queries
- **Logs:** Ver conexiones

### Resend Dashboard

- **Emails:** Ver emails enviados
- **Analytics:** Tasa de entrega
- **Logs:** Errores de envío

---

## 💰 Límites del Plan Gratis

### Railway
- **500 horas/mes** = ~20 días online 24/7
- Si necesitas más: $5/mes para 500 horas adicionales
- **Tip:** Apaga el servicio cuando no lo uses para ahorrar horas

### Supabase
- **500 MB** de espacio (suficiente para ~100,000 productos)
- **2 GB** de transferencia/mes
- **Si creces:** $25/mes para plan Pro

### Resend
- **3,000 emails/mes** = ~100/día
- **100 emails/día** límite
- **Si creces:** $20/mes para 50,000 emails

---

## 🛑 Solución de Problemas

### Error: "Application failed to respond"

**Causa:** Railway no puede conectarse a la base de datos

**Solución:**
1. Verifica que `DATABASE_URL` esté correcta en Variables
2. Verifica que Supabase esté online
3. Mira los logs en Railway

### Error: "ModuleNotFoundError"

**Causa:** Falta una dependencia

**Solución:**
1. Asegúrate de que `requirements.txt` esté correcto
2. Re-deploya: `git commit --allow-empty -m "Rebuild" && git push`

### Error: "This site can't be reached"

**Causa:** Railway no generó el dominio

**Solución:**
1. Ve a Settings → Domains
2. Click "Generate Domain"
3. Espera 1-2 minutos

### Emails no llegan

**Causa:** API key incorrecta o dominio no verificado

**Solución:**
1. Verifica `RESEND_API_KEY` en Railway
2. Usa `onboarding@resend.dev` para pruebas
3. Revisa logs de Resend

---

## 🎯 Checklist Final

- [ ] Supabase proyecto creado
- [ ] DATABASE_URL copiada
- [ ] Resend cuenta creada
- [ ] RESEND_API_KEY copiada
- [ ] Código en GitHub
- [ ] Railway proyecto creado
- [ ] Variables de entorno configuradas
- [ ] Dominio generado en Railway
- [ ] API respondiendo en `/`
- [ ] Documentación visible en `/docs`
- [ ] Usuario creado exitosamente
- [ ] Login funcionando
- [ ] Producto creado
- [ ] Email de alerta recibido

---

## 🚀 Siguiente Nivel

Una vez que funciona:

1. **Dominio personalizado** (opcional)
   - Railway: Settings → Domains → Add Custom Domain
   - Configura CNAME en tu proveedor de DNS

2. **Monitoreo** (opcional)
   - UptimeRobot (gratis) para verificar que esté online
   - Sentry (gratis) para tracking de errores

3. **Backup** (recomendado)
   - Supabase tiene backups automáticos (7 días)
   - Considera exportar manualmente cada semana

---

## 📞 Ayuda

**Railway:** https://docs.railway.app
**Supabase:** https://supabase.com/docs
**Resend:** https://resend.com/docs

---

**¡Tu API está online y funcionando gratis! 🎉**
