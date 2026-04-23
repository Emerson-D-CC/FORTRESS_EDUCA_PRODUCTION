from flask import session, redirect, url_for, flash, render_template, request
from app.utils.database_utils import db

from app.repositories.auth_repository import sp_obtener_mfa_secret, sp_guardar_mfa_secret_temp, sp_activar_mfa

# UTILIDADES
from app.utils.audit_utils import Auditoria_Session
from app.utils.database_utils import db

from app.security.mfa_controller import MFA_Controller
from app.forms.auth_forms  import FormVerificarMFA
from app.utils.response_utils import render_no_cache


class Config_MFA_Service:

    def Config_MFA(self):
        """Genera y muestra el QR para configurar MFA"""
        
        # =====================================================
        # SOLICITUD GET — accesible tras un login admin exitoso sin MFA activo.
        
        # Guardia: solo accesible si viene del login con setup pendiente
        if not session.get("mfa_setup_pendiente") or not session.get("user_id"):
            return redirect(url_for("auth.login_admin"))

        id_usuario = session.get("user_id")
        username = session.get("username", "")

        try:
            data = sp_obtener_mfa_secret(id_usuario)
            row  = data[0] if data else {}

            # Reutilizar secret temporal si ya fue generado (evita generar uno nuevo en cada recarga)
            secret_temp_bd = row.get("MFA_Secret_Temp")
            if isinstance(secret_temp_bd, (bytes, bytearray)):
                secret_temp_bd = secret_temp_bd.decode("utf-8")

            if secret_temp_bd and session.get("mfa_secret_temp") == secret_temp_bd:
                # Ya hay un QR pendiente, solo renderizar
                form = FormVerificarMFA()
                return render_no_cache("auth/config_mfa.html", form=form)

            # Generar nuevo secret y QR
            secret = MFA_Controller.generar_secret()
            uri = MFA_Controller.generar_uri(secret, username)
            qr_b64 = MFA_Controller.generar_qr_base64(uri)

            sp_guardar_mfa_secret_temp(id_usuario, secret)
            db.commit()

            session["mfa_secret_temp"] = secret
            session["mfa_qr_temp"] = f"data:image/png;base64,{qr_b64}"

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Setup_MFA (GET): {e}")
            flash("No se pudo generar el QR. Intente nuevamente.", "danger")
            return redirect(url_for("auth.login_admin"))

        form = FormVerificarMFA()
        return render_no_cache("auth/config_mfa.html", form=form)


    def Verify_Config_MFA(self):
        """Valida el código TOTP y activa el MFA"""
        
        # =====================================================
        # SOLICITUD POST -  Si el código es correcto, activa MFA y redirige al dashboard admin
        
        if not session.get("mfa_setup_pendiente") or not session.get("user_id"):
            return redirect(url_for("auth.login_admin"))

        form = FormVerificarMFA()
        id_usuario = session.get("user_id")
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")

        if not form.validate_on_submit():
            flash("Código inválido. Intente nuevamente.", "danger")
            return render_no_cache("auth/config_mfa.html", form=form)

        try:
            data = sp_obtener_mfa_secret(id_usuario)
            if not data:
                flash("Sesión expirada. Inicie sesión nuevamente.", "danger")
                return redirect(url_for("auth.login_admin"))

            row        = data[0]
            secret_temp = row.get("MFA_Secret_Temp") or row.get("mfa_secret_temp")
            if isinstance(secret_temp, (bytes, bytearray)):
                secret_temp = secret_temp.decode("utf-8")

            # Fallback a sesión si BD no tiene el temporal
            if not secret_temp:
                secret_temp = session.get("mfa_secret_temp")

            if not secret_temp:
                flash("No hay configuración pendiente. Inicie sesión nuevamente.", "danger")
                return redirect(url_for("auth.login_admin"))

            if not MFA_Controller.verificar_codigo(secret_temp, form.codigo_mfa.data.strip()):
                Auditoria_Session(id_usuario, ip, "MFA_SETUP_FAILED", user_agent)
                flash("Código incorrecto. Verifique la hora de su dispositivo.", "danger")
                return render_no_cache("auth/config_mfa.html", form=form)

            # Código válido: activar MFA
            sp_activar_mfa(id_usuario)
            db.commit()

            # Limpiar banderas de setup
            session.pop("mfa_setup_pendiente", None)
            session.pop("mfa_secret_temp", None)
            session.pop("mfa_qr_temp", None)
            session["double_factor"] = "ACTIVE"

            Auditoria_Session(id_usuario, ip, "MFA_SETUP_OK", user_agent)
            flash("Autenticación de dos factores activada. Bienvenido.", "success")
            return redirect(session.get("mfa_success_url", url_for("admin.dashboard")))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Confirmar_Setup_MFA: {e}")
            flash("Error interno. Intente nuevamente.", "danger")
            return render_no_cache("auth/config_mfa.html", form=form)