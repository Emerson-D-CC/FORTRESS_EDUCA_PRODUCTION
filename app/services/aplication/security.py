# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session
from flask_jwt_extended import get_jwt

# UTILIDADES
from app.utils.database_utils import db
from app.utils.password_utils import hashear_contraseña, verificar_contraseña

# SEGURIDAD
from app.security.mfa_controller import MFA_Controller

# CONFIGURACIONES LOCALES
from app.forms.aplication_forms import *
from app.repositories.aplication_repository import *

# ====================================================================================================================================================
#                                           PAGINA SECURITY.HTML
# ====================================================================================================================================================

class Security_Settings_Service:
    """Inicializa los formularios para la pagina de security."""

    def cargar_informacion_seguridad(self):
        
        form_password = FormCambiarcontraseña()
        form_mfa_activar = FormVerificarMFA()
        form_mfa_desactivar = FormVerificarMFA()
        sesiones = Security_Settings_Service().Session_Handler_Service()
        
        return render_template(
            "aplication/security.html",
            form_password=form_password,
            form_mfa_activar=form_mfa_activar,
            form_mfa_desactivar=form_mfa_desactivar,
            sesiones=sesiones,
            active_page="security"
        )

# ==========================================================================
#  GESTIÓN DE CAMBIO DE CONTRASEÑA

    def Change_Password(self):
        """Gestiona el cambio de contraseña desde el perfil del usuario."""

        # Cargar formulario
        form = FormCambiarcontraseña()
        
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")
        id_usuario = session.get("user_id")
        username = session.get("username_login")

        if request.method == "POST":
            if not form.validate_on_submit():
                errores = "; ".join(
                    mensaje for mensajes in form.errors.values() for mensaje in mensajes
                )
                flash(f"{errores}", "danger")
                return redirect(url_for("aplication.security"))

            contraseña_actual = form.contraseña_actual.data
            nueva_contraseña = form.nueva_contraseña.data

            try:
                # Obtener datos del usuario actual para validar contraseña
                data_user = sp_validar_data_user(username)
                if not data_user:
                    flash("Sesión inválida. Por favor inicie sesión nuevamente.", "danger")
                    return redirect(url_for("aplication.security"))

                data_user = data_user[0]
                
                validar_contraseña = self._validar_usuario(username, contraseña_actual)
                
                if not validar_contraseña:
                    flash("La contraseña actual no es correcta.", "danger")
                    return redirect(url_for("aplication.security"))

                # Generar nuevo salt + hash
                nuevo_hash = hashear_contraseña(nueva_contraseña)

                # Llamar SP para cambiar contraseña
                sp_cambiar_contraseña_perfil(id_usuario, nuevo_hash, ip, user_agent)
                
                db.commit()
                flash("Contraseña actualizada correctamente.", "success")
                return redirect(url_for("aplication.security"))

            except Exception as e:
                db.rollback()
                print(f"[ERROR] Cambiarcontraseña: {e}")
                flash("Error interno. Intente nuevamente.", "danger")
                return redirect(url_for("aplication.security"))

        # GET — Renderizar página de seguridad con formulario
        return render_template(
            "aplication/security.html",
            form_password=form,
            active_page="security"
        ) 
        
    def _validar_usuario(self, username, password_ingresada):
        try:
            user_data = sp_validar_data_autenticacion(username)

            if not user_data:
                return False 

            id_usuario = user_data[0].get("ID_Usuario")
            hash_db = user_data[0].get("Contraseña_Hash")

            if not hash_db:
                return False
            
            # Evaluar si las contraseñas coinciden
            es_valido = verificar_contraseña(password_ingresada, hash_db)

            if es_valido:
                # Notificar a la BD
                sp_exito_login(id_usuario)
                return True
            else:
                # Contraseña incorrecta
                return False

        except Exception as e:
            print(f"[ERROR] _validar_usuario: {e}")
            return False

