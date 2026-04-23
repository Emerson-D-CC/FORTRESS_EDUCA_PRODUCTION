from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, MultipleFileField

from wtforms import StringField, SelectField, DateField, TelField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, ValidationError

from app.utils.validation_utils import regex

# FUNCIÓN PARA VALIDAR SI EL ID = 0
def seleccion_valida(form, field):
    """Validador para SelectField"""
    if not field.data or field.data == 0 or field.data == "0":
        raise ValidationError("Debe seleccionar una opción válida.")
    
    
# ====================================================================================================================================================
#                                           PAGINA TICKET_REQUEST.HTML
# ====================================================================================================================================================

class FormTicketPaso1(FlaskForm):
    """Paso 1 — Selección del estudiante."""
    
    id_estudiante = SelectField(
        "Estudiante",
        validators=[DataRequired(), seleccion_valida],
        coerce=int
    )


class FormTicketPaso2(FlaskForm):
    """Paso 2 — Vulnerabilidad."""
    
    id_tipo_afectacion = SelectField(
        "Tipo de Afectación",
        validators=[DataRequired(), seleccion_valida],
        coerce=int
    )
    
    descripcion = TextAreaField(
        "Descripción del Caso",
        validators=[DataRequired(), Length(min=50, max=2000)]
    )


class FormTicketPaso3(FlaskForm):
    """Paso 3 — Ubicación."""
    
    id_barrio = SelectField(
        "Barrio",
        validators=[DataRequired(), seleccion_valida],
        coerce=int
    )
    
    id_tiempo_residencia = SelectField(
        "Tiempo de Residencia",
        validators=[DataRequired(), seleccion_valida],
        coerce=int
    )


class FormTicketPaso4(FlaskForm):
    """Paso 4 — Preferencias educativas."""
    
    id_jornada = SelectField(
        "Jornada Preferida",
        validators=[DataRequired(), seleccion_valida],
        coerce=int
    )
    
    id_colegio = SelectField(
        "Colegio de Preferencia",
        validators=[Optional()],
        coerce=int
    )


class FormTicketPaso5(FlaskForm):
    """Paso 5 — Documentos."""
    doc_acudiente = FileField(
        "Documento del Acudiente",
        validators=[
            FileRequired(message="El documento del acudiente es obligatorio."),
            FileAllowed(["pdf", "jpg", "jpeg", "png"], "Solo PDF, JPG o PNG.")
        ]
    )
    
    doc_menor = FileField(
        "Documento del Menor",
        validators=[
            Optional(),
            FileAllowed(["pdf", "jpg", "jpeg", "png"], "Solo PDF, JPG o PNG.")
        ]
    )
    
    doc_certificados = MultipleFileField(
        "Certificados / Boletines",
        validators=[Optional()]
    )
    
    doc_victima = FileField(
        "Documento de Víctima",
        validators=[
            Optional(),
            FileAllowed(["pdf", "jpg", "jpeg", "png"], "Solo PDF, JPG o PNG.")
        ]
    )


class FormTicketPaso6(FlaskForm):
    """Paso 6 — Confirmación."""
    acepta_terminos = BooleanField(
        "Acepto y declaro que la información es verídica.",
        validators=[DataRequired(message="Debe aceptar los términos para continuar.")]
    )



    
# ====================================================================================================================================================
#                                           PAGINA TICKET_STATUS.HTML
# ====================================================================================================================================================

class FormSubirDocumento(FlaskForm):
    """Formulario para subir un documento adicional a un ticket existente."""

    tipo_documento = SelectField(
        "Tipo de Documento",
        validators=[DataRequired(), seleccion_valida],
        coerce=int,
    )

    archivo = FileField(
        "Archivo",
        validators=[
            FileRequired(message="Debe seleccionar un archivo."),
            FileAllowed(
                ["pdf", "jpg", "jpeg", "png"],
                message="Solo se permiten archivos PDF, JPG o PNG.",
            ),
        ],
    )

