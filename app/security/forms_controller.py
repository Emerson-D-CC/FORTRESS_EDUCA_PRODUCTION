import re
import bleach
import unicodedata

from markupsafe import escape

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField, HiddenField
from wtforms.validators import ValidationError


# =============================================================================
#  CONFIGURACIÓN GLOBAL
# =============================================================================

# Etiquetas HTML permitidas
ALLOWED_HTML_TAGS: list[str] = [] # [] = sin HTML permitido (recomendado)
ALLOWED_HTML_ATTRS: dict = {} # {} = sin atributos permitidos

# Longitud máxima genérica para cualquier campo de texto
MAX_FIELD_LENGTH: int = 2048

# Patrones que indican intentos de inyección SQL
SQL_INJECTION_PATTERNS: list[str] = [
    r"(\b)(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|CAST|CONVERT)(\b)",
    r"(--|;|\/\*|\*\/|xp_|@@|char\(|nchar\(|varchar\()",
    r"(\bOR\b|\bAND\b)\s+[\w'\"]+\s*=\s*[\w'\"]+", # OR 1=1 / AND 'a'='a'
]

# Patrones que indican intentos de inyección de comandos del sistema
CMD_INJECTION_PATTERNS = [
    r"[;`$]", # Separadores de shell
    r"\$\(.*\)", # Sustitución de comandos
    r"\.\./|\.\.\\", # Path traversal
]

# Patrones de XSS comunes no capturados por bleach
XSS_PATTERNS: list[str] = [
    r"javascript\s*:",
    r"vbscript\s*:",
    r"on\w+\s*=", # onerror=, onclick=, etc.
    r"<\s*script",
    r"<\s*iframe",
    r"data\s*:\s*text/html",
]



# =============================================================================
#  FILTROS DE CAMPO
# =============================================================================

#  Funciones puras que transforman el valor de un campo antes de validarlo.

def filter_strip(value: str | None) -> str:
    """Elimina espacios en blanco al inicio y al final."""
    return value.strip() if value else value


def filter_lowercase(value: str | None) -> str:
    """Convierte el valor a minúsculas (para emails)"""
    return value.lower() if value else value


def filter_strip_html(value: str | None) -> str:
    """Elimina todas las etiquetas HTML usando bleach"""
    if not value:
        return value
    return bleach.clean(value, tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRS, strip=True)


def filter_normalize_unicode(value: str | None) -> str:
    """Normaliza caracteres Unicode a su forma NFC"""
    if not value:
        return value
    return unicodedata.normalize("NFC", value)


def filter_remove_null_bytes(value: str | None) -> str:
    """Elimina bytes nulos que pueden causar truncamiento en bases de datos"""
    if not value:
        return value
    return value.replace("\x00", "")


def filter_collapse_whitespace(value: str | None) -> str:
    """Reemplaza múltiples espacios/tabs/newlines por un solo espacio"""
    if not value:
        return value
    return re.sub(r"\s+", " ", value).strip()


# Cadena de filtros predefinidas

#: Filtros para campos de texto plano (nombre, apellido, ciudad, etc.)
FILTERS_TEXT = [
    filter_remove_null_bytes,
    filter_normalize_unicode,
    filter_strip_html,
    filter_strip,
    filter_collapse_whitespace,
]

#: Filtros para campos de email
FILTERS_EMAIL = [
    filter_remove_null_bytes,
    filter_normalize_unicode,
    filter_strip_html,
    filter_strip,
    filter_lowercase,
]

#: Filtros para campos de textarea (descripciones, comentarios, etc.)
FILTERS_TEXTAREA = [
    filter_remove_null_bytes,
    filter_normalize_unicode,
    filter_strip_html,
    filter_strip,
]

#: Filtros mínimos para contraseñas (NO modificar el valor, solo limpiar bytes peligrosos)
FILTERS_PASSWORD = [
    filter_remove_null_bytes,
]



# =============================================================================
#  VALIDADORES DE CAMPO
# =============================================================================

#  Funciones que lanzan ValidationError si detectan contenido peligroso.

def validate_no_html(form, field):
    """Rechaza el campo si contiene etiquetas HTML después de la sanitización."""
    if not field.data:
        return
    cleaned = bleach.clean(field.data, tags=[], strip=True)
    if cleaned != field.data:
        raise ValidationError("El campo no puede contener código HTML.")


def validate_no_sql_injection(form, field):
    """Detecta patrones comunes de inyección SQL."""
    if not field.data:
        return
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, field.data, re.IGNORECASE):
            raise ValidationError("El campo contiene caracteres no permitidos.")


def validate_no_cmd_injection(form, field):
    """Detecta patrones de inyección de comandos del sistema operativo."""
    if not field.data:
        return
    for pattern in CMD_INJECTION_PATTERNS:
        if re.search(pattern, field.data):
            raise ValidationError("El campo contiene caracteres no permitidos.")


def validate_no_xss(form, field):
    """Detecta patrones de XSS que bleach podría no capturar en todos los contextos."""
    if not field.data:
        return
    for pattern in XSS_PATTERNS:
        if re.search(pattern, field.data, re.IGNORECASE):
            raise ValidationError("El campo contiene contenido no permitido.")


