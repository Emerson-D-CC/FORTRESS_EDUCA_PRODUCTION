# <img src="app/static/img/shield.png" alt="Fortress Logo" width="50" align="center"> FORTRESS EDUCA

[![Python](https://img.shields.io/badge/Python-3.9+-3776ab.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000.svg?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

>Versión 8.3

## Descripción General

**Fortress Educa** es una plataforma web institucional diseñada para agilizar y centralizar el proceso de asignación de cupos educativos en colegios públicos de la localidad de Engativá (Bogotá D.C.). 

Esta solución tecnológica facilita el reintegro al sistema educativo de niños, niñas y adolescentes afectados por:

- Desplazamiento forzado
- Víctimas del conflicto armado
- Otros factores de vulnerabilidad económica y social

### Objetivos Principales

- **Garantizar acceso a la educación** de manera transparente y equitativa
- **Centralizar información** de solicitudes y seguimiento de cupos
- **Automatizar procesos** administrativos y de validación
- **Proteger datos** de menores en condición de vulnerabilidad
- **Facilitar seguimiento en línea** del estado de solicitudes

---

## Guía de Inicio Rápido

### Prerrequisitos

Antes de instalar Fortress Educa, asegúrate de tener instalados:

- **Python 3.12** ([Descargar](https://www.python.org/downloads/))
- **Git** ([Descargar](https://git-scm.com/))
- **pip** (gestor de paquetes de Python, incluido con Python)
- **Navegador web moderno** (Chrome, Firefox, Edge, Safari)

#### Verificar Instalación

```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar Git
git --version
```

---

## Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/fortress-educa.git
cd fortress-educa
```

### Paso 2: Crear Entorno Virtual

#### En Windows (PowerShell):

```powershell
# Crear el entorno virtual
py -m venv env

# Activar el entorno virtual
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\env\Scripts\Activate.ps1
```

#### En Windows (CMD):

```cmd
# Crear el entorno virtual
py -m venv env

# Activar el entorno virtual
env\Scripts\activate.bat
```

#### En macOS/Linux:

```bash
# Crear el entorno virtual
python3 -m venv env

# Activar el entorno virtual
source env/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
# Instalar todas las dependencias desde requirements.txt
pip install -r requirements.txt
```


### Paso 5: Configurar Base de Datos

```bash
# Ejecutar scripts SQL de inicialización
# (Revisar la carpeta database/scripts/)
```

### Paso 6: Ejecutar la Aplicación

```bash
# Iniciar el servidor Flask
python run.py

# O usando el comando One-liner (Windows PowerShell):
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\env\Scripts\Activate.ps1; python run.py
```

La aplicación estará disponible en: **http://localhost:5000**

---

## Detalles Técnicos y Arquitectura

### Tecnologías Utilizadas

#### Backend
- **Flask 3.1.3** - Framework web Python minimalista
- **Flask-JWT-Extended 4.7.1** - Autenticación con JWT tokens
- **Flask-Limiter 4.1.1** - Rate limiting y protección de API
- **Flask-Mail 0.10.0** - Envío de correos electrónicos
- **Flask-WTF 1.2.2** - Protección CSRF y validación de formularios

#### Base de Datos
- **MySQL/MariaDB** - Sistema gestor de base de datos relacional
- **PyMySQL** - Driver para conexión con MySQL

#### Frontend
- **HTML5** - Estructura semántica
- **CSS3** - Estilos y diseño responsivo
- **Bootstrap 5.3.0** - Framework CSS
- **JavaScript Vanilla** - Interactividad del lado cliente
- **Font Awesome 6.4.0** - Iconografía

#### Seguridad
- **reCAPTCHA** - Protección contra bots
- **CSRF Protection** - Protección contra ataques CSRF
- **JWT Tokens** - Autenticación segura
- **Password Hashing** - Encriptación de contraseñas

#### Otras Librerías
- **Pandas** - Procesamiento de datos y reportes
- **Python-dotenv** - Gestión de variables de entorno
- **Werkzeug** - Utilidades de seguridad

### Estructura del Proyecto

```
fortress-educa/
│
├── app/                              # Paquete principal de la aplicación
│   ├── __init__.py                  # Inicializador de Flask
│   ├── settings.py                  # Configuraciones globales
│   │
│   ├── blueprints/                  # Módulos funcionales (rutas)
│   │   ├── home/                    # Página de inicio y públicas
│   │   ├── auth/                    # Autenticación y registro
│   │   ├── aplication/              # Gestión de solicitudes
│   │   ├── tickets/                 # Sistema de tickets/soporte
│   │   ├── admin/                   # Panel administrativo
│   │   └── technical/               # Panel técnico
│   │
│   ├── controllers/                 # Lógica de negocio
│   │   ├── auth_controller.py       # Controlador de autenticación
│   │   ├── aplication_controller.py # Controlador de solicitudes
│   │   ├── admin_controller.py      # Controlador de administración
│   │   ├── tickets_controller.py    # Controlador de tickets
│   │   ├── technical_controller.py  # Controlador técnico
│   │   ├── home_controller.py       # Controlador de inicio
│   │   └── error_controller.py      # Controlador de errores
│   │
│   ├── repositories/                # Acceso a datos (DAO)
│   │   ├── auth_repository.py       # Operaciones de autenticación
│   │   ├── aplication_repository.py # Operaciones de solicitudes
│   │   ├── admin_repository.py      # Operaciones administrativas
│   │   ├── tickets_repository.py    # Operaciones de tickets
│   │   ├── technical_repository.py  # Operaciones técnicas
│   │   ├── home_repository.py       # Operaciones de inicio
│   │   ├── core_repository.py       # Operaciones de base de datos
│   │   └── utils_repository.py      # Utilidades de BD
│   │
│   ├── services/                    # Lógica de servicios (inyección)
│   │   ├── auth/                    # Servicios de autenticación
│   │   ├── admin/                   # Servicios de administración
│   │   ├── aplication/              # Servicios de solicitudes
│   │   ├── tickets/                 # Servicios de tickets
│   │   ├── technical/               # Servicios técnicos
│   │   ├── home/                    # Servicios de inicio
│   │   └── core/                    # Servicios core
│   │
│   ├── security/                    # Módulos de seguridad
│   │   ├── jwt_controller.py        # Gestión de JWT
│   │   ├── session_controller.py    # Control de sesiones
│   │   ├── forms_controller.py      # Validación de formularios
│   │   ├── mfa_controller.py        # Autenticación de dos factores
│   │   ├── recaptcha_controller.py  # Validación reCAPTCHA
│   │   └── redirect_controller.py   # Control de redirecciones
│   │
│   ├── forms/                       # Validación de formularios
│   │   ├── auth_forms.py            # Formularios de autenticación
│   │   ├── aplication_forms.py      # Formularios de solicitudes
│   │   ├── admin_forms.py           # Formularios administrativos
│   │   ├── tickets_forms.py         # Formularios de tickets
│   │   ├── technical_forms.py       # Formularios técnicos
│   │   ├── home_forms.py            # Formularios de inicio
│   │   └── core_forms.py            # Formularios core
│   │
│   ├── models/                      # Modelos de base de datos
│   │   └── (Modelos ORM)
│   │
│   ├── data_structures/             # Estructuras de datos
│   │   ├── report_row.py            # Estructura para filas de reportes
│   │   └── report_nodo.py           # Estructura para nodos de reportes
│   │
│   ├── utils/                       # Funciones de utilidad
│   │   ├── database_utils.py        # Utilidades de base de datos
│   │   ├── password_utils.py        # Utilidades de contraseñas
│   │   ├── validation_utils.py      # Validaciones comunes
│   │   ├── response_utils.py        # Formato de respuestas
│   │   ├── export_doc_utils.py      # Exportación de documentos
│   │   ├── dataframe_utils.py       # Utilidades de Pandas
│   │   ├── audit_utils.py           # Auditoría de operaciones
│   │   ├── extensions_utils.py      # Extensiones de Flask
│   │   └── decorators/              # Decoradores personalizados
│   │
│   ├── static/                      # Archivos estáticos
│   │   ├── css/                     # Hojas de estilo
│   │   ├── js/                      # Scripts JavaScript
│   │   ├── img/                     # Imágenes
│   │   └── lib/                     # Librerías externas
│   │
│   └── templates/                   # Plantillas HTML
│       ├── layout_public.html       # Layout para páginas públicas
│       ├── layout_aplication.html   # Layout para solicitudes
│       ├── layout_admin.html        # Layout administrativo
│       ├── layout_technical.html    # Layout técnico
│       ├── layout_tickets.html      # Layout de tickets
│       ├── home/                    # Páginas de inicio
│       ├── auth/                    # Páginas de autenticación
│       ├── aplication/              # Páginas de solicitudes
│       ├── admin/                   # Páginas administrativas
│       ├── technical/               # Páginas técnicas
│       ├── tickets/                 # Páginas de tickets
│       ├── errors/                  # Páginas de error
│       └── includes/                # Componentes reutilizables
│
├── database/                        # Configuración de base de datos
│   ├── scripts/                     # Scripts SQL
│   │   ├── basic_data.sql          # Datos iniciales
│   │   ├── functions.sql           # Funciones SQL
│   │   ├── procedures.sql          # Procedimientos almacenados
│   │   └── index.sql               # Índices
│   ├── generadores/                # Generadores de datos
│   │   ├── users_generator.py      # Generar usuarios de prueba
│   │   └── ticket_generator.py     # Generar tickets de prueba
│   └── backups/                    # Copias de seguridad
│
├── docs/                            # Documentación del proyecto
│   ├── arquitectura_actual.md       # Arquitectura técnica
│   ├── Cambios realizados.md        # Historial de cambios
│   ├── commands.md                  # Comandos útiles
│   ├── fuentes.md                   # Referencias y fuentes
│   ├── migracion_estructura.md      # Documentación de migraciones
│   └── PENDIENTE.md                 # Tareas pendientes
│
├── aws/                             # Configuración AWS
│   └── commands.txt                 # Comandos para despliegue
│
├── env/                             # Entorno virtual (no incluir en Git)
├── requirements.txt                 # Dependencias de Python
├── run.py                           # Punto de entrada de la aplicación
├── .env                             # Variables de entorno (no incluir en Git)
├── .gitignore                       # Archivos a ignorar en Git
└── README.md                        # Este archivo

```

### Patrón Arquitectónico: MVC + Inyección de Dependencias

Fortress Educa utiliza una arquitectura basada en **MVC (Model-View-Controller)** mejorada con capas de servicios y repositorio:

```
Request → Blueprint (Rutas)
   ↓
Controller (Lógica HTTP)
   ↓
Service (Lógica de Negocio)
   ↓
Repository (Acceso a Datos)
   ↓
Database
   ↓
Response → Template (Vistas HTML)
```

---

## Funcionalidades Principales

### Para Acudientes

1. **Registro y Autenticación**
   - Crear cuenta segura con validación de correo
   - Autenticación con 2FA (Autenticación de Dos Factores)
   - Recuperación de contraseña

2. **Gestión de Solicitudes**
   - Diligenciar formularios con datos del menor
   - Cargar documentación requerida
   - Seguimiento en línea del estado

3. **Panel de Control**
   - Ver historial de solicitudes
   - Descargar comprobantes
   - Recibir notificaciones por correo

###  Para Funcionarios/Técnicos

1. **Validación de Solicitudes**
   - Revisar documentación cargada
   - Validar datos de solicitantes
   - Cambiar estado de solicitudes

2. **Asignación de Cupos**
   - Asignar cupos en colegios disponibles
   - Generar reportes de asignación
   - Seguimiento de disponibilidad

3. **Sistema de Tickets**
   - Crear tickets de soporte
   - Gestionar comunicación con acudientes
   - Documentar procedimientos

###  Para Administradores

1. **Gestión de Usuarios**
   - Crear y editar usuarios del sistema
   - Asignar roles y permisos
   - Gestionar colegios y cupos

2. **Reportes y Auditoría**
   - Generar reportes estadísticos
   - Ver historial de cambios
   - Auditar operaciones del sistema

3. **Configuración del Sistema**
   - Parámetros de la plataforma
   - Gestión de correos
   - Mantenimiento general

---

## Seguridad

Fortress Educa implementa múltiples capas de seguridad:

- **Encriptación de contraseñas** usando Werkzeug
- **CSRF Protection** en todos los formularios
- **JWT Tokens** con expiración configurable
- **Rate Limiting** para prevenir ataques de fuerza bruta
- **reCAPTCHA** en formularios públicos
- **Validación y sanitización** de entrada
- **Sesiones seguras** con timeout
- **Cumplimiento GDPR** - Ley 1581 de 2012 (Colombia)

---

## Procesos del Sistema

### Flujo de Solicitud de Cupo

```
1. Registro del Acudiente
   ↓
2. Diligenciamiento de Solicitud
   ↓
3. Carga de Documentación
   ↓
4. Validación por Funcionario
   ↓
5. Asignación de Cupo
   ↓
6. Notificación y Confirmación
```

### Poblaciones Atendidas

- Desplazamiento Forzado
- Víctimas del Conflicto Armado
- Vulnerabilidad Económica
- Reintegro Educativo

---


## Documentación Adicional

Para más información detallada, consulta:

- [Arquitectura Actual](docs/arquitectura_actual.md) - Documentación técnica profunda
- [Cambios Realizados](docs/Cambios%20realizados.md) - Historial de modificaciones
- [Comandos](docs/commands.md) - Guía de comandos
- [Migraciones](docs/migracion_estructura.md) - Documentación de cambios en BD
- [Tareas Pendientes](docs/PENDIENTE.md) - Roadmap del proyecto

---

##  Contribución y Colaboración

### Reportar Problemas

Si encuentras un error o tienes una sugerencia de mejora:

1. Verifica que el problema no haya sido reportado
2. Abre un **Issue** describiendo:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Sistema operativo y navegador utilizado

### Contribuir Código

1. **Fork** el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/AmazingFeature`
3. Realiza tus cambios manteniendo el estilo de código
4. Commit con mensajes descriptivos: `git commit -m 'Add AmazingFeature'`
5. Push a la rama: `git push origin feature/AmazingFeature`
6. Abre un **Pull Request**

### Estándares de Código

- Seguir convenciones PEP 8 para Python
- Nombres descriptivos para variables y funciones
- Comentarios en español donde sea necesario
- Validación en frontend y backend

---

## Soporte e Información

### Canales de Contacto

| Canal | Información |
|-------|------------|
| **Email** | soporte@fortresseduca.com |
| **Teléfono** | +57 (1) 2345-6789 |
| **Ubicación** | Transversal 17 Nº 25-25, Engativá, Bogotá D.C. |
| **Horario** | Lunes a Viernes, 8:00 AM - 5:00 PM |

### Políticas Importantes

- [Política de Privacidad](app/templates/home/privacy_policy.html) - Protección de datos
- [Términos y Condiciones](app/templates/home/terms_of_use.html) - Uso de la plataforma
- [Código de Conducta](CODE_OF_CONDUCT.md) - Pautas de comportamiento

### Recursos

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [JWT en Python](https://flask-jwt-extended.readthedocs.io/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- 🇨🇴 [Normativa Colombiana de Protección de Datos](https://www.sic.gov.co/)

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

## Agradecimientos

Agradecemos a:

- La localidad de Engativá por el respaldo a la iniciativa
- Los colegios públicos participantes
- Comunidades de software libre que hicieron posible esta plataforma
- Todos los contribuidores al proyecto

---

## Historial de Versiones

### v1.0.0 (29 de Abril de 2026)
- Lanzamiento inicial
- Módulo de autenticación
- Gestión de solicitudes
- Panel administrativo
- Sistema de tickets
- Reportes y auditoría

---

## Roadmap Futuro

- [ ] Integración con sistemas SIEE (Secretaría de Educación)
- [ ] App móvil nativa (iOS/Android)
- [ ] Notificaciones por SMS
- [ ] Machine Learning para asignación inteligente
- [ ] APIs REST documentadas
- [ ] Dashboard avanzado de analytics

---

<div align="center">

**Construyendo oportunidades educativas para la niñez colombiana 🇨🇴**

Fortress Educa © 2026 | Plataforma de Reintegro Educativo en Engativá

</div>