# ====================================================================================================================================================
#                                           PAGINA PROFILE.HTML
# ====================================================================================================================================================

# PERFIL - Acudiente

class FormAcudienteDatosPersonales(FlaskForm):
    """Campos NO editables del acudiente (solo lectura, sin validación activa)."""

    primer_nombre = StringField("Primer Nombre")
    segundo_nombre = StringField("Segundo Nombre")
    primer_apellido = StringField("Primer Apellido")
    segundo_apellido = StringField("Segundo Apellido")
    tipo_identificacion = StringField("Tipo de Documento")
    numero_documento = StringField("Número de Documento")
    parentesco = StringField("Parentesco")
    fecha_creacion = StringField("Fecha de Registro")
    email = StringField("Correo Electrónico")

class FormAcudienteDatosEditables(FlaskForm):
    """Campos editables del acudiente."""

    telefono = TelField(
        "Teléfono / Celular",
        validators = [DataRequired(), Length(min=7, max=20)]
    )
    
    barrio = SelectField(
        "Barrio",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )
    
    genero = SelectField(
        "Género",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )

    grupo_preferencial = SelectField(
        "Grupo Preferencial",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )

    estrato = SelectField(
        "Estrato",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )


# PERFIL - Estudiante

class FormEstudianteDatosPersonales(FlaskForm):
    """Campos NO editables del estudiante en perfil."""

    tipo_identificacion = StringField("Tipo de Identificación")
    
    numero_documento = StringField("Número de Documento")


class FormEstudianteDatosEditables(FlaskForm):
    """Campos editables del estudiante en perfil."""
    
    id_estudiante = HiddenField(
        "ID Estudiante",
        validators=[DataRequired()]
    )
    
    primer_nombre = StringField(
        "Primer Nombre",
        validators = [DataRequired(), Length(max=50)]
    )

    segundo_nombre = StringField(
        "Segundo Nombre",
        validators = [Optional(), Length(max=50)]
    )

    primer_apellido = StringField(
        "Primer Apellido",
        validators = [DataRequired(), Length(max=50)]
    )

    segundo_apellido = StringField(
        "Segundo Apellido",
        validators = [Optional(), Length(max=50)]
    )

    fecha_nacimiento = DateField(
        "Fecha de Nacimiento",
        validators = [DataRequired()]
    )

    genero = SelectField(
        "Género",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )

    grupo_preferencial = SelectField(
        "Grupo Preferencial",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )

    grado_actual = SelectField(
        "Último Grado Aprobado",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )

    grado_proximo = SelectField(
        "Grado a Cursar",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )

    colegio_anterior = SelectField(
        "Última Institución Educativa",
        validators = [DataRequired(), seleccion_valida],
        coerce = int
    )



# ====================================================================================================================================================
#                                           PAGINA REGISTER_STUDENT.HTML
# ====================================================================================================================================================

