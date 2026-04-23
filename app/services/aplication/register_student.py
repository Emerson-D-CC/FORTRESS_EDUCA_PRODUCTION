# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session

# UTILIDADES
from app.utils.database_utils import db

# CONFIGURACIONES LOCALES
from app.forms.aplication_forms import *
from app.repositories.aplication_repository import *

# ====================================================================================================================================================
#                                           PAGINA REGISTER_STUDENT.HTML
# ====================================================================================================================================================

def _form_opciones_estudiante_register(form):
    """Asigna choices a todos los SelectFields del formulario del estudiante"""
    
    generos = sp_obtener_generos()
    grupos_preferenciales = sp_obtener_grupos_preferenciales()
    grados = sp_obtener_grados()
    colegios = sp_obtener_colegios()
    tipos_identificacion  = sp_obtener_tipos_identificacion()
    parentesco_estudiante = sp_obtener_parentesco_est()

    form.tipo_identificacion.choices = (
        [(0, "— Seleccione una Identificación —")] +
        [(t["ID_Tipo_Iden"], t["Nombre_Tipo_Iden"]) for t in tipos_identificacion]
    )
    form.genero.choices = (
        [(0, "— Seleccione un Género —")] +
        [(g["ID_Genero"], g["Nombre_Genero"]) for g in generos]
    )
    form.grupo_preferencial.choices = (
        [(0, "— Seleccione un Grupo —")] +
        [(gp["ID_Grupo_Preferencial"], gp["Nombre_Grupo_Preferencial"]) for gp in grupos_preferenciales]
    )
    form.grado_actual.choices = (
        [(0, "— Seleccione un grado —")] +
        [(gr["ID_Grado"], gr["Nombre_Grado"]) for gr in grados]
    )
    form.grado_proximo.choices = (
        [(0, "— Seleccione un grado —")] +
        [(gr["ID_Grado"], gr["Nombre_Grado"]) for gr in grados]
    )
    form.colegio_anterior.choices = (
        [(0, "— Seleccione un Colegio —")] +
        [(c["ID_Colegio"], c["Nombre_Colegio"]) for c in colegios]
    )
    form.parentesco.choices = (
        [(0, "— Seleccione un Parentesco —")] +
        [(p["ID_Parentesco"], p["Nombre_Parentesco"]) for p in parentesco_estudiante]
    )


# Campos SelectField que no pueden ser 0
_SELECTS_REQUERIDOS = [
    "tipo_identificacion", "genero", "grupo_preferencial",
    "grado_actual", "grado_proximo", "colegio_anterior", "parentesco"
]


class Register_Student_Service:
    """Gestiona el proceso para el registro de un nuevo estudiante"""

    def registrar(self):
        form = FormRegistroEstudiante()
        _form_opciones_estudiante_register(form)

        if request.method == "GET":
            return render_template(
                "aplication/register_student.html",
                form=form,
            )

        # POST

        # Validación de WTForms
        if not form.validate_on_submit():
            errores = "; ".join(
                f"{field}: {', '.join(msgs)}"
                for field, msgs in form.errors.items()
            )
            print(f"[FORM ERRORS] {errores}")
            flash("Por favor revise todos los campos del formulario.", "danger")
            return render_template(
                "aplication/register_student.html",
                form=form,
            )

        # verificar que ningún SelectField llegó como 0
        campos_invalidos = [
            campo for campo in _SELECTS_REQUERIDOS
            if getattr(form, campo).data == 0
        ]
        
        if campos_invalidos:
            flash("Hay campos de selección sin completar. Por favor revise el formulario.", "danger")
            return render_template(
                "aplication/register_student.html",
                form=form,
            )

        # Datos seguros, proceder con BD
        user_id = session["user_id"]
        ip  = request.remote_addr
        user_agent = request.headers.get("User-Agent")

        try:
            # Verificar duplicado
            estudiante_existente = sp_estudiante_existe(
                form.numero_documento.data, user_id
            )
            if estudiante_existente:
                flash("Este estudiante ya se encuentra registrado.", "warning")
                return render_template(
                    "aplication/register_student.html",
                    form=form,
                )

            sp_registrar_estudiante((
                # TBL_PERSONA
                form.numero_documento.data,
                form.primer_nombre.data,
                form.segundo_nombre.data or None,
                form.primer_apellido.data,
                form.segundo_apellido.data or None,
                form.fecha_nacimiento.data,
                # TBL_ESTUDIANTE
                form.tipo_identificacion.data,
                form.grado_actual.data,
                form.grado_proximo.data,
                form.colegio_anterior.data,
                form.genero.data,
                form.grupo_preferencial.data,
                user_id,
                form.parentesco.data,
                # Auditoría
                ip,
                user_agent,
            ))

            db.commit()
            session["estudiante_verificado"] = True
            flash("Estudiante registrado correctamente.", "success")
            return redirect(url_for("aplication.profile"))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Registro de estudiante fallido: {e}")
            session["estudiante_verificado"] = False
            flash("Ocurrió un error al registrar al estudiante. Intente nuevamente.", "danger")
            return render_template(
                "aplication/register_student.html",
                form=form,
            )