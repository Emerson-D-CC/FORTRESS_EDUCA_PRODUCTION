from datetime import datetime, date

# FUNCIONES DE FLASK
from flask_wtf import FlaskForm

from wtforms import SelectField, HiddenField, StringField, SelectMultipleField, EmailField, TelField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, InputRequired, NumberRange, EqualTo, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget

# UTILIDADES
from app.utils.validation_utils import regex
# SECURIDAD
from app.security.forms_controller import SanitizedForm

# Validador reutilizable: asegura que el SelectField no quede en "-- Seleccione --"
def seleccion_valida(form, field):
    from wtforms.validators import ValidationError
    if not field.data or int(field.data) == 0:
        raise ValidationError("Debe seleccionar una opción válida.")
    

# ====================================================================================================================================================
#                                           PAGINA ACCOUNTS.HTML
# ====================================================================================================================================================

class FormToggleEstado(FlaskForm):
    """Form para protección CSRF al cambiar estado de usuario/estudiante/técnico"""
    pass  # Solo proporciona protección CSRF, nuevo_estado se maneja en request.form



# ====================================================================================================================================================
#                                           PAGINA CASES.HTML
# ====================================================================================================================================================

class FormFiltroTickets(SanitizedForm):
    """Filtros GET para la tabla de tickets"""

    class Meta:
        csrf = False

    estado = SelectField(
        "Estado",
        coerce=int,
        default=0,
        validators=[Optional()],
    )
    
    grado = SelectField(
        "Grado",
        coerce=int,
        default=0,
        validators=[Optional()],
    )
    
    afectacion = SelectField(
        "Tipo de Afectación",
        coerce=int,
        default=0,
        validators=[Optional()],
    )    
    
    
# ====================================================================================================================================================
#                                           PAGINA ACCOUNTS_NEW.HTML
# ====================================================================================================================================================

# VALIDADORES COMPARTIDOS

def _seleccion_valida(form, field):
    """Rechaza la opción placeholder (ID 0 o cadena vacía)."""
    if not field.data or str(field.data) in ("0", ""):
        raise ValidationError("Debe seleccionar una opción válida.")


def _validar_nombre(valor: str, label: str):
    if not valor:
        raise ValidationError(f"{label} no puede estar vacío.")
    if not regex.formato_nombre_apellido(valor):
        raise ValidationError(f"{label} no puede contener números ni caracteres especiales.")


def _validar_fecha_adulto(fecha_texto: str):
    """Valida que el usuario sea mayor de 18 y menor de 100 años."""
    if not fecha_texto:
        raise ValidationError("La fecha de nacimiento es obligatoria.")
    try:
        fecha = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Formato de fecha inválido.")
    hoy = date.today()
    if fecha >= hoy:
        raise ValidationError("La fecha no puede ser hoy ni una fecha futura.")
    edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
    if edad > 100:
        raise ValidationError("Fecha inválida (más de 100 años).")
    if edad < 18:
        raise ValidationError("El usuario debe ser mayor de 18 años.")

# ==========================================================================
# FORMULARIO: ACUDIENTE / TÉCNICO / ADMIN

