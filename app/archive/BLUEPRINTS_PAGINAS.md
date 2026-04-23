# ORGANIZACIÓN DE PÁGINAS POR BLUEPRINT

## Descripción General
Este documento explica la organización de páginas/templates en la nueva estructura basada en blueprints de Flask. Cada blueprint agrupa páginas relacionadas funcionalmente, facilitando el mantenimiento y la escalabilidad.

## 📋 Blueprint: pagina (Páginas Públicas)
**Prefijo de rutas:** `/` (raíz)
**Audiencia:** Usuarios no autenticados
**Layout base:** `layout_public.html`

### Páginas incluidas:
- **home.html** - Página de inicio/landing
- **about.html** - Información sobre la plataforma
- **contact.html** - Formulario de contacto
- **pricing.html** - Información de precios/planes
- **features.html** - Características del sistema
- **help.html** - Centro de ayuda público
- **terms.html** - Términos y condiciones
- **privacy.html** - Política de privacidad

### Funcionalidades:
- Información pública del sistema
- Formularios de contacto/registro inicial
- Navegación pública
- Contenido estático informativo

---

## 👤 Blueprint: aplicacion (Dashboard de Usuario)
**Prefijo de rutas:** `/app`
**Audiencia:** Usuarios autenticados (estudiantes/profesores)
**Layout base:** `layout_dashboard.html`

### Páginas incluidas:
- **index.html** - Dashboard principal del usuario
- **profile.html** - Perfil personal y configuración
- **register_student.html** - Registro de estudiantes
- **security.html** - Configuración de seguridad personal
- **settings.html** - Preferencias generales
- **ticket_request.html** - Solicitud de tickets/soporte
- **ticket_status.html** - Estado de tickets activos
- **ticket_detail.html** - Detalle específico de un ticket
- **notifications.html** - Centro de notificaciones
- **calendar.html** - Calendario personal
- **grades.html** - Visualización de calificaciones
- **schedule.html** - Horario de clases
- **assignments.html** - Tareas y entregas
- **resources.html** - Recursos de estudio

### Funcionalidades:
- Gestión del perfil personal
- Sistema de tickets/soporte
- Configuración de seguridad (MFA, contraseñas)
- Acceso a información académica
- Comunicación con administradores

---

## 🛡️ Blueprint: admin (Panel Administrativo)
**Prefijo de rutas:** `/admin`
**Audiencia:** Administradores del sistema
**Layout base:** `layout_admin.html`

### Páginas incluidas:
- **dashboard.html** - Panel principal de administración
- **users.html** - Gestión de usuarios (CRUD)
- **cases.html** - Gestión de casos/tickets
- **ticket_list.html** - Lista completa de tickets del sistema
- **ticket_response.html** - Responder a tickets específicos
- **ticket_reports.html** - Reportes de tickets y estadísticas
- **history.html** - Historial de actividades
- **settings.html** - Configuración del sistema
- **reports.html** - Reportes y estadísticas
- **logs.html** - Logs del sistema
- **backup.html** - Gestión de respaldos
- **system_info.html** - Información del sistema
- **user_permissions.html** - Gestión de permisos
- **announcements.html** - Comunicados del sistema
- **analytics.html** - Análisis de uso

### Funcionalidades:
- Gestión completa de usuarios
- Administración de tickets/casos
- Configuración global del sistema
- Reportes y monitoreo
- Mantenimiento del sistema

---

## 🎫 Sistema de Tickets - Decisión Arquitectural

### ❌ Opción Descartada: Blueprint Independiente
**No se recomienda crear un blueprint `tickets` separado porque:**
- Los usuarios accederían a tickets desde `/app/tickets/*`
- Los admins accederían desde `/admin/tickets/*`
- Separaría la funcionalidad de tickets de los flujos naturales de usuario/admin
- Complicaría la navegación y experiencia de usuario

### ✅ Opción Recomendada: Tickets en Blueprints Existentes

#### **Tickets en Blueprint `aplicacion`** (`/app`)
**Páginas del usuario:**
- `ticket_request.html` - Crear nuevos tickets
- `ticket_status.html` - Ver estado de mis tickets
- `ticket_detail.html` - Ver detalle específico de un ticket
- `ticket_history.html` - Historial de mis tickets

**Funcionalidades:**
- Solicitar soporte técnico
- Seguimiento de tickets personales
- Comunicación con administradores
- Gestión de tickets propios

#### **Tickets en Blueprint `admin`** (`/admin`)
**Páginas administrativas:**
- `ticket_list.html` - Lista completa de todos los tickets
- `ticket_response.html` - Responder y gestionar tickets
- `ticket_reports.html` - Reportes y estadísticas de tickets
- `cases.html` - Vista general de casos activos

**Funcionalidades:**
- Gestión centralizada de todos los tickets
- Asignación y respuesta a tickets
- Reportes y análisis de tickets
- Escalado de casos complejos

