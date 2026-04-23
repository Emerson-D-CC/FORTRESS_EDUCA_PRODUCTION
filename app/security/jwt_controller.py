from flask_jwt_extended import create_access_token, create_refresh_token, unset_jwt_cookies
from flask import redirect, flash, session, make_response
from flask import current_app

from app.security.redirect_controller import get_login_url_por_rol

from datetime import timedelta


# ── Sin cambios ─────────────────────────────────────────────────────────────
def generar_access_token(user_id, role_id):
    additional_claims = {"role_id": role_id}
    expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(minutes=55))
    return create_access_token(
        identity=str(user_id),
        additional_claims=additional_claims,
        expires_delta=expires_delta
    )

def generar_refresh_token(user_id):
    return create_refresh_token(identity=str(user_id))


# ── Handlers actualizados ────────────────────────────────────────────────────

def handle_unauthorized_error(err_str):
    """Sin token: solo tenemos sesión para resolver el rol"""
    
    login_url = get_login_url_por_rol() 
    session.clear()
    response = make_response(redirect(login_url))
    unset_jwt_cookies(response)
    flash("No se encontró una sesión activa.", "warning")
    return response


def handle_expired_error(jwt_header, jwt_data):
    """Token expirado: los claims aún son accesibles en jwt_data"""
    
    role_id = jwt_data.get("role_id") if jwt_data else None
    login_url = get_login_url_por_rol(role_id=role_id)
    session.clear()
    response = make_response(redirect(login_url))
    unset_jwt_cookies(response)
    flash("Tu sesión ha expirado. Por favor, ingresa de nuevo.", "danger")
    return response


def handle_invalid_error(err_str):
    """Token inválido/manipulado: sin claims confiables, usamos sesión"""
    
    login_url = get_login_url_por_rol()
    session.clear()
    response = make_response(redirect(login_url))
    unset_jwt_cookies(response)
    flash("Token inválido o manipulado.", "danger")
    return response






"""
from flask_jwt_extended import create_access_token, create_refresh_token, unset_jwt_cookies
from flask import redirect, url_for, flash, session, make_response
from flask import current_app


from app.repositories.utils_repository import sp_obtener_roles

from datetime import timedelta


# Generar Access Token
def generar_access_token(user_id, role_id):
    
    # Los datos extra (role_id) se pasan en additional_claims
    additional_claims = {"role_id": role_id}

    expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(minutes=55))
    return create_access_token(identity=str(user_id), additional_claims=additional_claims, expires_delta=expires_delta)

# Generar Refresh Token
def generar_refresh_token(user_id):
    return create_refresh_token(identity=str(user_id))

def handle_unauthorized_error(err_str):
    session.clear()
    response = make_response(redirect(url_for("auth.login_user")))
    unset_jwt_cookies(response)
    flash("No se encontró una sesión activa.", "warning")
    return response

def handle_expired_error(jwt_header, jwt_data):
    session.clear()
    response = make_response(redirect(url_for("auth.login_user")))
    unset_jwt_cookies(response)
    flash("Tu sesión ha expirado. Por favor, ingresa de nuevo.", "danger")
    return response

def handle_invalid_error(err_str):
    session.clear()
    response = make_response(redirect(url_for("auth.login_user")))
    unset_jwt_cookies(response)
    flash("Token inválido o manipulado.", "danger")
    return response

"""