# FUNCIONES DE FLASK
from flask_wtf import FlaskForm
from datetime import date, datetime

from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

# UTILIDADES
from app.utils.validation_utils import regex
# SECURIDAD
from app.security.forms_controller import SanitizedForm

# ====================================================================================================================================================
#                                           PAGINA LOGIN_USER.HTML
# ====================================================================================================================================================

class LoginUserForm(SanitizedForm):

    username = StringField(
        "Usuario",
        validators = [DataRequired(), Length(min=3, max=100), Email()]
    )
    
    password = PasswordField(
        "Contraseña",
        validators = [DataRequired(), Length(min=6, max=255)]
    )
    


# ====================================================================================================================================================
#                                           PAGINA LOGIN_ADMIN.HTML
# ====================================================================================================================================================

class LoginAdminForm(SanitizedForm):

    username_admin = StringField(
        "Usuario",
        validators = [DataRequired(), Length(min=3, max=100), Email()]
    )
    
    password = PasswordField(
        "Contraseña",
        validators = [DataRequired(), Length(min=6, max=255)]
    )
    


# ====================================================================================================================================================
#                                           PAGINA LOGIN_TECHNICAL.HTML
# ====================================================================================================================================================

class LoginTecForm(SanitizedForm):

    username_technical = StringField(
        "Usuario",
        validators = [DataRequired(), Length(min=3, max=100), Email()]
    )
    
    password = PasswordField(
        "Contraseña",
        validators = [DataRequired(), Length(min=6, max=255)]
    )
    


# ====================================================================================================================================================
#                                           PAGINA CONFIG_MFA.HTML
# ====================================================================================================================================================

class FormVerificarMFA(FlaskForm):
    """Formulario para confirmar un código TOTP al activar o autenticar 2FA"""

    codigo_mfa = StringField(
        "Código de verificación",
        validators = [
            DataRequired(message="Ingrese el código de 6 dígitos."), 
            Length(min=6, max=6, message="El código debe tener exactamente 6 dígitos.")
        ]
    )
    
    def validate_codigo_mfa(self, field):
        # regex.codigo_mfa retorna True si es válido (6 dígitos), False si es inválido
        if not regex.codigo_mfa(field.data):
            raise ValidationError("El código debe ser exactamente 6 dígitos numéricos.")



# ====================================================================================================================================================
#                                           PAGINA VERIFY_MFA.HTML
# ====================================================================================================================================================
    
class FormVerificarMFA(FlaskForm):

    codigo_mfa = StringField(
        "Código de verificación",
        validators = [
            DataRequired(message = "Ingrese el código de 6 dígitos."),
            Length(min=6, max=6, message = "El código debe tener exactamente 6 dígitos.")
        ]
    )
    
    def validate_codigo_mfa(self, field):
        if not regex.codigo_mfa(field.data):
            raise ValidationError("El código debe ser exactamente 6 dígitos numéricos.")



# ====================================================================================================================================================
#                                           PAGINA REGISTER.HTML
# ====================================================================================================================================================
        
# VALIDADOR PERSONALIZADO

def seleccion_valida(form, field):
    """Asegura que el usuario haya seleccionado una opción válida (no ID 0 o vacío)"""
    
    if not field.data or field.data == 0 or field.data == "0":
        raise ValidationError("Debe seleccionar una opción válida.")
    
