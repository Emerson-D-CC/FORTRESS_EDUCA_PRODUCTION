# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session

# UTILIDADES
from app.utils.database_utils import db

# CONFIGURACIONES LOCALES
from app.repositories.aplication_repository import (
    sp_obtener_perfil_acudiente,
    sp_obtener_estudiantes_por_acudiente,
    sp_obtener_estratos,
    sp_obtener_generos,
    sp_obtener_grupos_preferenciales,
    sp_obtener_barrios,
    sp_obtener_grados,
    sp_obtener_colegios,
    sp_actualizar_datos_adicionales,
    sp_actualizar_persona,
    sp_actualizar_estudiante,
    sp_verificar_estudiante_acudiente,
    sp_obtener_estudiante_por_id,
)
        
from app.forms.aplication_forms import FormAcudienteDatosEditables, FormEstudianteDatosEditables

# ====================================================================================================================================================
#                                           PAGINA PROFILE.HTML
# ====================================================================================================================================================

def _form_opciones_acudiente(form):
    """Asigna choices a los SelectFields del formulario del acudiente"""
    form.estrato.choices = (
        [(0, "— Seleccione un Estrato —")] +
        [(e["ID_Estrato"], e["Nombre_Estrato"]) for e in sp_obtener_estratos()]
    )
    form.genero.choices = (
        [(0, "— Seleccione un Género —")] +
        [(g["ID_Genero"], g["Nombre_Genero"]) for g in sp_obtener_generos()]
    )
    form.grupo_preferencial.choices = (
        [(0, "— Seleccione un Grupo —")] +
        [(gp["ID_Grupo_Preferencial"], gp["Nombre_Grupo_Preferencial"]) for gp in sp_obtener_grupos_preferenciales()]
    )
    form.barrio.choices = (
        [(0, "— Seleccione un Barrio —")] +
        [(b["ID_Barrio"], b["Nombre_Barrio"]) for b in sp_obtener_barrios()]
    )


def _form_opciones_estudiante(form):
    """Asigna choices a todos los SelectFields del formulario del estudiante"""
    form.genero.choices = (
        [(0, "— Seleccione un Género —")] +
        [(g["ID_Genero"], g["Nombre_Genero"]) for g in sp_obtener_generos()]
    )
    form.grupo_preferencial.choices = (
        [(0, "— Seleccione un Grupo —")] +
        [(gp["ID_Grupo_Preferencial"], gp["Nombre_Grupo_Preferencial"]) for gp in sp_obtener_grupos_preferenciales()]
    )
    form.grado_actual.choices = (
        [(0, "— Seleccione un grado —")] +
        [(gr["ID_Grado"], gr["Nombre_Grado"]) for gr in sp_obtener_grados()]
    )
    form.grado_proximo.choices = (
        [(0, "— Seleccione un grado —")] +
        [(gr["ID_Grado"], gr["Nombre_Grado"]) for gr in sp_obtener_grados()]
    )
    form.colegio_anterior.choices = (
        [(0, "— Seleccione un Colegio —")] +
        [(c["ID_Colegio"], c["Nombre_Colegio"]) for c in sp_obtener_colegios()]
    )


