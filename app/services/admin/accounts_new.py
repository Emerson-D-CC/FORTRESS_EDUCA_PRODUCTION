from datetime import date, timedelta

from flask import render_template, request, redirect, url_for, flash, session, make_response

from app.forms.admin_forms import CreateUsuarioForm, CreateEstudianteForm
from app.repositories.admin_repository import (
    sp_obtener_tipos_documento_admin,
    sp_obtener_tipos_documento_est,
    sp_obtener_parentesco_admin,
    sp_obtener_parentesco_est,    
    sp_obtener_barrios_admin,
    sp_obtener_grados,
    sp_obtener_colegios,
    sp_obtener_generos,
    sp_obtener_grupos_preferenciales,
    sp_obtener_acudientes_activos,
    sp_verificar_usuario_admin,
    sp_verificar_estudiante_admin,
    sp_registrar_usuario_admin,
    sp_registrar_estudiante_admin,
)

from app.utils.password_utils import hashear_contraseña
from app.utils.database_utils import db

# ====================================================================================================================================================

# Mapeo de form_type → ID_Rol en TBL_ROL
_ROL_MAP = {
    "acudiente": 2,
    "tecnico": 3,
    "admin": 4,
}

# Etiquetas para mensajes flash
_ROL_LABEL = {
    "acudiente": "Acudiente",
    "tecnico": "Técnico",
    "admin": "Administrador",
}

# ID de parentesco usado como placeholder para Técnico y Admin (N/A).
# Ajusta al ID real de tu TBL_PARENTESCO que represente "No Aplica".
_PARENTESCO_DEFAULT = 1

# Claves de sesión con prefijo propio para no colisionar con otras vistas
_SK_TAB = "new_tab_activo"
_SK_DATA = "new_form_data"
_SK_ERRORS = "new_form_errors"
_SK_MSG = "new_flash_message"
_SK_CAT = "new_flash_category"


# ====================================================================================================================================================

