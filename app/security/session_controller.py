# FUNCIONES DE FLASK
from flask import session, redirect, request
from datetime import datetime, timezone
# FUNCIONES DE FLASK
from flask_jwt_extended import unset_jwt_cookies, verify_jwt_in_request, get_jwt

from app.settings import Config_Session

# UTILIDADES
from app.utils.database_utils import db

from app.repositories.auth_repository import sp_cerrar_sesion
from app.security.redirect_controller import get_login_url_por_rol


# Declarar Constantes para configuración
TIEMPO_MAX_INACTIVIDAD = Config_Session.PERMANENT_SESSION_LIFETIME
MAX_SESSION_DURATION = Config_Session.MAX_SESSION_DURATION

def _cerrar_sesion_inactiva():
    """Cierra la sesión de un usuario por inactividad o tiempo limite"""
    
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims:
            jti = claims.get("jti", "")
            if jti:
                sp_cerrar_sesion(jti)
                db.commit()

        jti = session.get("jti")
        if jti:
            sp_cerrar_sesion(jti)
            db.commit()
            print(f"[INFO] Sesión cerrada por inactividad: JTI={jti}")
    except Exception as e:
        print(f"[WARN] No se pudo cerrar sesión en BD (inactividad): {e}")
    finally:
        session.clear()


def _redirect_a_login():
    """Construye la respuesta de redirección al login correcto ANTES de limpiar sesión"""
    
    login_url = get_login_url_por_rol()   # lee role_id de sesión antes de borrarla
    _cerrar_sesion_inactiva()             # limpia sesión y BD
    response = redirect(login_url)
    unset_jwt_cookies(response)
    return response


def controlar_sesion(app):
    @app.before_request
    def verificar_inactividad():
        rutas_publicas = [
            "auth.login_user",
            "auth.login_admin",
            "auth.login_technical",            
        ]

        if request.endpoint in rutas_publicas:
            return None

        if "user_id" not in session:
            return None

        ahora = datetime.now(timezone.utc)

        # Verificar duración máxima de sesión
        session_start_str = session.get("session_start")
        if session_start_str:
            try:
                session_start = datetime.fromisoformat(session_start_str)
                if ahora - session_start > MAX_SESSION_DURATION:
                    return _redirect_a_login()
            except ValueError:
                return _redirect_a_login()

        # Verificar inactividad
        ultima_str = session.get("ultima_actividad")
        if ultima_str:
            try:
                ultima = datetime.fromisoformat(ultima_str)
                if ahora - ultima > TIEMPO_MAX_INACTIVIDAD:
                    return _redirect_a_login()
            except ValueError:
                return _redirect_a_login()

        session["ultima_actividad"] = ahora.isoformat()