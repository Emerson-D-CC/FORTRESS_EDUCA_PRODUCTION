from datetime import datetime, timezone

# FUNCIONES DE FLASK
from flask import request, redirect, url_for, flash, session, current_app, make_response
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt, verify_jwt_in_request, decode_token

# CONFIGURACIONES LOCALES
from app.forms.auth_forms import LoginTecForm
from app.repositories.auth_repository import (
    sp_validar_data_user, 
    sp_registrar_sesion, 
    sp_validar_data_autenticacion, 
    sp_exito_login, 
    sp_obtener_roles, 
    sp_cerrar_sesion,
)

# SEGURIDAD
from app.security.recaptcha_controller import validar_recaptcha
from app.security.jwt_controller import generar_access_token, generar_refresh_token

# UTILIDADES
from app.utils.password_utils import verificar_contraseña
from app.utils.database_utils import db
from app.utils.audit_utils import Auditoria_Session
from app.utils.response_utils import render_no_cache  

    # Intentos fallidos antes de exigir reCAPTCHA
INTENTOS_PARA_RECAPTCHA = 3

class Login_Technical_Service:
    """Servicio de autenticación"""

# ====================================================================================================================================================
#                                           PAGINA LOGIN_TECHNICAL.HTML
# ====================================================================================================================================================
    
    def Login_Technical(self):
        """Validación de credenciales y rol para ingreso"""

        form  = LoginTecForm()
        
        intentos_fallidos = session.get("login_intentos_technical", 0)
        mostrar_recaptcha = intentos_fallidos >= INTENTOS_PARA_RECAPTCHA
        site_key = current_app.config.get("RECAPTCHA_SITE_KEY", "")

        # Indicar que la recuperación de contraseña debe volver a la página de login de tecnico
        session["password_recovery_login_endpoint"] = "auth.login_technical"

        ctx = dict(form=form, mostrar_recaptcha=mostrar_recaptcha,
                   recaptcha_site_key=site_key)

        # =====================================================
        # SOLICITUD POST
        if request.method == "POST":

            if not form.validate_on_submit():
                return render_no_cache("auth/login_technical.html", **ctx)
            
            # Datos de auditoría
            ip = request.remote_addr
            user_agent = request.headers.get("User-Agent")
            
            # Se valida antes de consultar la BD para ahorrar recursos.
            if mostrar_recaptcha:
                token_recaptcha = request.form.get("g-recaptcha-response", "")
                if not token_recaptcha:
                    flash("Por favor complete el reCAPTCHA.", "warning")
                    ctx["mostrar_recaptcha"] = True
                    return render_no_cache("auth/login_technical.html", **ctx)
                
                # validar_recaptcha retorna True si el token es válido                
                if not validar_recaptcha(token_recaptcha):
                    flash("reCAPTCHA inválido. Intente nuevamente.", "danger")
                    ctx["mostrar_recaptcha"] = True
                    return render_no_cache("auth/login_technical.html", **ctx)
                
            # Credenciales del formulario
            username = form.username_technical.data
            password = form.password.data

            try:
                # Buscar datos del usuario en BD por nombre de usuario                
                data_user = sp_validar_data_user(username)

                if not data_user:
                    # Se pasa 2 como ID (usuario generido de auditoria del sistema) si no existe en la BD.                     
                    Auditoria_Session(2, ip, "TEC_FAILED_LOGIN", user_agent)
                    
                    # Incrementar contador de intentos fallidos                    
                    session["login_intentos_technical"] = intentos_fallidos + 1
                    ctx["mostrar_recaptcha"] = session["login_intentos_technical"] >= INTENTOS_PARA_RECAPTCHA
                    
                    flash("Credenciales inválidas", "danger")
                    return render_no_cache("auth/login_technical.html", **ctx)
                
                # Cache en memoria para evitar consultas repetidas a BD
                data_user = data_user[0]

                if not self._validar_usuario(username, password):
                    # Auditar intento fallido con usuario existente                    
                    Auditoria_Session(data_user["ID_Usuario"], ip, "FAILED_LOGIN", user_agent)
                    
                    # Incrementar contador de intentos fallidos                    
                    session["login_intentos_technical"] = intentos_fallidos + 1
                    ctx["mostrar_recaptcha"] = session["login_intentos_technical"] >= INTENTOS_PARA_RECAPTCHA
                    
                    flash("Credenciales inválidas", "danger")
                    return render_no_cache("auth/login_technical.html", **ctx)
                
                # Validar el rol del usuario
                if not self._validar_rol_technical(data_user["FK_ID_Rol"]):
                    # Auditar intento fallido con usuario existente                    
                    Auditoria_Session(data_user["ID_Usuario"], ip, "FAILED_LOGIN", user_agent)
                    
                    # Incrementar contador de intentos fallidos
                    session["login_intentos_technical"] = intentos_fallidos + 1
                    ctx["mostrar_recaptcha"] = session["login_intentos_technical"] >= INTENTOS_PARA_RECAPTCHA
                    
                    flash("La cuenta no tiene los permisos necesarios para acceder", "danger")
                    return render_no_cache("auth/login_technical.html", **ctx)

                # LOGIN EXITOSO
                session.pop("login_intentos_technical", None)

                primer_nombre = data_user.get("Primer_Nombre", "")
                primer_apellido = data_user.get("Primer_Apellido", "")
                nombre_technical = data_user.get("Nombre_Completo", "")
                
                iniciales_technical = (
                    (primer_nombre[0] if primer_nombre   else "") +
                    (primer_apellido[0] if primer_apellido else "")
                ).upper()

                # Guardar datos importantes para la sesión
                session.permanent = True
                session["user_id"] = data_user["ID_Usuario"]
                session["username"] = nombre_technical
                session["username_login"] = username
                session["role_id"] = data_user["FK_ID_Rol"]
                session["double_factor"] = data_user["Doble_Factor_Activo"]
                session["nombre_technical"] = nombre_technical
                session["iniciales_technical"] = iniciales_technical
                session["session_start"] = datetime.now(timezone.utc).isoformat()
                session["ultima_actividad"] = datetime.now(timezone.utc).isoformat()

                # GENERAR TOKENS
                access_token = generar_access_token(data_user["ID_Usuario"], data_user["FK_ID_Rol"])
                refresh_token = generar_refresh_token(data_user["ID_Usuario"])

                try:
                    decoded = decode_token(access_token)
                    jti = decoded.get("jti", "")
                    session["jti"] = jti
                    sp_registrar_sesion(
                        data_user["ID_Usuario"], jti,
                        (user_agent or "Desconocido")[:255], ip
                    )
                    db.commit()
                except Exception as e:
                    print(f"[WARN] No se pudo registrar sesión: {e}")

                if data_user.get("Doble_Factor_Activo") == "ACTIVE":
                    # MFA ya configurado. Verificar código
                    session["mfa_pendiente"] = True
                    session["mfa_user_autenticado"] = True
                    session["mfa_rol_esperado"] = "Tecnico"                    
                    session["mfa_login_url"] = url_for("auth.login_technical")
                    session["mfa_success_url"] = url_for("technical.dashboard")
                    
                    # Auditar ingreso con MFA existente
                    Auditoria_Session(data_user["ID_Usuario"], ip, "PENDING_MFA", user_agent)
                    response = make_response(redirect(url_for("auth.verify_mfa"), 303))
                else:
                    # MFA no configurado. Forzar configuración antes de entrar
                    session["mfa_setup_pendiente"]  = True
                    session["mfa_user_autenticado"] = True
                    session["mfa_rol_esperado"] = "Tecnico"
                    session["mfa_login_url"] = url_for("auth.login_technical")
                    session["mfa_success_url"] = url_for("technical.dashboard")
                    Auditoria_Session(data_user["ID_Usuario"], ip, "PENDING_MFA", user_agent)
                    response = make_response(redirect(url_for("auth.config_mfa"), 303))

                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                return response

            except Exception as e:
                print(f"[ERROR] Login_Technical: {e}")
                flash("Error interno del servidor. Intente nuevamente.", "danger")
                return render_no_cache("auth/login_technical.html", **ctx)
            
        # =====================================================
        # SOLICITUD GET — renderizar formulario con estado actual de intentos
        return render_no_cache("auth/login_technical.html", **ctx)

    # Métodos privados
    def _validar_usuario(self, username, password_ingresada):
        """Valida la credenciales ingresadas por el usuario"""
        try:
            user_data = sp_validar_data_autenticacion(username)

            if not user_data:
                return False 

            id_usuario = user_data[0].get("ID_Usuario")
            hash_db = user_data[0].get("Contraseña_Hash")

            if not hash_db:
                return False
            
            if verificar_contraseña(password_ingresada, hash_db):
                # Notificar a la BD
                sp_exito_login(id_usuario)
                return True
            return False

        except Exception as e:
            print(f"[ERROR] _validar_usuario: {e}")
            return False


    def _validar_rol_technical(self, role_id):
        """Obtiene el ID del rol para comparar con el rol del usuario"""
        try:
            if role_id is None:
                return False
                
            id_rol_requerido = sp_obtener_roles("Tecnico")
            if id_rol_requerido != role_id:
                return False
            return True
        
        except Exception as e:
            print(f"[ERROR] _validar_rol_technical: {e}")
            return False




# ====================================================================================================================================================
#                                           FUNCIÓN DE LOGOUT
# ====================================================================================================================================================

    def Logout(self):
        """Cierra la sesión del usuario activo usando Flask-JWT-Extended"""
        
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            if claims:
                user_id = claims.get("sub")
                jti = claims.get("jti", "")
                ip = request.remote_addr
                user_agent = request.headers.get("User-Agent")
                
                if jti:
                    try:
                        sp_cerrar_sesion(jti)
                        db.commit()
                    except Exception as e:
                        print(f"[WARN] No se pudo cerrar sesión en BD: {e}")
                        
                Auditoria_Session(user_id, ip, "LOGOUT", user_agent)
                
            response = make_response(redirect(url_for("auth.login_technical"), 303))
            unset_jwt_cookies(response)
            session.clear()
            return response
        
        except Exception as e:
            print(f"[ERROR] Logout technical: {e}")
            response = make_response(redirect(url_for("auth.login_technical"), 303))
            unset_jwt_cookies(response)
            session.clear()
            return response