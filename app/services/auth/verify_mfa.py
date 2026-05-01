# FUNCIONES DE FLASK
# FUNCIONES DE FLASK
from flask import request, redirect, url_for, flash, session

# CONFIGURACIONES LOCALES
from app.forms.auth_forms import FormVerificarMFA
from app.repositories.auth_repository import sp_obtener_mfa_secret, sp_obtener_roles

# UTILIDADES
from app.utils.audit_utils import Auditoria_Session
from app.utils.response_utils import render_no_cache

# SEGURIDAD
from app.security.mfa_controller import MFA_Controller


# Whitelist de destinos válidos por rol.
_DESTINOS_PERMITIDOS = {
    "Acudiente": "aplication.dashboard",
    "Admin": "admin.dashboard",
    "Tecnico": "technical.dashboard",
}

# ====================================================================================================================================================
#                                           PAGINA VERIFY_MFA.HTML
# ====================================================================================================================================================

class Verify_MFA_Service:

    def Verify_MFA(self):
        """Valida el código TOTP durante el login para usuarios con 2FA activo"""

        login_url = session.get("mfa_login_url", url_for("auth.login_user"))

        # Guard: sesión MFA válida
        if not session.get("mfa_pendiente") or not session.get("mfa_user_autenticado"):
            session.pop("mfa_pendiente", None)
            session.pop("mfa_user_autenticado", None)
            session.pop("mfa_rol_esperado", None)
            return redirect(login_url, 303)

        # Validar que el rol en sesión coincide con el rol esperado
        rol_esperado = session.get("mfa_rol_esperado")
        role_id = session.get("role_id")

        if not self._validar_rol_vs_esperado(rol_esperado, role_id):
            # Posible manipulación de sesión: destruir todo y forzar login
            Auditoria_Session(
                session.get("user_id", 2),
                request.remote_addr,
                "INVALID_MFA_ROLE",
                request.headers.get("User-Agent", "")
            )
            session.clear()
            return redirect(url_for("auth.login_user"), 303)

        # Obtener destino desde whitelist (ignora el valor de sesión)
        endpoint_destino = _DESTINOS_PERMITIDOS.get(rol_esperado)
        if not endpoint_destino:
            session.clear()
            return redirect(url_for("auth.login_user"), 303)

        success_url = url_for(endpoint_destino)

        form = FormVerificarMFA()

        # =====================================================
        # SOLICITUD POST
        if request.method == "POST" and form.validate_on_submit():
            id_usuario = session.get("user_id")
            ip = request.remote_addr
            user_agent = request.headers.get("User-Agent", "")

            try:
                data = sp_obtener_mfa_secret(id_usuario)
                if not data:
                    flash("Error de sesión. Inicie sesión nuevamente.", "danger")
                    return redirect(login_url, 303)

                row = data[0]
                secret = row.get("MFA_Secret") or row.get("mfa_secret")
                if isinstance(secret, (bytes, bytearray)):
                    secret = secret.decode("utf-8")

                if not secret or not MFA_Controller.verificar_codigo(
                    secret, form.codigo_mfa.data.strip()
                ):
                    Auditoria_Session(id_usuario, ip, "FAILED_MFA", user_agent)
                    flash("Código incorrecto. Intente de nuevo.", "danger")
                    return render_no_cache("auth/verify_mfa.html", form=form)

                # MFA válido: limpiar banderas y redirigir
                session.pop("mfa_pendiente", None)
                session.pop("mfa_user_autenticado", None)
                session.pop("mfa_rol_esperado", None)
                session.pop("mfa_login_url", None)
                session.pop("mfa_success_url", None)

                Auditoria_Session(id_usuario, ip, "LOGIN_MFA", user_agent)
                return redirect(success_url, 303)

            except Exception as e:
                print(f"[ERROR] VerificarMFA.verificar: {e}")
                flash("Error interno. Intente nuevamente.", "danger")

        
        # =====================================================
        # SOLICITUD GET
        return render_no_cache("auth/verify_mfa.html", form=form)

    # Método privado

    def _validar_rol_vs_esperado(self, rol_esperado: str, role_id) -> bool:
        """Compara el role_id real de la sesión contra el rol que el login declaró como esperado"""
        try:
            if not rol_esperado or role_id is None:
                return False
            # Solo aceptamos roles contemplados en la whitelist
            if rol_esperado not in _DESTINOS_PERMITIDOS:
                return False

            id_rol_bd = sp_obtener_roles(rol_esperado)
            return id_rol_bd == role_id

        except Exception as e:
            print(f"[ERROR] _validar_rol_vs_esperado: {e}")
            return False