# ==========================================================================
#  GESTIÓN DE MFA (Microsoft Authenticator / TOTP)

    def MFA_Activation(self):
        """Activa, desactiva y verifica el doble factor de autenticación."""

        # Obener datos del usuario
        id_usuario = session.get("user_id")
        username = session.get("username")

        try:
            # Verificar si ya hay un secret temporal pendiente en BD
            data = sp_obtener_mfa_secret(id_usuario)
            row = data[0] if data else {}

            secret_temp_existente = row.get("MFA_Secret_Temp")
            if isinstance(secret_temp_existente, (bytes, bytearray)):
                secret_temp_existente = secret_temp_existente.decode("utf-8")

            # Si ya hay un secret temporal, reutilizarlo en lugar de generar uno nuevo
            if secret_temp_existente and session.get("mfa_secret_temp") == secret_temp_existente:
                flash("Ya tiene un QR pendiente. Escanéelo e ingrese el código para confirmar.", "info")
                return redirect(url_for("aplication.security"))

            # No hay secret pendiente: generar uno nuevo
            secret = MFA_Controller.generar_secret()
            uri = MFA_Controller.generar_uri(secret, username)
            qr_b64 = MFA_Controller.generar_qr_base64(uri)

            sp_guardar_mfa_secret_temp(id_usuario, secret)
            db.commit()

            session['mfa_secret_temp'] = secret
            session['mfa_qr_temp'] = f"data:image/png;base64,{qr_b64}"
            
            print(f"[DEBUG] iniciar_activacion - secret generado: {secret}")
            print(f"[DEBUG] iniciar_activacion - session mfa_secret_temp antes: {session.get('mfa_secret_temp')}")
            
            flash("QR generado. Escaneelo con Microsoft Authenticator e ingrese el código para confirmar.", "info")
            return redirect(url_for("aplication.security"))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] iniciar_activacion MFA: {e}")
            flash("No se pudo generar el QR. Intente nuevamente.", "danger")
            return redirect(url_for("aplication.security"))

    def mfa_activacion(self):
        """Recibe el código TOTP y, si es válido, activa el MFA"""
        
        form = FormVerificarMFA()
        id_usuario = session.get("user_id")

        if not form.validate_on_submit():
            errores = "; ".join(f"{f}: {', '.join(m)}" for f, m in form.errors.items())
            flash(f"{errores}", "danger")
            return redirect(url_for("aplication.security"))

        try:
            # Obtener secret desde la BD (fuente de verdad)
            data = sp_obtener_mfa_secret(id_usuario)
            if not data:
                flash("Sesión expirada. Inicie el proceso nuevamente.", "danger")
                return redirect(url_for("aplication.security"))
            
            row = data[0]

            # Normalizar: el driver puede retornar bytes o str
            secret_temp = row.get("MFA_Secret_Temp") or row.get("mfa_secret_temp")
            if isinstance(secret_temp, (bytes, bytearray)):
                secret_temp = secret_temp.decode("utf-8")

            if not secret_temp:
                # Fallback: usar el secret guardado en sesión
                secret_temp = session.get("mfa_secret_temp")

            if not secret_temp:
                flash("No hay configuración pendiente. Inicie el proceso nuevamente.", "danger")
                return redirect(url_for("aplication.security"))

            codigo_ingresado = form.codigo_mfa.data.strip()
            
            if not MFA_Controller.verificar_codigo(secret_temp, codigo_ingresado):
                flash("Código incorrecto. Verifique la hora de su dispositivo e intente de nuevo.", "danger")
                return redirect(url_for("aplication.security"))

            sp_activar_mfa(id_usuario)
            db.commit()

            session["double_factor"] = "ACTIVE"
            session.pop('mfa_secret_temp', None)
            session.pop('mfa_qr_temp', None)

            flash("Autenticación de dos factores activada correctamente.", "success")
            return redirect(url_for("aplication.security"))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] confirmar_activacion MFA: {e}")
            flash("Error interno al confirmar. Intente nuevamente.", "danger")
            return redirect(url_for("aplication.security"))


    def mfa_desactivar(self):
        """Desactiva el MFA después de verificar un código vigente"""
        
        form = FormVerificarMFA()
        id_usuario = session.get("user_id")

        if not form.validate_on_submit():
            errores = "; ".join(f"{f}: {', '.join(m)}" for f, m in form.errors.items())
            flash(f"Errores en el formulario: {errores}", "danger")
            return redirect(url_for("aplication.security"))

        try:
            data = sp_obtener_mfa_secret(id_usuario)
            if not data:
                flash("Sesión expirada. Inicie sesión nuevamente.", "danger")
                return redirect(url_for("auth.login_user"))

            row = data[0]

            # Normalizar igual que en confirmar_activacion
            secret = row.get("MFA_Secret") or row.get("mfa_secret")
            if isinstance(secret, (bytes, bytearray)):
                secret = secret.decode("utf-8")

            if not secret:
                flash("El 2FA no está activo en tu cuenta.", "warning")
                return redirect(url_for("aplication.security"))

            if not MFA_Controller.verificar_codigo(secret, form.codigo_mfa.data.strip()):
                flash("Código incorrecto. No se puede desactivar.", "danger")
                return redirect(url_for("aplication.security"))

            sp_desactivar_mfa(id_usuario)
            db.commit()

            session["double_factor"] = "INACTIVE"

            flash("Autenticación de dos factores desactivada.", "success")
            return redirect(url_for("aplication.security"))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] desactivar MFA: {e}")
            flash("Error interno. Intente nuevamente.", "danger")
            return redirect(url_for("aplication.security"))


