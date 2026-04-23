from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms import SelectField, TextAreaField, BooleanField, DateTimeLocalField, HiddenField, StringField, SelectMultipleField, EmailField, TelField, IntegerField
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, InputRequired, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget

# Validador reutilizable: asegura que el SelectField no quede en "-- Seleccione --"
def seleccion_valida(form, field):
    from wtforms.validators import ValidationError
    if not field.data or int(field.data) == 0:
        raise ValidationError("Debe seleccionar una opción válida.")

    
# ====================================================================================================================================================
#                                           PAGINA TICKET_PANEL.HTML
# ====================================================================================================================================================

# Cambio de estado del ticket
class FormCambiarEstado(FlaskForm):
    """Permite al técnico cambiar el estado del ticket"""
    estado = SelectField(
        "Estado",
        validators=[DataRequired(message="Debe seleccionar un estado."), seleccion_valida],
        coerce=int,
        choices=[],  # se carga en el servicio
    )

    fecha_cierre = DateTimeLocalField(
        "Fecha de Cierre",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
    )

    resolucion = TextAreaField(
        "Resolución",
        validators=[
            DataRequired(message="La resolución es obligatoria."),
            Length(min=5, max=2000, message="La resolución debe tener entre 5 y 2000 caracteres."),
        ],
        render_kw={"rows": 3},
    )


# Agregar comentario al ticket
class FormAgregarComentario(FlaskForm):
    """Permite al técnico agregar un comentario al ticket"""
    comentario = TextAreaField(
        "Comentario",
        validators=[
            DataRequired(message="El comentario no puede estar vacío."),
            Length(min=3, max=3000, message="El comentario debe tener entre 3 y 3000 caracteres."),
        ],
        render_kw={"rows": 3, "placeholder": "Escribe tu comentario aquí…"},
    )

    es_interno = BooleanField(
        "Interno",
        default=False,
    )


class FormConfirmarCupo(FlaskForm):
    """Formulario vacío: solo sirve para validar el token CSRF"""
    pass
    
# Subir documento
class FormSubirDocumentoTecnico(FlaskForm):
    """Formulario para subir documentos adicionales al ticket desde el rol técnico"""

    tipo_documento = SelectField(
        "Tipo de Documento",
        validators=[DataRequired(), seleccion_valida],
        coerce=int,
        choices=[],  # se carga en el servicio
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
#                                           PAGINA ACCOUNTS.HTML
# ====================================================================================================================================================

class FormToggleEstado(FlaskForm):
    """Form para cambiar estado de usuario/estudiante/técnico via POST"""
    nuevo_estado = HiddenField("nuevo_estado", validators=[DataRequired()])
    
    
    
# ====================================================================================================================================================
#                                           PAGINA SCHOOL_STATUS.HTML
# ====================================================================================================================================================


# Widget para múltiple selección con checkboxes
class MultiCheckboxField(SelectMultipleField):
    """SelectMultipleField renderizado como checkboxes individuales"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


# Filtro de la tabla

class FormFiltroColegios(FlaskForm):
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

class FormAgregarColegio(FlaskForm):
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

class FormEditarColegio(FlaskForm):
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


class FormPrioridadAfectacion(FlaskForm):
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


class FormPrioridadGrupo(FlaskForm):
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


class FormPrioridadEstrato(FlaskForm):
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