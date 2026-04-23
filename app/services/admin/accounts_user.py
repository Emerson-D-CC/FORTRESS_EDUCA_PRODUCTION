from flask import request, render_template, redirect, url_for, flash
from app.repositories.admin_repository import (
    sp_admin_metricas_usuarios, 
    sp_admin_acudientes_listar, 
    sp_admin_estudiantes_listar, 
    sp_admin_toggle_estado_usuario, 
    sp_admin_toggle_estado_estudiante
)
from app.forms.admin_forms import FormToggleEstado

class Accounts_User_Service:
    """Lógica de negocio para accounts_user.html (acudientes y estudiantes)."""


    @staticmethod
    def _int_or_none(value):
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    # Vista principal
    # ------------------------------------------------------------------
    

    def listar_usuarios(self):
        form_toggle = FormToggleEstado()
        
        datos_metricas = sp_admin_metricas_usuarios()
        datos_acudientes = sp_admin_acudientes_listar()
        datos_estudiantes = sp_admin_estudiantes_listar()
    
        return render_template(
            "admin/accounts_user.html",
            active_page="users",
            form_toggle = form_toggle,
            metricas=datos_metricas,
            acudientes=datos_acudientes,
            estudiantes=datos_estudiantes,
            tab_activo=request.args.get("tab", "acudientes"),
        )

    # ------------------------------------------------------------------
    # Toggle estado acudiente (POST)
    # ------------------------------------------------------------------
    def toggle_estado_usuario(self, id_usuario: int):
        nuevo_estado = self._int_or_none(request.form.get("nuevo_estado"))
        if nuevo_estado not in (0, 1):
            flash("Estado inválido.", "danger")
            return redirect(url_for("admin.accounts_user"))

        ejecutor_id = 1
        ip = request.remote_addr
        user_agent = request.user_agent.string

        sp_admin_toggle_estado_usuario(id_usuario, nuevo_estado, ejecutor_id, ip, user_agent)

        accion = "activado" if nuevo_estado == 1 else "desactivado"
        flash(f"Usuario ACU-{id_usuario} {accion} correctamente.", "success")
        
        return redirect(url_for("admin.accounts_user", tab="acudientes"))

    # ------------------------------------------------------------------
    # Toggle estado estudiante (POST)
    # ------------------------------------------------------------------
    def toggle_estado_estudiante(self, id_estudiante: int):
        nuevo_estado = self._int_or_none(request.form.get("nuevo_estado"))
        if nuevo_estado not in (0, 1):
            flash("Estado inválido.", "danger")
            return redirect(url_for("admin.accounts_user"))

        ejecutor_id = 1  # TODO: reemplazar con current_user.ID_Usuario
        ip = request.remote_addr
        user_agent = request.user_agent.string

        sp_admin_toggle_estado_estudiante(id_estudiante, nuevo_estado, ejecutor_id, ip, user_agent)

        accion = "activado" if nuevo_estado == 1 else "eliminado"
        flash(f"Estudiante EST-{id_estudiante} {accion} correctamente.", "success")
        return redirect(url_for("admin.accounts_user", tab="estudiantes"))