class RegisterForm(SanitizedForm):
    
    # SECCIÓN 1: DATOS DEL ACUDIENTE
        
        # IDENTIFICACIÓN DEL ACUDIENTE 
    tipo_documento = SelectField(
        "Tipo Documento",
        validators = [
            DataRequired(message = "Debe seleccionar un tipo de documento."),
            seleccion_valida
        ],
        coerce=str,
        choices = [],
        validate_choice = False
    )

    documento = StringField(
        "Documento",
        validators = [
            DataRequired(message = "El número de documento es obligatorio."),
            Length(min=5, max=15, message = "El documento debe tener entre 5 y 15 caracteres.")
        ]
    )
    
        # NOMBRE COMPLETO DEL ACUDIENTE
    primer_nombre = StringField(
        "Primer Nombre",
        validators = [
            DataRequired(message = "El primer nombre es obligatorio."),
            Length(min=2, max=50, message = "El nombre debe tener entre 2 y 50 caracteres.")
        ],
    )

    segundo_nombre = StringField(
        "Segundo Nombre",
        validators = [
            Length(max=50, message = "El segundo nombre no puede exceder 50 caracteres.")
        ]
    )

    primer_apellido = StringField(
        "Primer Apellido",
        validators = [
            DataRequired(message = "El primer apellido es obligatorio."),
            Length(min=2, max=50, message = "El apellido debe tener entre 2 y 50 caracteres.")
        ]
    )

    segundo_apellido = StringField(
        "Segundo Apellido",
        validators = [
            Length(max=50, message = "El segundo apellido no puede exceder 50 caracteres.")
        ]
    )

        # DATOS PERSONALES Y DE CONTACTO
    fecha_nacimiento = StringField(
        "Fecha de Nacimiento",
        validators = [
            DataRequired(message = "La fecha de nacimiento es obligatoria.")
        ]
    )
    
    parentesco = SelectField(
        "Parentesco con el Menor",
        validators = [
            DataRequired(message = "Debe seleccionar el parentesco con el menor."),
            seleccion_valida
        ],
        coerce=str,
        choices = []
    )

    telefono = StringField(
        "Teléfono",
        validators = [
            DataRequired(message = "El teléfono es obligatorio."),
            Length(min=7, max=15, message = "El teléfono debe tener entre 7 y 15 caracteres.")
        ]
    )

    email = StringField(
        "Correo Electrónico",
        validators = [
            DataRequired(message = "El correo electrónico es obligatorio."),
            Email(message = "Debe ingresar un correo electrónico válido."),
            Length(max=255, message = "El correo no puede exceder 255 caracteres.")
        ]
    )

    direccion = StringField(
        "Dirección",
        validators = [
            DataRequired(message = "La dirección de residencia es obligatoria."),
            Length(max=255, message = "La dirección no puede exceder 255 caracteres.")
        ]
    )

    barrio = SelectField(
        "Barrio",
        validators = [
            DataRequired(message = "Debe seleccionar un barrio."),
            seleccion_valida
        ],
        coerce=int,
        choices = []
    )


    # SECCIÓN 2: SEGURIDAD
    
        # CONTRASEÑA DE ACCESO
    password = PasswordField(
        "Contraseña",
        validators = [
            DataRequired(message = "La contraseña es obligatoria."),
            Length(min=10, max=255, message = "Debe tener mínimo 10 caracteres.")
        ]
    )

    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators = [
            DataRequired(message = "Debe confirmar la contraseña."),
            EqualTo("password", message = "Las contraseñas no coinciden.")
        ]
    )

    
    # SECCIÓN 3: TÉRMINOS Y CONDICIONES
    
    terms = BooleanField(
        "Aceptación de términos",
        validators = [
            DataRequired(message = "Debe aceptar los términos y condiciones para continuar.")
        ]
    )

    # VALIDADORES PERSONALIZADOS (REGEX)

    def validate_primer_nombre(self, field):
        """Validador personalizado para primer nombre"""
        # El campo es obligatorio, así que siempre tendrá datos
        valor = field.data.strip() if field.data else ""
        
        if not valor:
            raise ValidationError("El primer nombre no puede estar vacío.")
        
        if not regex.formato_nombre_apellido(valor):
            raise ValidationError("El nombre no puede contener números ni caracteres especiales.")
    
    def validate_segundo_nombre(self, field):
        """Validador personalizado para segundo nombre"""
        # Si el campo está vacío, no validar
        if not field.data or not field.data.strip():
            return  # ← Salir sin error
        
        valor = field.data.strip()
        
        # Si tiene datos, validar formato
        if not regex.formato_nombre_apellido(valor):
            raise ValidationError("El segundo nombre no puede contener números ni caracteres especiales.")
    
    def validate_primer_apellido(self, field):
        """Validador personalizado para primer apellido"""
        # El campo es obligatorio, así que siempre tendrá datos
        valor = field.data.strip() if field.data else ""
        
        if not valor:
            raise ValidationError("El primer apellido no puede estar vacío.")
        
        if not regex.formato_nombre_apellido(valor):
            raise ValidationError("El apellido no puede contener números ni caracteres especiales.")
        
    def validate_segundo_apellido(self, field):
        """Validador personalizado para segundo apellido"""
        # Si el campo está vacío, no validar
        if not field.data or not field.data.strip():
            return  # ← Salir sin error
        
        valor = field.data.strip()
        
        # Si tiene datos, validar formato
        if not regex.formato_nombre_apellido(valor):
            raise ValidationError("El segundo apellido no puede contener números ni caracteres especiales.")
 
 
    def validate_documento(self, field):
        """Validador personalizado para número de documento"""
        valor = field.data.strip() if field.data else ""
        
        if not valor:
            raise ValidationError("El documento no puede estar vacío.")
        
        if not regex.formato_numero_identificacion(valor):
            raise ValidationError
        
        
    def validate_telefono(self, field):
        """Validador personalizado para teléfono"""
        valor = field.data.strip() if field.data else ""
        
        if not valor:
            raise ValidationError("El teléfono no puede estar vacío.")
        
        if not regex.formato_telefono_sin_prefijo_celular(valor):
            raise ValidationError
 
 
    def validate_direccion(self, field):
        """Validador personalizado para la dirección"""
        valor = field.data.strip() if field.data else ""
        
        if not valor:
            raise ValidationError("La dirección no puede estar vacía.")
        
        if not regex.formato_direccion(valor):
            raise ValidationError(
                "Formato de dirección inválido. Ej: Cra 80 #65-12 o Calle 50 #25-30"
            )
 

    def validate_fecha_nacimiento(self, field):
        """Validador personalizado para fecha de nacimiento"""
        fecha_texto = field.data
        
        if not fecha_texto:
            raise ValidationError("La fecha de nacimiento es obligatoria.")
        
        # 1. Convertimos la cadena de texto 'YYYY-MM-DD' a un objeto de tipo date
        try:
            fecha = datetime.strptime(fecha_texto, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("El formato de la fecha de nacimiento no es válido.")
            
        hoy = date.today()
        
        # 2. Ahora sí podemos comparar fechas reales sin romper Python
        # Fecha futura o actual
        if fecha >= hoy:
            raise ValidationError("La fecha de nacimiento no puede ser hoy ni una fecha futura.")
        
        # Calcular edad
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        
        # Edad mayor a 100 años (fecha improbable)
        if edad > 100:
            raise ValidationError("La fecha de nacimiento es inválida (edad mayor a 100 años).")
            
        # Menor de edad (< 18 años)
        if edad < 18:
            raise ValidationError("Debes ser mayor de 18 años para registrarte.")

 
 
    def validate_password(self, field):
        """Validador personalizado para contraseña"""
        contraseña = field.data
        
        if not contraseña:
            raise ValidationError("La contraseña es obligatoria.")
        
        # Validar requisitos de complejidad usando la función existente
        errores = regex.formato_contraseña(contraseña)
        
        if errores:
            # Concatenar todos los errores en un mensaje claro
            mensaje_error = "Requisitos no cumplidos: " + " | ".join(errores)
            raise ValidationError(mensaje_error)


# ====================================================================================================================================================
#                                           PAGINA RECOVER_PASSWORD.HTML
# ====================================================================================================================================================

class RecuperarcontraseñaForm(SanitizedForm):
    username = StringField(
        "Correo Electrónico",
        validators = [DataRequired(), Length(min=3, max=100), Email()]
    )

class VerificarCodigoForm(FlaskForm):
    codigo = StringField(
        "Código de Verificación",
        validators = [DataRequired(), Length(min=6, max=6)]
    )


class NuevacontraseñaForm(SanitizedForm):
    password = PasswordField(
        "Nueva Contraseña",
        validators = [DataRequired(), Length(min=6, max=255)]
    )
    confirmar_password = PasswordField(
        "Confirmar Contraseña",
        validators = [DataRequired(), EqualTo("password", message = "Las contraseñas no coinciden.")]
    )

    def validate_password(self, field):
        """Validador personalizado para contraseña"""
        errores = regex.formato_contraseña(field.data)
        if errores:
            # Crear mensaje detallado con cada error
            mensaje = "La contraseña debe cumplir con lo siguiente:\n"
            mensaje += "\n".join([f"• {error}" for error in errores])
            raise ValidationError(mensaje) 