class FormRegistroEstudiante(FlaskForm):
    """Formulario completo para registrar un nuevo estudiante."""

    # Datos de identidad (TBL_PERSONA)
    primer_nombre = StringField(
        "Primer Nombre",
        validators = [DataRequired(), Length(max=50)]
    )

    segundo_nombre = StringField(
        "Segundo Nombre",
        validators = [Optional(), Length(max=50)]
    )

    primer_apellido = StringField(
        "Primer Apellido",
        validators = [DataRequired(), Length(max=50)]
    )

    segundo_apellido = StringField(
        "Segundo Apellido",
        validators = [Optional(), Length(max=50)]
    )

    fecha_nacimiento = DateField(
        "Fecha de Nacimiento",
        validators = [DataRequired()]
    )

    # Datos del estudiante (TBL_ESTUDIANTE)
    tipo_identificacion = SelectField(
        "Tipo de Identificación",
        validators = [DataRequired(), seleccion_valida],
        coerce = int,
        choices = [],
        validate_choice = False
    )

    numero_documento = StringField(
        "Número de Documento",
        validators = [DataRequired(), Length(max=15)]
    )

    genero = SelectField(
        "Género",
        validators = [DataRequired(), seleccion_valida],
        coerce = int,
        choices = [],
        validate_choice = False
    )

    grupo_preferencial = SelectField(
        "Grupo Preferencial",
        validators = [DataRequired(), seleccion_valida],
        coerce = int,
        choices = [],
        validate_choice = False
    )

    grado_actual = SelectField(
        "Último Grado Aprobado",
        validators = [DataRequired(), seleccion_valida],
        coerce = int,
        choices = [],
        validate_choice = False
    )

    grado_proximo = SelectField(
        "Grado a Cursar",
        validators = [DataRequired(), seleccion_valida],
        coerce = int,
        choices = [],
        validate_choice = False
    )

    colegio_anterior = SelectField(
        "Última Institución Educativa",
        validators = [DataRequired(), seleccion_valida],
        coerce = int,
        choices = [],
        validate_choice = False
    )

    parentesco = SelectField(
        "Parentesco con el Acudiente",
        validators = [DataRequired(), seleccion_valida],
        coerce=str,
        choices = [],
        validate_choice = False
    )



# ====================================================================================================================================================
#                                           PAGINA SECURITY.HTML
# ====================================================================================================================================================


class FormCambiarcontraseña(FlaskForm):
    """Formulario para cambiar la contraseña desde el perfil."""

    contraseña_actual = PasswordField(
        "Contraseña Actual",
        validators=[DataRequired(message="La contraseña actual es obligatoria.")]
    )

    nueva_contraseña = PasswordField(
        "Nueva Contraseña",
        validators=[
            DataRequired(message="La nueva contraseña es obligatoria."), 
            Length(min=10, max=255, message="Mínimo 10 caracteres.")
        ]
    )

    confirmar_contraseña = PasswordField(
        "Confirmar Nueva Contraseña",
        validators=[
            DataRequired(message="Confirme la nueva contraseña."),
            EqualTo("nueva_contraseña", message="Las contraseñas no coinciden.")
        ]
    )
    
    def validate_nueva_contraseña(self, field):
        errores = regex.formato_contraseña(field.data)
        if errores:
            mensaje = "La contraseña debe cumplir con: " + ", ".join(errores)
            raise ValidationError(mensaje)


class FormVerificarMFA(FlaskForm):
    """Formulario para confirmar un código TOTP al activar o autenticar 2FA."""

    codigo_mfa = StringField(
        "Código de verificación",
        validators=[DataRequired(), Length(min=6, max=6, message="El código debe tener exactamente 6 dígitos.")]
    )
    
    def validate_codigo_mfa(self, field):
        # regex.codigo_mfa retorna True si es válido (6 dígitos), False si es inválido
        if not regex.codigo_mfa(field.data):
            raise ValidationError("El código debe ser exactamente 6 dígitos numéricos.")
        
        

# ====================================================================================================================================================
#                                           PAGINA SETTINGS.HTML
# ====================================================================================================================================================


class FormNotificacionesEmail(FlaskForm):
    """Formulario para activar o desactivar notificaciones por correo electrónico."""
 
    notificaciones_email = BooleanField("Recibir alertas por Correo Electrónico")
    submit_email = SubmitField("Guardar")
 
 
class FormNotificacionesNavegador(FlaskForm):
    """Formulario para activar o desactivar notificaciones en el navegador."""
 
    notificaciones_navegador = BooleanField("Notificaciones en el Navegador")
    submit_navegador = SubmitField("Guardar")


class FormEliminarCuenta(FlaskForm):
    """Formulario para ejecutar baja lógica de usuario."""
    
    contraseña = PasswordField(
        "Contraseña",
        validators=[DataRequired()]
    )
    
    submit_eliminar = SubmitField("Eliminar cuenta")