def validate_max_length(max_length: int = MAX_FIELD_LENGTH):
    """Fábrica de validadores: crea un validador de longitud máxima personalizado"""
    def _validate(form, field):
        if field.data and len(field.data) > max_length:
            raise ValidationError(f"El campo no puede superar {max_length} caracteres.")
    return _validate


def validate_only_printable(form, field):
    """Rechaza caracteres de control no imprimibles (excepto newline y tab)."""
    if not field.data:
        return
    for char in field.data:
        category = unicodedata.category(char)
        if category == "Cc" and char not in ("\n", "\t", "\r"):
            raise ValidationError("El campo contiene caracteres no válidos.")


# Grupos de validadores predefinidos

#: Validadores para campos de texto plano
VALIDATORS_TEXT = [
    validate_no_html,
    validate_no_sql_injection,
    # validate_no_cmd_injection,
    validate_no_xss,
    validate_only_printable,
]

#: Validadores para campos de textarea (más permisivos con whitespace)
VALIDATORS_TEXTAREA = [
    validate_no_html,
    validate_no_sql_injection,
    validate_no_xss,
]

#: Validadores para contraseñas
VALIDATORS_PASSWORD = [
    validate_no_xss,
    validate_only_printable,
]


# =============================================================================
#  MIXIN DE SANITIZACIÓN AUTOMÁTICA
# =============================================================================

#  Aplica automáticamente filtros a todos los campos StringField y TextAreaField


class AutoSanitizeMixin:

    _SECURITY_VALIDATORS: dict = {
        "password": VALIDATORS_PASSWORD,
        "email":    [],
        "textarea": VALIDATORS_TEXTAREA + [validate_no_cmd_injection],
        "text":     VALIDATORS_TEXT,
    }

    def _get_field_type(self, field) -> str | None:
        if isinstance(field, HiddenField):
            return None
        if isinstance(field, PasswordField):
            return "password"
        if isinstance(field, EmailField) or "email" in field.name.lower():
            return "email"
        if isinstance(field, TextAreaField):
            return "textarea"
        if isinstance(field, StringField):
            return "text"
        return None

    def _run_security_validators(self):
        """
        Corre validadores sobre el input crudo y guarda los errores
        en un dict propio. NO intenta modificar field.errors directamente
        porque es una tupla inmutable en este punto del ciclo de WTForms.
        """
        from wtforms.validators import ValidationError

        self._security_error_map = {}  # {field_name: [error1, error2, ...]}

        for field in self:
            if not field.data or not isinstance(field.data, str):
                continue

            field_type = self._get_field_type(field)
            if field_type is None:
                continue

            validators = self._SECURITY_VALIDATORS.get(field_type, [])
            for validator in validators:
                try:
                    validator(self, field)
                except ValidationError as e:
                    # Guardar en el mapa, nunca tocar field.errors aquí
                    if field.name not in self._security_error_map:
                        self._security_error_map[field.name] = []
                    self._security_error_map[field.name].append(str(e))

    def _sanitize_all_fields(self):
        FILTER_MAP = {
            "password": FILTERS_PASSWORD,
            "email":    FILTERS_EMAIL,
            "textarea": FILTERS_TEXTAREA,
            "text":     FILTERS_TEXT,
        }

        for field in self:
            if not field.data or not isinstance(field.data, str):
                continue

            field_type = self._get_field_type(field)
            if field_type is None:
                continue

            for f in FILTER_MAP.get(field_type, []):
                field.data = f(field.data)

    def validate(self, extra_validators=None):
        # ① Validar input crudo — errores van al mapa interno, no a field.errors
        self._run_security_validators()
        has_security_errors = bool(self._security_error_map)

        # ② Sanitizar para almacenamiento
        self._sanitize_all_fields()

        # ③ Validadores normales de WTForms
        wtforms_result = super().validate(extra_validators)

        # ④ Ahora sí field.errors ya es una lista mutable — inyectar errores de seguridad
        for field in self:
            if field.name in self._security_error_map:
                field.errors = list(field.errors) + self._security_error_map[field.name]

        return wtforms_result and not has_security_errors



# =============================================================================
#  CLASE BASE PRINCIPAL (SanitizedForm)
# =============================================================================

#  Hereda de AutoSanitizeMixin + FlaskForm.
#  Incluye protección CSRF de Flask-WTF y auto-sanitización de campos.

class SanitizedForm(AutoSanitizeMixin, FlaskForm):
    """Clase base para todos los formularios del proyecto.

    Incluye:
     Protección CSRF (Flask-WTF)
     Auto-sanitización de StringField, TextAreaField, EmailField y PasswordField
     Normalización Unicode
     Eliminación de HTML, XSS y bytes nulos

    Uso:
        class LoginUserForm(SanitizedForm):
            ...
    """
    pass



# =============================================================================
#  UTILIDADES DE SALIDA (Output Escaping)
# =============================================================================

#  Para usar en rutas Flask antes de enviar datos a templates o APIs.

def safe_output(value: str | None) -> str:
    """Escapa el valor para mostrarlo de forma segura en un template HTML.

    Ejemplo en una ruta:
        nombre = safe_output(request.form.get("nombre"))
    """
    if not value:
        return ""
    return str(escape(value))


def sanitize_for_db(value: str | None) -> str:
    """Sanitización mínima antes de enviar un valor a la base de datos"""
    if not value:
        return ""
    value = filter_remove_null_bytes(value)
    value = filter_normalize_unicode(value)
    value = filter_strip(value)
    return value
