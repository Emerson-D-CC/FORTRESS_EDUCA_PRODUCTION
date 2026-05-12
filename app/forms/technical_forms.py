# FUNCIONES DE FLASK
from flask_wtf import FlaskForm

from wtforms import SelectField, PasswordField, StringField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, ValidationError

# UTILIDADES
from app.utils.validation_utils import regex
# SECURIDAD
from app.security.forms_controller import SanitizedForm

# ====================================================================================================================================================
#                                           PAGINA CASES.HTML
# ====================================================================================================================================================

class FormFiltroTicketsTecnico(FlaskForm):
    """Filtros GET para technical_cases.html"""

    class Meta:
        csrf = False # Formulario GET de solo lectura

    busqueda = StringField(
        "Buscar",
        validators=[Optional(), Length(max=100)],
        render_kw={
            "placeholder": "ID, estudiante, acudiente, colegio…",
            "autocomplete": "off",
        },
    )

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
#                                           PAGINA SECURITY.HTML
# ====================================================================================================================================================

class FormCambiarcontraseña(SanitizedForm):
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