class CreateUsuarioForm(SanitizedForm):
    """Formulario unificado para crear Acudiente (rol 2), Técnico (rol 3) o Admin (rol 4)"""

    form_type = HiddenField(default="acudiente")

    # Identificación
    tipo_documento = SelectField(
        "Tipo de Documento",
        validators=[DataRequired(message="Seleccione un tipo de documento."), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )
    documento = StringField(
        "Número de Documento",
        validators=[
            DataRequired(message="El número de documento es obligatorio."),
            Length(min=5, max=30, message="El documento debe tener entre 5 y 30 caracteres."),
        ],
    )

    # Nombre completo
    primer_nombre = StringField(
        "Primer Nombre",
        validators=[DataRequired(), Length(min=2, max=50)],
    )
    segundo_nombre = StringField("Segundo Nombre", validators=[Length(max=50)])
    primer_apellido = StringField(
        "Primer Apellido",
        validators=[DataRequired(), Length(min=2, max=50)],
    )
    segundo_apellido = StringField("Segundo Apellido", validators=[Length(max=50)])

    # Datos de contacto
    fecha_nacimiento = StringField(
        "Fecha de Nacimiento",
        validators=[DataRequired(message="La fecha de nacimiento es obligatoria.")],
    )
    parentesco = SelectField(
        "Parentesco",
        validators=[Optional()],   # La validación obligatoria se aplica vía validate_parentesco
        coerce=str,
        choices=[],
        validate_choice=False,
    )
    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(message="El teléfono es obligatorio."),
            Length(min=7, max=15),
        ],
    )
    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo electrónico es obligatorio."),
            Email(message="Ingrese un correo válido."),
            Length(max=255),
        ],
    )
    direccion = StringField(
        "Dirección",
        validators=[
            DataRequired(message="La dirección de residencia es obligatoria."),
            Length(max=255),
        ],
    )
    barrio = SelectField(
        "Barrio",
        validators=[DataRequired(), _seleccion_valida],
        coerce=int,
        choices=[],
        validate_choice=False,
    )

    # Seguridad
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=10, max=255, message="Mínimo 10 caracteres."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Confirme la contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )

    # Validadores personalizados

    def validate_primer_nombre(self, field):
        _validar_nombre(field.data.strip() if field.data else "", "El primer nombre")

    def validate_segundo_nombre(self, field):
        if not field.data or not field.data.strip():
            return
        if not regex.formato_nombre_apellido(field.data.strip()):
            raise ValidationError("El segundo nombre no puede contener números ni caracteres especiales.")

    def validate_primer_apellido(self, field):
        _validar_nombre(field.data.strip() if field.data else "", "El primer apellido")

    def validate_segundo_apellido(self, field):
        if not field.data or not field.data.strip():
            return
        if not regex.formato_nombre_apellido(field.data.strip()):
            raise ValidationError("El segundo apellido no puede contener números ni caracteres especiales.")

    def validate_documento(self, field):
        valor = field.data.strip() if field.data else ""
        if not valor:
            raise ValidationError("El documento no puede estar vacío.")
        if not regex.formato_numero_identificacion(valor):
            raise ValidationError("El documento solo puede contener números.")

    def validate_fecha_nacimiento(self, field):
        _validar_fecha_adulto(field.data)

    def validate_parentesco(self, field):
        """Solo es obligatorio para Acudiente."""
        if self.form_type.data == "acudiente":
            if not field.data or str(field.data) in ("0", ""):
                raise ValidationError("Debe seleccionar el parentesco con el menor.")

    def validate_telefono(self, field):
        valor = field.data.strip() if field.data else ""
        if not valor:
            raise ValidationError("El teléfono no puede estar vacío.")
        if not regex.formato_telefono_sin_prefijo_celular(valor):
            raise ValidationError("Ingrese un número de teléfono válido.")

    def validate_direccion(self, field):
        valor = field.data.strip() if field.data else ""
        if not valor:
            raise ValidationError("La dirección no puede estar vacía.")
        if not regex.formato_direccion(valor):
            raise ValidationError("Formato de dirección inválido. Ej: Cra 80 #65-12")

    def validate_password(self, field):
        if not field.data:
            raise ValidationError("La contraseña es obligatoria.")
        errores = regex.formato_contraseña(field.data)
        if errores:
            raise ValidationError("Requisitos no cumplidos: " + " | ".join(errores))


# ==========================================================================
# FORMULARIO: ESTUDIANTE

