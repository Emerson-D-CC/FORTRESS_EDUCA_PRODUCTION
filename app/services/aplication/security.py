from flask import render_template, request, redirect, url_for, flash, session

from app.utils.database_utils import db
from app.security.mfa_controller import MFA_Controller
from app.services.core.core_security import SharedSecurityService

from app.repositories.aplication_repository import (
    sp_obtener_mfa_secret,
    sp_guardar_mfa_secret_temp,
    sp_activar_mfa,
    sp_desactivar_mfa,
)

from app.forms.aplication_forms import FormCambiarcontraseña, FormVerificarMFA


class Security_Settings_Service:
    """Servicio de seguridad para Aplication (contraseña + sesiones + MFA)."""

    _ENDPOINT = "aplication.security"

    def __init__(self):
        self._shared = SharedSecurityService(self._ENDPOINT, FormCambiarcontraseña)

    #  Vista principal 

    def cargar_informacion_seguridad(self):
        form_password    = FormCambiarcontraseña()
        form_mfa_activar  = FormVerificarMFA()
        form_mfa_desactivar = FormVerificarMFA()
        sesiones = self._shared.listar_sesiones()

        return render_template(
            "aplication/security.html",
            form_password=form_password,
            form_mfa_activar=form_mfa_activar,
            form_mfa_desactivar=form_mfa_desactivar,
            sesiones=sesiones,
            active_page="security",
        )

    #  Contraseña 

    def Change_Password(self):
        return self._shared.change_password()

    #  Sesiones 

    def Session_Handler_Service(self):
        return self._shared.listar_sesiones()

    def cerrar_sesiones(self):
        return self._shared.cerrar_todas_sesiones()

    def cerrar_sesion(self, jti_sesion: str):
        return self._shared.cerrar_sesion(jti_sesion)

    #  MFA (exclusivo de Aplication) 

    def MFA_Activation(self):
        """Genera el QR y guarda el secret temporal en BD."""
        id_usuario = session.get("user_id")
        username   = session.get("username")

        try:
            data = sp_obtener_mfa_secret(id_usuario)
            row  = data[0] if data else {}

            secret_temp_existente = row.get("MFA_Secret_Temp")
            if isinstance(secret_temp_existente, (bytes, bytearray)):
                secret_temp_existente = secret_temp_existente.decode("utf-8")

            if secret_temp_existente and session.get("mfa_secret_temp") == secret_temp_existente:
                flash("Ya tiene un QR pendiente. Escanéelo e ingrese el código para confirmar.", "info")
                return redirect(url_for(self._ENDPOINT))

            secret  = MFA_Controller.generar_secret()
            uri     = MFA_Controller.generar_uri(secret, username)
            qr_b64  = MFA_Controller.generar_qr_base64(uri)

            sp_guardar_mfa_secret_temp(id_usuario, secret)
            db.commit()

            session["mfa_secret_temp"] = secret
            session["mfa_qr_temp"]     = f"data:image/png;base64,{qr_b64}"

            flash("QR generado. Escanéelo con Microsoft Authenticator e ingrese el código.", "info")
            return redirect(url_for(self._ENDPOINT))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] MFA_Activation: {e}")
            flash("No se pudo generar el QR. Intente nuevamente.", "danger")
            return redirect(url_for(self._ENDPOINT))

    def mfa_activacion(self):
        """Confirma el código TOTP y activa el MFA."""
        form       = FormVerificarMFA()
        id_usuario = session.get("user_id")

        if not form.validate_on_submit():
            errores = "; ".join(f"{f}: {', '.join(m)}" for f, m in form.errors.items())
            flash(errores, "danger")
            return redirect(url_for(self._ENDPOINT))

        try:
            data = sp_obtener_mfa_secret(id_usuario)
            if not data:
                flash("Sesión expirada. Inicie el proceso nuevamente.", "danger")
                return redirect(url_for(self._ENDPOINT))

            row = data[0]
            secret_temp = row.get("MFA_Secret_Temp") or row.get("mfa_secret_temp")
            if isinstance(secret_temp, (bytes, bytearray)):
                secret_temp = secret_temp.decode("utf-8")

            secret_temp = secret_temp or session.get("mfa_secret_temp")

            if not secret_temp:
                flash("No hay configuración pendiente. Inicie el proceso nuevamente.", "danger")
                return redirect(url_for(self._ENDPOINT))

            if not MFA_Controller.verificar_codigo(secret_temp, form.codigo_mfa.data.strip()):
                flash("Código incorrecto. Verifique la hora de su dispositivo.", "danger")
                return redirect(url_for(self._ENDPOINT))

            sp_activar_mfa(id_usuario)
            db.commit()

            session["double_factor"] = "ACTIVE"
            session.pop("mfa_secret_temp", None)
            session.pop("mfa_qr_temp", None)

            flash("Autenticación de dos factores activada correctamente.", "success")
            return redirect(url_for(self._ENDPOINT))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] mfa_activacion: {e}")
            flash("Error interno al confirmar. Intente nuevamente.", "danger")
            return redirect(url_for(self._ENDPOINT))

    def mfa_desactivar(self):
        """Verifica TOTP y desactiva el MFA."""
        form       = FormVerificarMFA()
        id_usuario = session.get("user_id")

        if not form.validate_on_submit():
            errores = "; ".join(f"{f}: {', '.join(m)}" for f, m in form.errors.items())
            flash(f"Errores en el formulario: {errores}", "danger")
            return redirect(url_for(self._ENDPOINT))

        try:
            data = sp_obtener_mfa_secret(id_usuario)
            if not data:
                flash("Sesión expirada. Inicie sesión nuevamente.", "danger")
                return redirect(url_for("auth.login_user"))

            row = data[0]
            secret = row.get("MFA_Secret") or row.get("mfa_secret")
            if isinstance(secret, (bytes, bytearray)):
                secret = secret.decode("utf-8")

            if not secret:
                flash("El 2FA no está activo en tu cuenta.", "warning")
                return redirect(url_for(self._ENDPOINT))

            if not MFA_Controller.verificar_codigo(secret, form.codigo_mfa.data.strip()):
                flash("Código incorrecto. No se puede desactivar.", "danger")
                return redirect(url_for(self._ENDPOINT))

            sp_desactivar_mfa(id_usuario)
            db.commit()

            session["double_factor"] = "INACTIVE"
            flash("Autenticación de dos factores desactivada.", "success")
            return redirect(url_for(self._ENDPOINT))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] mfa_desactivar: {e}")
            flash("Error interno. Intente nuevamente.", "danger")
            return redirect(url_for(self._ENDPOINT))