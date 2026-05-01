import random
from datetime import datetime, timedelta

# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_mail import Message

# CONFIGURACIONES LOCALES
from app.forms.auth_forms import RecuperarcontraseñaForm, VerificarCodigoForm, NuevacontraseñaForm
from app.repositories.auth_repository import (
    sp_obtener_email_por_username, 
    sp_actualizar_contraseña,
)

# UTILIDADES
from app.utils.extensions_utils import mail
from app.utils.password_utils import hashear_contraseña

# Permitir solo endpoints válidos para la redirección final de recuperación
_VALID_LOGIN_RECOVERY_ENDPOINTS = {"auth.login_user", "auth.login_admin"}


def _obtener_url_login_recovery():
    endpoint = session.get("password_recovery_login_endpoint", "auth.login_user")
    if endpoint not in _VALID_LOGIN_RECOVERY_ENDPOINTS:
        endpoint = "auth.login_user"
    return url_for(endpoint)


def _set_password_recovery_login_endpoint_from_request():
    endpoint = request.args.get("next", "")
    if endpoint in _VALID_LOGIN_RECOVERY_ENDPOINTS:
        session["password_recovery_login_endpoint"] = endpoint


# ====================================================================================================================================================
#                                           PAGINA RECOVER_PASSWORD.HTML
# ====================================================================================================================================================

class Password_Recovery_Service:

    CODIGO_TTL_MINUTOS = 10  # tiempo de expiración codigo

    #  Solicitar código
    def Password_Recovery(self):
        
        """GET / POST — el usuario ingresa su correo y recibe el código"""
        _set_password_recovery_login_endpoint_from_request()
        login_url = _obtener_url_login_recovery()
        form = RecuperarcontraseñaForm()

        # =====================================================
        # SOLICITUD GET
        
        if request.method == "GET":
            return render_template("auth/recover_password.html", form=form, paso=1, login_url=login_url)

        # =====================================================
        # SOLICITUD POST
        
        if not form.validate_on_submit():
            flash("Por favor ingrese un correo válido.", "danger")
            return render_template("auth/recover_password.html", form=form, paso=1, login_url=login_url)

        username = form.username.data.strip().lower()

        # Verificar si el usuario existe
        email = sp_obtener_email_por_username(username)
        if not email:
            # Mensaje genérico para no revelar si el usuario existe
            flash("Si el correo está registrado, recibirá un código en breve.", "info")
            return render_template("auth/recover_password.html", form=form, paso=1, login_url=login_url)

        # Generar código aleatorio de 6 dígitos
        codigo = str(random.randint(100000, 999999))
        expiracion = (datetime.utcnow() + timedelta(minutes=self.CODIGO_TTL_MINUTOS)).isoformat()

        # Guardar en sesión
        session["recuperacion"] = {
            "username": username,
            "codigo": codigo,
            "expiracion": expiracion,
            "verificado": False
        }

        # Enviar correo
        try:
            self._enviar_correo_codigo(email, codigo)
        except Exception as e:
            current_app.logger.error(f"Error enviando correo de recuperación: {e}")
            flash("No se pudo enviar el correo. Intente más tarde.", "danger")
            return render_template("auth/recover_password.html", form=form, paso=1, login_url=login_url)

        flash("Código enviado. Revise su bandeja de entrada.", "success")
        return redirect(url_for("auth.recover_password_verify"))

    #  Verificar código
    def Verify_Code(self):
        """GET / POST — el usuario ingresa el código recibido"""
        _set_password_recovery_login_endpoint_from_request()
        login_url = _obtener_url_login_recovery()
        form = VerificarCodigoForm()

        # Redirigir si no hay sesión de recuperación activa
        if "recuperacion" not in session:
            flash("Sesión expirada. Inicie el proceso nuevamente.", "warning")
            return redirect(url_for("auth.recover_password_code"))

        # =====================================================
        # SOLICITUD GET
        
        if request.method == "GET":
            return render_template("auth/recover_password.html", form=form, paso=2, login_url=login_url)

        # =====================================================
        # SOLICITUD POST
        
        if not form.validate_on_submit():
            flash("Ingrese el código de 6 dígitos.", "danger")
            return render_template("auth/recover_password.html", form=form, paso=2, login_url=login_url)

        datos = session["recuperacion"]

        # Verificar expiración
        if datetime.utcnow() > datetime.fromisoformat(datos["expiracion"]):
            session.pop("recuperacion", None)
            flash("El código expiró. Solicite uno nuevo.", "warning")
            return redirect(url_for("auth.recover_password_code"))

        # Comparar código
        if form.codigo.data.strip() != datos["codigo"]:
            flash("Código incorrecto. Verifique e intente de nuevo.", "danger")
            return render_template("auth/recover_password.html", form=form, paso=2, login_url=login_url)

        # Marcar como verificado en sesión
        session["recuperacion"]["verificado"] = True
        session.modified = True

        return redirect(url_for("auth.recover_password_new"))

    #  Nueva contraseña
    def New_Password(self):
        _set_password_recovery_login_endpoint_from_request()
        login_url = _obtener_url_login_recovery()  
        form = NuevacontraseñaForm()

        datos = session.get("recuperacion")

        if not datos or not datos.get("verificado"):
            flash("Acceso no autorizado. Complete el proceso de verificación.", "warning")
            return redirect(url_for("auth.recover_password_code"))

        if request.method == "GET":
            return render_template("auth/recover_password.html", form=form, paso=3, login_url=login_url)

        if not form.validate_on_submit():
            flash("Por favor revise los campos.", "danger")
            return render_template("auth/recover_password.html", form=form, paso=3, login_url=login_url)

        username = datos["username"]
        nuevo_hash = hashear_contraseña(form.password.data)
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent")

        try:
            sp_actualizar_contraseña(username, nuevo_hash, ip, user_agent)
        except Exception as e:
            current_app.logger.error(f"Error actualizando contraseña: {e}")
            flash("Error al actualizar la contraseña. Intente más tarde.", "danger")
            return render_template("auth/recover_password.html", form=form, paso=3, login_url=login_url)

        # limpiar sesión después de haber resuelto login_url
        session.pop("recuperacion", None)
        session.pop("password_recovery_login_endpoint", None)

        flash("¡Contraseña actualizada exitosamente! Ya puede iniciar sesión.", "success")
        return redirect(login_url)  # usar la URL ya resuelta


    #  Envio Correo
    def _enviar_correo_codigo(self, destinatario: str, codigo: str):
        """Envía el correo con el código de verificación"""
        msg = Message(
            subject="Recuperación de contraseña - Fortress Educa",
            recipients=[destinatario]
        )
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; padding: 24px;
                    border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #1a3a5c;">Recuperación de Contraseña</h2>
            <p>Recibimos una solicitud para restablecer la contraseña de su cuenta en
               <strong>Fortress Educa</strong>.</p>
            <p>Su código de verificación es:</p>
            <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px;
                        color: #2e7d32; text-align: center; padding: 16px 0;">
                {codigo}
            </div>
            <p style="color: #666; font-size: 13px;">
                Este código es válido por <strong>{self.CODIGO_TTL_MINUTOS} minutos</strong>.
                Si usted no solicitó este cambio, ignore este correo.
            </p>
            <hr style="border: none; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 11px;">
                Plataforma de Cupos Educativos · Alcaldía Local de Engativá
            </p>
        </div>
        """
        mail.send(msg)