class AdminCreateService:

    # Fechas límite 
    @staticmethod
    def _fechas_adulto():
        hoy = date.today()
        return (
            hoy.replace(year=hoy.year - 100),   # fecha_min
            hoy - timedelta(days=1),             # fecha_max
        )

    @staticmethod
    def _fechas_estudiante():
        hoy = date.today()
        return (
            hoy.replace(year=hoy.year - 25),     # fecha_min (25 años)
            hoy.replace(year=hoy.year - 3),      # fecha_max (mínimo 3 años)
        )

    # Poblar SelectFields

    def _poblar_usuario(self, form: CreateUsuarioForm):
        try:
            tipos = sp_obtener_tipos_documento_admin()
            parent = sp_obtener_parentesco_admin()
            barrios = sp_obtener_barrios_admin()

            form.tipo_documento.choices = (
                [(0, "— Seleccione un tipo —")] +
                [(d["ID_Tipo_Iden"], d["Nombre_Tipo_Iden"]) for d in tipos]
            )
            form.parentesco.choices = (
                [(0, "— Seleccione un parentesco —")] +
                [(p["ID_Parentesco"], p["Nombre_Parentesco"]) for p in parent]
            )
            form.barrio.choices = (
                [(0, "— Seleccione un barrio —")] +
                [(b["ID_Barrio"], b["Nombre_Barrio"]) for b in barrios]
            )
        except Exception as exc:
            print(f"[ERROR] _poblar_usuario: {exc}")
            flash("Error al cargar opciones del formulario de usuario.", "danger")

    def _poblar_estudiante(self, form: CreateEstudianteForm):
        try:
            tipos = sp_obtener_tipos_documento_est()
            grados = sp_obtener_grados()
            colegios = sp_obtener_colegios()
            generos = sp_obtener_generos()
            grupos = sp_obtener_grupos_preferenciales()
            acud = sp_obtener_acudientes_activos()
            parent = sp_obtener_parentesco_est()

            form.tipo_documento.choices = (
                [(0, "— Seleccione —")] +
                [(d["ID_Tipo_Iden"], d["Nombre_Tipo_Iden"]) for d in tipos]
            )
            form.grado_actual.choices = (
                [(0, "— Seleccione —")] +
                [(g["ID_Grado"], g["Nombre_Grado"]) for g in grados]
            )
            form.grado_proximo.choices = (
                [(0, "— Ninguno / No aplica —")] +
                [(g["ID_Grado"], g["Nombre_Grado"]) for g in grados]
            )
            form.colegio_anterior.choices = (
                [(0, "— Seleccione —")] +
                [(c["ID_Colegio"], c["Nombre_Colegio"]) for c in colegios]
            )
            form.genero.choices = (
                [(0, "— Seleccione —")] +
                [(g["ID_Genero"], g["Nombre_Genero"]) for g in generos]
            )
            form.grupo_preferencial.choices = (
                [(0, "— Seleccione —")] +
                [(g["ID_Grupo_Preferencial"], g["Nombre_Grupo_Preferencial"]) for g in grupos]
            )
            form.acudiente.choices = (
                [(0, "— Seleccione un acudiente —")] +
                [(a["ID_Usuario"], f"{a['Nombre_Completo']} — {a['Num_Doc_Persona']}") for a in acud]
            )
            form.parentesco_estudiante.choices = (
                [(0, "— Seleccione —")] +
                [(p["ID_Parentesco"], p["Nombre_Parentesco"]) for p in parent]
            )
        except Exception as exc:
            print(f"[ERROR] _poblar_estudiante: {exc}")
            flash("Error al cargar opciones del formulario de estudiante.", "danger")

    # Restaurar datos de sesión en el formulario activo

    def _restaurar_sesion(self, form_usuario: CreateUsuarioForm, form_estudiante: CreateEstudianteForm, tab_activo: str):
        if _SK_ERRORS not in session:
            return

        form_data = session.pop(_SK_DATA, {})
        form_errors = session.pop(_SK_ERRORS, {})
        target_form = form_estudiante if tab_activo == "estudiante" else form_usuario

        for field_name, value in form_data.items():
            if hasattr(target_form, field_name):
                getattr(target_form, field_name).data = value

        for field_name, errors in form_errors.items():
            if hasattr(target_form, field_name):
                getattr(target_form, field_name).errors = errors

        if _SK_MSG in session:
            flash(session.pop(_SK_MSG), session.pop(_SK_CAT, "danger"))

    # Helpers de sesión

    @staticmethod
    def _set_session_error(tab: str, form_data: dict, form_errors: dict, mensaje: str, categoria: str = "danger"):
        session[_SK_TAB] = tab
        session[_SK_DATA] = form_data
        session[_SK_ERRORS] = form_errors
        session[_SK_MSG] = mensaje
        session[_SK_CAT] = categoria

    @staticmethod
    def _clear_session():
        for key in (_SK_TAB, _SK_DATA, _SK_ERRORS, _SK_MSG, _SK_CAT):
            session.pop(key, None)

    # Render

    def _render(self, form_usuario, form_estudiante, tab_activo):
        f_min_adulto, f_max_adulto = self._fechas_adulto()
        f_min_est, f_max_est = self._fechas_estudiante()

        response = make_response(render_template(
            "admin/accounts_new.html",
            form_usuario=form_usuario,
            form_estudiante=form_estudiante,
            tab_activo=tab_activo,
            fecha_min_adulto=f_min_adulto,
            fecha_max_adulto=f_max_adulto,
            fecha_min_est=f_min_est,
            fecha_max_est=f_max_est,
            active_page = "new_user",            
        ))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Punto de entrada principal

    def Accounts_New(self):
        form_usuario = CreateUsuarioForm()
        form_estudiante = CreateEstudianteForm()

        self._poblar_usuario(form_usuario)
        self._poblar_estudiante(form_estudiante)

        if request.method == "GET":
            tab_activo = session.pop(_SK_TAB, "acudiente")
            self._restaurar_sesion(form_usuario, form_estudiante, tab_activo)
            return self._render(form_usuario, form_estudiante, tab_activo)

        # POST
        form_type = request.form.get("form_type", "acudiente")

        if form_type == "estudiante":
            return self._procesar_estudiante(form_estudiante)

        return self._procesar_usuario(form_usuario, form_type)

    # Procesamiento: Usuario (Acudiente / Técnico / Admin

    def _procesar_usuario(self, form: CreateUsuarioForm, form_type: str):
        if form_type not in _ROL_MAP:
            flash("Tipo de usuario no reconocido.", "danger")
            return redirect(url_for("admin.accounts_new"))

        if not form.validate_on_submit():
            print(f"[VALIDACIÓN] accounts_new ({form_type}): " +
                  "; ".join(f"{k}: {v}" for k, v in form.errors.items()))
            self._set_session_error(
                form_type,
                request.form.to_dict(),
                form.errors,
                "Revise los campos marcados en el formulario.",
            )
            return redirect(url_for("admin.accounts_new"))

        # Verificar duplicado
        try:
            if sp_verificar_usuario_admin(form.email.data, form.documento.data):
                self._set_session_error(
                    form_type,
                    request.form.to_dict(),
                    {},
                    "El documento o correo ya está registrado en el sistema.",
                    "warning",
                )
                return redirect(url_for("admin.accounts_new"))
        except Exception as exc:
            print(f"[ERROR] sp_verificar_usuario_admin: {exc}")
            self._set_session_error(form_type, request.form.to_dict(), {},
                                    "Error al verificar el usuario. Intente nuevamente.")
            return redirect(url_for("admin.accounts_new"))

        # Parentesco: requerido para Acudiente, placeholder para Técnico/Admin
        id_parentesco = (
            int(form.parentesco.data)
            if form_type == "acudiente"
            else _PARENTESCO_DEFAULT
        )

        try:
            hash_pwd = hashear_contraseña(form.password.data)
            ip = request.remote_addr
            user_agent = request.headers.get("User-Agent", "")
            id_admin = session.get("id_usuario", 1)

            sp_registrar_usuario_admin((
                form.documento.data.strip(),
                form.primer_nombre.data.strip(),
                form.segundo_nombre.data.strip() if form.segundo_nombre.data else None,
                form.primer_apellido.data.strip(),
                form.segundo_apellido.data.strip() if form.segundo_apellido.data else None,
                form.fecha_nacimiento.data,
                form.email.data.lower().strip(),
                form.telefono.data.strip(),
                id_parentesco,
                int(form.tipo_documento.data),
                1, # FK_ID_Genero  (default — no capturado en este form)
                1, # FK_ID_Grupo_Preferencial (default)
                1, # FK_ID_Estrato (default)
                int(form.barrio.data),
                form.email.data.lower().strip(),
                hash_pwd,
                _ROL_MAP[form_type],
                ip,
                user_agent,
                id_admin,
            ))
            db.commit()

        except Exception as exc:
            db.rollback()
            print(f"[ERROR] sp_registrar_usuario_admin: {exc}")
            self._set_session_error(form_type, request.form.to_dict(), {},
                                    "Error al crear la cuenta. Intente nuevamente o contacte al administrador.")
            return redirect(url_for("admin.accounts_new"))

        self._clear_session()
        flash(f"{_ROL_LABEL[form_type]} registrado correctamente.", "success")
        return redirect(url_for("admin.accounts_new"))

    # Procesamiento: Estudiante

    def _procesar_estudiante(self, form: CreateEstudianteForm):
        if not form.validate_on_submit():
            print(f"[VALIDACIÓN] accounts_new (estudiante): " +
                  "; ".join(f"{k}: {v}" for k, v in form.errors.items()))
            self._set_session_error(
                "estudiante",
                request.form.to_dict(),
                form.errors,
                "Revise los campos marcados en el formulario.",
            )
            return redirect(url_for("admin.accounts_new"))

        # Verificar duplicado
        try:
            if sp_verificar_estudiante_admin(form.documento.data):
                self._set_session_error(
                    "estudiante",
                    request.form.to_dict(),
                    {},
                    "Ya existe un estudiante registrado con ese documento.",
                    "warning",
                )
                return redirect(url_for("admin.accounts_new"))
        except Exception as exc:
            print(f"[ERROR] sp_verificar_estudiante_admin: {exc}")
            self._set_session_error("estudiante", request.form.to_dict(), {},
                                    "Error al verificar el estudiante. Intente nuevamente.")
            return redirect(url_for("admin.accounts_new"))

        try:
            ip = request.remote_addr
            user_agent = request.headers.get("User-Agent", "")
            id_admin = session.get("id_usuario", 1)

            # Grado próximo: 0 → None (nullable en TBL_ESTUDIANTE)
            grado_prox = (
                int(form.grado_proximo.data)
                if form.grado_proximo.data and str(form.grado_proximo.data) != "0"
                else 0   # el SP aplica NULLIF(val, 0)
            )

            sp_registrar_estudiante_admin((
                form.documento.data.strip(),
                form.primer_nombre.data.strip(),
                form.segundo_nombre.data.strip() if form.segundo_nombre.data else None,
                form.primer_apellido.data.strip(),
                form.segundo_apellido.data.strip() if form.segundo_apellido.data else None,
                form.fecha_nacimiento.data,
                int(form.tipo_documento.data),
                int(form.grado_actual.data),
                grado_prox,
                int(form.colegio_anterior.data),
                int(form.genero.data),
                int(form.grupo_preferencial.data),
                int(form.acudiente.data),
                int(form.parentesco_estudiante.data),
                ip,
                user_agent,
                id_admin,
            ))
            db.commit()

        except Exception as exc:
            db.rollback()
            print(f"[ERROR] sp_registrar_estudiante_admin: {exc}")
            self._set_session_error("estudiante", request.form.to_dict(), {},
                                    "Error al registrar el estudiante. Intente nuevamente.")
            return redirect(url_for("admin.accounts_new"))

        self._clear_session()
        flash("Estudiante registrado correctamente.", "success")
        return redirect(url_for("admin.accounts_new"))