class Profile_Data_Service:

    def cargar_datos_perfil(self):
        user_id = session.get("user_id")
        if not user_id:
            flash("No se encontró sesión de usuario activa.", "danger")
            return redirect(url_for("aplication.dashboard"))

        verificacion = sp_verificar_estudiante_acudiente(user_id)
        if not verificacion or verificacion.get("total_estudiantes", 0) == 0:
            flash("Debes registrar al menos un estudiante para continuar.", "info")
            return redirect(url_for("aplication.register_student"))

        form_acu_edit = FormAcudienteDatosEditables()
        form_est = FormEstudianteDatosEditables()
        _form_opciones_acudiente(form_acu_edit)
        _form_opciones_estudiante(form_est)

        # Determinar tab activo
        # Por defecto: acudiente. Si viene ?tab=menor o hay ?estudiante=X = menor.
        id_param  = request.args.get("estudiante", type=int)
        tab_param = request.args.get("tab", "")
        active_tab = "menor" if (tab_param == "menor" or id_param) else "acudiente"

        # POST
        if request.method == "POST":
            form_type = request.form.get("form_type", "").strip().lower()
            if form_type == "acudiente":
                if self._actualizar_acudiente(form_acu_edit):
                    return redirect(url_for("aplication.profile", tab="acudiente"))
                active_tab = "acudiente"
            elif form_type == "estudiante":
                # Recuperar el estudiante que se estaba editando para volver a él
                id_est_post = request.form.get("id_estudiante", type=int)
                if self._actualizar_estudiante(form_est):
                    return redirect(url_for(
                        "aplication.profile",
                        tab="menor",
                        estudiante=id_est_post
                    ))
                active_tab = "menor"
            else:
                flash("Tipo de formulario no reconocido.", "danger")

        # Datos desde BD
        datos_acu_fijos = sp_obtener_perfil_acudiente(user_id)
        datos_acu = sp_obtener_perfil_acudiente(user_id)
        lista_est = sp_obtener_estudiantes_por_acudiente(user_id)

        # Pre-poblar acudiente (solo GET)
        if datos_acu and request.method == "GET":
            form_acu_edit.telefono.data = datos_acu.get("Telefono")
            form_acu_edit.barrio.data = datos_acu.get("ID_Barrio", 0)
            form_acu_edit.genero.data = datos_acu.get("ID_Genero", 0)
            form_acu_edit.grupo_preferencial.data = datos_acu.get("ID_Grupo_Preferencial", 0)
            form_acu_edit.estrato.data = datos_acu.get("ID_Estrato", 0)

        # Estudiante activo
        estudiante_activo = None
        if lista_est:
            if id_param:
                estudiante_activo = next(
                    (e for e in lista_est if e["ID_Estudiante"] == id_param),
                    lista_est[0]
                )
            else:
                estudiante_activo = lista_est[0]

            # Asingar datos del estudiante para los campos del formulario
            if request.method == "GET" and estudiante_activo:
                form_est.id_estudiante.data = estudiante_activo["ID_Estudiante"]
                form_est.primer_nombre.data = estudiante_activo.get("Primer_Nombre")
                form_est.segundo_nombre.data = estudiante_activo.get("Segundo_Nombre")
                form_est.primer_apellido.data = estudiante_activo.get("Primer_Apellido")
                form_est.segundo_apellido.data = estudiante_activo.get("Segundo_Apellido")
                form_est.fecha_nacimiento.data = estudiante_activo.get("Fecha_Nacimiento")
                form_est.genero.data = estudiante_activo.get("ID_Genero", 0)
                form_est.grupo_preferencial.data = estudiante_activo.get("ID_Grupo_Preferencial", 0)
                form_est.grado_actual.data = estudiante_activo.get("ID_Grado_Actual", 0)
                form_est.grado_proximo.data = estudiante_activo.get("ID_Grado_Proximo", 0)
                form_est.colegio_anterior.data = estudiante_activo.get("ID_Colegio_Anterior", 0)

        return render_template(
            "aplication/profile.html",
            form_acu=form_acu_edit,
            form_est=form_est,
            datos_acu_fijos=datos_acu_fijos,
            datos_acu=datos_acu,
            lista_est=lista_est,
            estudiante_activo=estudiante_activo,
            active_tab=active_tab,
            active_page="profile",
        )

    # Guardar datos del acudiente

    def _actualizar_acudiente(self, form):
        _form_opciones_acudiente(form)
        if not form.validate_on_submit():
            flash("Por favor revise los campos del formulario del acudiente.", "danger")
            return False

        user_id   = session.get("user_id")
        datos_acu = sp_obtener_perfil_acudiente(user_id)
        if not datos_acu:
            flash("No se encontró el perfil del acudiente.", "danger")
            return False

        try:
            sp_actualizar_datos_adicionales((
                datos_acu.get("ID_Datos_Adicionales"),
                form.telefono.data,
                datos_acu.get("ID_Persona"),
                form.genero.data,
                form.grupo_preferencial.data,
                form.estrato.data,
                form.barrio.data,
                user_id,
                request.remote_addr,
                request.headers.get("User-Agent"),
            ))
            db.commit()
            flash("Datos del acudiente actualizados correctamente.", "success")
            return True
        except Exception as e:
            db.rollback()
            flash("Error al guardar los cambios del acudiente.", "danger")
            return False

    # Guardar estudiante

    def _actualizar_estudiante(self, form):
        _form_opciones_estudiante(form)
        if not form.validate_on_submit():
            flash("Por favor revise los campos del formulario del menor.", "danger")
            return False

        user_id = session.get("user_id")
        id_estudiante = form.id_estudiante.data

        # Verificar que el estudiante pertenece al acudiente activo
        datos_est = sp_obtener_estudiante_por_id(id_estudiante, user_id)
        
        if not datos_est:
            flash("No se encontró el estudiante indicado.", "danger")
            return False

        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent")
        
        try:
            # 1. Actualizar TBL_PERSONA del menor
            sp_actualizar_persona((
                datos_est["ID_Persona"],
                form.primer_nombre.data,
                form.segundo_nombre.data or None,
                form.primer_apellido.data,
                form.segundo_apellido.data or None,
                form.fecha_nacimiento.data,
                user_id,
                ip,
                user_agent,
            ))

            # 2. Actualizar TBL_ESTUDIANTE
            sp_actualizar_estudiante((
                form.grado_actual.data,
                form.grado_proximo.data,
                form.colegio_anterior.data,
                form.genero.data,
                form.grupo_preferencial.data,
                datos_est["ID_Persona"],
                user_id,
                ip,
                user_agent,
            ))

            db.commit()
            flash("Datos del estudiante actualizados correctamente.", "success")
            return True
        except Exception as e:
            db.rollback()
            flash("Ocurrió un error al guardar los cambios del estudiante.", "danger")
            return False