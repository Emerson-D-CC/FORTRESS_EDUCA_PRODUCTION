# PROYECTO FORTRESS EDUCA - NUEVA ESTRUCTURA

## Descripción
Esta es la versión reestructurada del proyecto Fortress Educa, migrada desde la estructura modular original a una arquitectura basada en blueprints de Flask.

## Estructura Anterior vs Nueva

### Estructura Original:
```
app/
├── modules/
│   ├── home/
│   ├── dashboard_user/
│   └── admin/
├── security/
├── database/
├── core/
├── utils/
├── templates/
└── static/
```

### Nueva Estructura (Blueprint-based):
```
app/
├── blueprints/          # Blueprints organizados por funcionalidad
│   ├── pagina/         # Home/landing público
│   ├── aplicacion/     # Dashboard de usuario
│   ├── admin/          # Panel administrativo
│   └── auth/           # Autenticación y seguridad
├── controllers/        # Lógica de rutas (antes routes.py)
├── services/           # Lógica de negocio
├── repositories/       # Acceso a datos
├── models/             # Modelos de datos
├── forms/              # Formularios WTForms
├── utils/              # Utilidades generales
├── core/               # Configuración central
├── data_structures/    # Estructuras de datos
├── templates/          # Templates organizados por blueprint
└── static/             # Archivos estáticos
```

## Arquitectura por Capas

1. **Blueprints**: Punto de entrada por funcionalidad
2. **Controllers**: Manejo de rutas HTTP y respuestas
3. **Services**: Lógica de negocio y validaciones
4. **Repositories**: Acceso a datos y consultas SQL
5. **Models**: Definición de estructuras de datos
6. **Forms**: Validación y procesamiento de formularios

## Beneficios de la Nueva Estructura

- **Separación de responsabilidades**: Cada capa tiene una función específica
- **Mantenibilidad**: Código más fácil de mantener y modificar
- **Escalabilidad**: Fácil agregar nuevas funcionalidades
- **Testabilidad**: Cada componente puede ser probado independientemente
- **Reutilización**: Servicios y utilidades compartidos entre blueprints

## Flujo de una Request

1. **Blueprint** → Define el prefijo de rutas
2. **Controller** → Recibe la request y valida parámetros
3. **Service** → Ejecuta lógica de negocio
4. **Repository** → Accede a la base de datos
5. **Model** → Estructura los datos de respuesta
6. **Template** → Renderiza la vista final

## Configuración

- **Base de datos**: MySQL con stored procedures
- **Autenticación**: JWT + MFA (TOTP)
- **Seguridad**: reCAPTCHA, hashing, sesiones
- **Framework**: Flask con extensiones (Mail, CSRF, etc.)

## Inicio Rápido

1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar variables de entorno
3. Ejecutar: `python run.py`