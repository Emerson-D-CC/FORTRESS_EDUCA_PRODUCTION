from flask import request, render_template, redirect, url_for, flash
from app.repositories.admin_repository import sp_admin_metricas_funcionarios, sp_admin_tecnicos_listar, sp_admin_administradores_listar, sp_admin_toggle_estado_tecnico

from app.forms.admin_forms import FormToggleEstado


class Accounts_Func_Service:
    """Lógica de negocio para accounts_func.html (técnicos y admins)."""

    @staticmethod
    def _int_or_none(value):
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    # Vista principal
    # ------------------------------------------------------------------
    def listar_funcionarios(self):
        
        form_toggle = FormToggleEstado()
        
        filtros = {
            "estado": self._int_or_none(request.args.get("estado")),
        }
        datos_metricas = sp_admin_metricas_funcionarios()
        datos_tecnicos = sp_admin_tecnicos_listar(estado=filtros["estado"])
        datos_admins = sp_admin_administradores_listar()
        
        return render_template(
            "admin/accounts_func.html",
            active_page="staff",
            form_toggle = form_toggle,            
            metricas=datos_metricas,
            tecnicos=datos_tecnicos,
            admins=datos_admins,
            filtros=filtros,
            tab_activo=request.args.get("tab", "funcionarios"),
        )

    # ------------------------------------------------------------------
    # Toggle estado técnico (POST)
    # ------------------------------------------------------------------
    def toggle_estado_tecnico(self, id_usuario: int):
        nuevo_estado = self._int_or_none(request.form.get("nuevo_estado"))
        if nuevo_estado not in (0, 1):
            flash("Estado inválido.", "danger")
            return redirect(url_for("admin.accounts_func"))

        ejecutor_id = 1  # TODO: reemplazar con current_user.ID_Usuario
        ip = request.remote_addr
        user_agent = request.user_agent.string

        sp_admin_toggle_estado_tecnico(id_usuario, nuevo_estado, ejecutor_id, ip, user_agent)

        accion = "activado" if nuevo_estado == 1 else "desactivado"
        flash(f"Técnico TEC-{id_usuario} {accion} correctamente.", "success")
        return redirect(url_for("admin.accounts_func", tab="funcionarios"))