class CreateEstudianteForm(SanitizedForm):
    """Formulario para registrar un Estudiante"""

    # Identificación
    tipo_documento = SelectField(
        "Tipo de Documento",
        validators=[DataRequired(), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )
    documento = StringField(
        "Número de Documento",
        validators=[
            DataRequired(message="El documento es obligatorio."),
            Length(min=5, max=30),
        ],
    )

    # Nombre completo 
    primer_nombre   = StringField("Primer Nombre",   validators=[DataRequired(), Length(min=2, max=50)])
    segundo_nombre  = StringField("Segundo Nombre",  validators=[Length(max=50)])
    primer_apellido = StringField("Primer Apellido", validators=[DataRequired(), Length(min=2, max=50)])
    segundo_apellido = StringField("Segundo Apellido", validators=[Length(max=50)])

    # Datos personales 
    fecha_nacimiento = StringField(
        "Fecha de Nacimiento",
        validators=[DataRequired(message="La fecha de nacimiento es obligatoria.")],
    )
    genero = SelectField(
        "Género",
        validators=[DataRequired(), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )
    grupo_preferencial = SelectField(
        "Grupo Preferencial",
        validators=[DataRequired(), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )

    # Datos académicos
    grado_actual = SelectField(
        "Grado Actual",
        validators=[DataRequired(), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )
    grado_proximo = SelectField(
        "Grado Solicitado",
        validators=[Optional()],
        coerce=lambda x: int(x) if x not in (None, '', 'None') else 0,
        choices=[],
        validate_choice=False,
    )
    colegio_anterior = SelectField(
        "Colegio Anterior",
        validators=[DataRequired(), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )

    # Vínculo con Acudiente
    acudiente = SelectField(
        "Acudiente Responsable",
        validators=[DataRequired(), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )
    parentesco_estudiante = SelectField(
        "Parentesco del Acudiente con el Estudiante",
        validators=[DataRequired(), _seleccion_valida],
        coerce=str,
        choices=[],
        validate_choice=False,
    )

    # Validadores personalizados

    def validate_primer_nombre(self, field):
        _validar_nombre(field.data.strip() if field.data else "", "El primer nombre")

    def validate_segundo_nombre(self, field):
        if not field.data or not field.data.strip():
            return
        if not regex.formato_nombre_apellido(field.data.strip()):
            raise ValidationError("El segundo nombre no puede contener números ni caracteres especiales.")

    def validate_primer_apellido(self, field):
        _validar_nombre(field.data.strip() if field.data else "", "El primer apellido")

    def validate_segundo_apellido(self, field):
        if not field.data or not field.data.strip():
            return
        if not regex.formato_nombre_apellido(field.data.strip()):
            raise ValidationError("El segundo apellido no puede contener números ni caracteres especiales.")

    def validate_documento(self, field):
        valor = field.data.strip() if field.data else ""
        if not valor:
            raise ValidationError("El documento no puede estar vacío.")
        if not regex.formato_numero_identificacion(valor):
            raise ValidationError("El documento solo puede contener números.")

    def validate_fecha_nacimiento(self, field):
        if not field.data:
            raise ValidationError("La fecha de nacimiento es obligatoria.")
        try:
            fecha = datetime.strptime(field.data, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Formato de fecha inválido.")
        hoy = date.today()
        if fecha >= hoy:
            raise ValidationError("La fecha no puede ser hoy ni una fecha futura.")
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        if edad > 25:
            raise ValidationError("La edad del estudiante parece inválida (más de 25 años).")
        if edad < 3:
            raise ValidationError("La edad mínima para registro es 3 años.")


    
# ====================================================================================================================================================
#                                           PAGINA SCHOOL_STATUS.HTML
# ====================================================================================================================================================

# Widget para múltiple selección con checkboxes
class MultiCheckboxField(SelectMultipleField):
    """SelectMultipleField renderizado como checkboxes individuales"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


# Filtro de la tabla

class FormFiltroColegios(SanitizedForm):
    """Formulario GET para los filtros de la tabla de colegios"""
    class Meta:
        csrf = False   # filtros GET no requieren CSRF

    nombre = StringField(
        "Buscar por nombre",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Buscar por nombre"},
    )

    estado = SelectField(
        "Estado",
        validators=[Optional()],
        choices=[
            ("", "Todos"),
            ("1", "Activo"),
            ("0", "Inactivo"),
        ],
        default="",
    )

    id_barrio = SelectField(
        "Barrio",
        validators=[Optional()],
        coerce=int,
        choices=[],   # se carga dinámicamente en el servicio
    )

    id_jornada = SelectField(
        "Jornada",
        validators=[Optional()],
        coerce=int,
        choices=[],   # se carga dinámicamente en el servicio
    )


# Modal Agregar Colegio

class FormAgregarColegio(SanitizedForm):
    """Registro de un nuevo colegio desde el modal"""

    nombre = StringField(
        "Nombre de la Institución",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=100, message="Máximo 100 caracteres."),
        ],
        render_kw={"placeholder": "Ej: IED Quirigua"},
    )

    dane = StringField(
        "Código DANE",
        validators=[
            DataRequired(message="El código DANE es obligatorio."),
            Length(min=12, max=15, message="El código DANE debe tener entre 12 y 15 caracteres."),
            Regexp(r"^\d+$", message="El código DANE debe contener solo dígitos."),
        ],
        render_kw={"placeholder": "Ej: 111001000xxx", "maxlength": "15"},
    )

    id_barrio = SelectField(
        "Barrio",
        validators=[DataRequired(message="Seleccione un barrio."), seleccion_valida],
        coerce=int,
        choices=[],   # se carga en el servicio
    )

    direccion = StringField(
        "Dirección",
        validators=[
            DataRequired(message="La dirección es obligatoria."),
            Length(max=100, message="Máximo 100 caracteres."),
        ],
        render_kw={"placeholder": "Ej: Cl 67 No. 77-50"},
    )

    email = EmailField(
        "Email Institucional",
        validators=[
            Optional(),
            Email(message="Ingrese un correo electrónico válido."),
            Length(max=255),
        ],
        render_kw={"placeholder": "colegio@educacionbogota.edu.co"},
    )

    telefono = TelField(
        "Teléfono",
        validators=[
            Optional(),
            Length(max=45),
            Regexp(r"^\d+$", message="Solo dígitos."),
        ],
        render_kw={"placeholder": "Ej: 6012509683"},
    )

    # Jornadas iniciales (al menos una)
    jornadas = MultiCheckboxField(
        "Jornadas Disponibles",
        validators=[DataRequired(message="Seleccione al menos una jornada.")],
        coerce=int,
        choices=[],   # se carga en el servicio
    )
    
    

# ====================================================================================================================================================
#                                           PAGINA SCHOOL_CONFIG.HTML
# ====================================================================================================================================================

# Editar datos de un colegio

class FormEditarColegio(SanitizedForm):
    """Edición de datos de un colegio existente"""

    nombre = StringField(
        "Nombre de la Institución",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=100),
        ],
    )

    dane = StringField(
        "Código DANE",
        validators=[
            DataRequired(message="El código DANE es obligatorio."),
            Length(min=12, max=15),
            Regexp(r"^\d+$", message="Solo dígitos."),
        ],
    )

    id_barrio = SelectField(
        "Barrio",
        validators=[DataRequired(message="Seleccione un barrio."), seleccion_valida],
        coerce=int,
        choices=[],
    )

    direccion = StringField(
        "Dirección",
        validators=[
            DataRequired(message="La dirección es obligatoria."),
            Length(max=100),
        ],
    )

    email = EmailField(
        "Email Institucional",
        validators=[Optional(), Email(), Length(max=255)],
    )

    telefono = TelField(
        "Teléfono",
        validators=[Optional(), Length(max=45), Regexp(r"^\d*$")],
    )


# Guardar jornadas 

class FormGuardarJornadas(FlaskForm):
    """Checkboxes para activar/desactivar jornadas del colegio. Los choices se cargan dinámicamente en el servicio"""

    jornadas_activas = MultiCheckboxField(
        "Jornadas",
        validators=[DataRequired(message="El colegio debe tener al menos una jornada activa.")],
        coerce=int,
        choices=[],
    )


# Cambio de estado de un colegio (eliminado logico)

class FormCambiarEstadoColegio(FlaskForm):
    """Formulario mínimo para confirmar el cambio de estado"""
    # Campo oculto para confirmar la acción desde el modal
    confirmar = HiddenField(default="1")
    
    

# ====================================================================================================================================================
#                                           PAGINA SETTINGS.HTML
# ====================================================================================================================================================


class FormPrioridadAfectacion(SanitizedForm):
    """Crear o editar un Tipo de Afectación"""

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=60, message="Máximo 60 caracteres."),
        ],
    )
    descripcion = StringField(
        "Descripción",
        validators=[
            DataRequired(message="La descripción es obligatoria."),
            Length(max=150, message="Máximo 150 caracteres."),
        ],
    )
    nivel_prioridad = IntegerField(
        "Nivel de Prioridad",
        validators=[
            InputRequired(message="El nivel es obligatorio."),
            NumberRange(min=0, max=99, message="Debe estar entre 0 y 99."),
        ],
    )


class FormPrioridadGrupo(SanitizedForm):
    """Crear o editar un Grupo Preferencial"""

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=30, message="Máximo 30 caracteres."),
        ],
    )
    descripcion = StringField(
        "Descripción",
        validators=[
            DataRequired(message="La descripción es obligatoria."),
            Length(max=150, message="Máximo 150 caracteres."),
        ],
    )
    nivel_prioridad = IntegerField(
        "Nivel de Prioridad",
        validators=[
            InputRequired(message="El nivel es obligatorio."),
            NumberRange(min=0, max=99, message="Debe estar entre 0 y 99."),
        ],
    )


class FormPrioridadEstrato(SanitizedForm):
    """Crear o editar un Estrato Socioeconómico"""

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=10, message="Máximo 10 caracteres."),
        ],
    )
    
    descripcion = StringField(
        "Descripción",
        validators=[
            DataRequired(message="La descripción es obligatoria."),
            Length(max=150, message="Máximo 150 caracteres."),
        ],
    )
    
    nivel_prioridad = IntegerField(
        "Nivel de Prioridad",
        validators=[
            InputRequired(message="El nivel es obligatorio."),
            NumberRange(min=0, max=99, message="Debe estar entre 0 y 99."),
        ],
    )




# ====================================================================================================================================================
#                                           PAGINA SECURITY.HTML
# ====================================================================================================================================================

class FormCambiarcontraseña(FlaskForm):
    """Formulario para cambiar la contraseña desde el perfil"""

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