# ==========================================================================
# CENTRO DE CONTROL DE SESIONES 

    def Session_Handler_Service(self):
        """Consulta y revoca sesiones activas del usuario."""
        
        id_usuario = session.get("user_id")
        try:
            sesiones = sp_listar_sesiones(id_usuario)
            jti_actual = get_jwt().get("jti", "")

            sesiones_formateadas = []
            for s in (sesiones or []):
                sesiones_formateadas.append({
                    "id": s["ID_Sesion"],
                    "JTI": s["JTI"],
                    "dispositivo": s["Dispositivo"] or "Desconocido",
                    "ip": s["IP"] or "—",
                    "inicio": s["Fecha_Inicio"].strftime("%d/%m/%Y %H:%M") if s.get("Fecha_Inicio") else "—",
                    "ultimo": s["Ultimo_Acceso"].strftime("%d/%m/%Y %H:%M") if s.get("Ultimo_Acceso") else "—",
                    "es_actual": s["JTI"] == jti_actual,
                })

            session['sesiones_activas'] = sesiones_formateadas
            return sesiones_formateadas

        except Exception as e:
            print(f"[ERROR] listar sesiones: {e}")
            return []

    def cerrar_sesiones(self):
        id_usuario = session.get("user_id")
        try:
            jti_actual = get_jwt().get("jti", "")
            sp_cerrar_todas_sesiones(id_usuario, jti_actual)
            db.commit()
            flash("Todas las demás sesiones han sido cerradas.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR] cerrar_otras: {e}")
            flash("Error al cerrar sesiones. Intente nuevamente.", "danger")
        return redirect(url_for("aplication.security"))

    def cerrar_sesion(self, jti_sesion: str):
        id_usuario = session.get("user_id")
        try:
            sesiones = sp_listar_sesiones(id_usuario) or []
            sesion = next((s for s in sesiones if s["JTI"] == jti_sesion), None)

            if not sesion:
                flash("Sesión no encontrada.", "warning")
                return redirect(url_for("aplication.security"))

            jti_actual = get_jwt().get("jti", "")
            if jti_sesion == jti_actual:
                flash("No puede cerrar su sesión actual desde aquí.", "danger")
                return redirect(url_for("aplication.security"))

            sp_cerrar_sesion(jti_sesion)
            db.commit()
            flash("Sesión cerrada correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR] cerrar_una: {e}")
            flash("Error al cerrar sesión. Intente nuevamente.", "danger")
        return redirect(url_for("aplication.security"))