### 🔄 Servicios Compartidos
**A pesar de estar en blueprints diferentes, se compartirán:**
- `services/ticket_service.py` - Lógica de negocio de tickets
- `repositories/ticket_repository.py` - Acceso a datos de tickets
- `models/ticket_models.py` - Modelos de datos de tickets
- `forms/ticket_forms.py` - Formularios de tickets

**Beneficios de esta arquitectura:**
- ✅ **UX Natural**: Los usuarios gestionan tickets en su dashboard
- ✅ **UX Admin**: Los admins gestionan tickets en su panel
- ✅ **Código Reutilizable**: Servicios compartidos evitan duplicación
- ✅ **Separación de Roles**: Diferentes interfaces según permisos
- ✅ **Mantenibilidad**: Lógica centralizada en servicios compartidos

---

## 🔐 Blueprint: auth (Autenticación)
**Prefijo de rutas:** `/auth`
**Audiencia:** Todos los usuarios
**Layout base:** `layout_public.html`

### Páginas incluidas:
- **login.html** - Formulario de inicio de sesión
- **register.html** - Registro de nuevos usuarios
- **forgot_password.html** - Recuperación de contraseña
- **reset_password.html** - Restablecimiento de contraseña
- **verify_email.html** - Verificación de email
- **mfa_setup.html** - Configuración de MFA
- **mfa_verify.html** - Verificación de código MFA
- **logout.html** - Página de cierre de sesión
- **account_locked.html** - Cuenta bloqueada
- **email_sent.html** - Confirmación de envío de email

### Funcionalidades:
- Autenticación completa (login/logout)
- Registro de usuarios
- Recuperación de contraseñas
- Autenticación de dos factores (MFA)
- Verificación de email
- Manejo de sesiones

---

## 🔧 Componentes Compartidos (templates/components/)
**Ubicación:** `templates/components/`
**Uso:** Incluidos en múltiples layouts

### Componentes:
- **home_navbar_1.html** - Barra de navegación principal
- **home_navbar_2.html** - Barra de navegación secundaria
- **home_footer.html** - Pie de página público
- **user_header.html** - Cabecera del dashboard de usuario
- **user_sidebar.html** - Barra lateral del usuario
- **admin_header.html** - Cabecera del panel admin
- **admin_sidebar.html** - Barra lateral del admin
- **logout_modal.html** - Modal de confirmación de logout
- **modal_global.html** - Modal genérico reutilizable
- **modal_informative.html** - Modal informativo
- **modal_mandatory.html** - Modal obligatorio

---

## 🚨 Páginas de Error (templates/errors/)
**Ubicación:** `templates/errors/`
**Uso:** Manejadas por error handlers globales

### Páginas:
- **error.html** - Página genérica de error
- **404.html** - Página no encontrada
- **500.html** - Error interno del servidor
- **403.html** - Acceso prohibido
- **401.html** - No autorizado

---

## 🎨 Layouts Base (templates/layouts/)
**Ubicación:** `templates/layouts/`
**Uso:** Extendidos por páginas específicas

### Layouts:
- **layout_public.html** - Para páginas públicas
- **layout_dashboard.html** - Para dashboard de usuario
- **layout_admin.html** - Para panel administrativo

---

## 📁 Estructura de Archivos Final

```
templates/
├── layouts/
│   ├── layout_public.html
│   ├── layout_dashboard.html
│   └── layout_admin.html
├── components/
│   ├── home_navbar_1.html
│   ├── user_sidebar.html
│   └── modal_global.html
├── errors/
│   ├── 404.html
│   └── 500.html
├── pagina/
│   ├── home.html
│   └── contact.html
├── aplicacion/
│   ├── index.html
│   ├── profile.html
│   ├── ticket_request.html
│   ├── ticket_status.html
│   ├── ticket_detail.html
│   └── ticket_history.html
├── admin/
│   ├── dashboard.html
│   ├── users.html
│   ├── ticket_list.html
│   ├── ticket_response.html
│   ├── ticket_reports.html
│   └── cases.html
└── auth/
    ├── login.html
    ├── register.html
    └── mfa_verify.html
```

## 🔄 Migración desde Estructura Anterior

### De templates/home/ → templates/pagina/
- home.html
- contact.html
- about.html

### De templates/dashboard_users/ → templates/aplicacion/
- index.html → index.html
- profile.html → profile.html
- ticket_*.html → ticket_*.html

### De templates/admin/ → templates/admin/
- dashboard.html
- users.html
- cases.html

### Nuevos en templates/auth/
- Todas las páginas de autenticación
- MFA y recuperación de contraseña

Esta organización asegura una separación clara de responsabilidades y facilita el mantenimiento del código.

## 🔧 Implementación de Servicios Compartidos

### Para el Sistema de Tickets:
Los blueprints `aplicacion` y `admin` compartirán los siguientes componentes:

- **services/ticket_service.py** - Lógica de negocio centralizada
- **repositories/ticket_repository.py** - Acceso unificado a datos
- **models/ticket_models.py** - Estructuras de datos comunes
- **forms/ticket_forms.py** - Formularios reutilizables

Esto permite que tanto usuarios como administradores interactúen con el mismo sistema de tickets, pero con interfaces y permisos apropiados para cada rol.