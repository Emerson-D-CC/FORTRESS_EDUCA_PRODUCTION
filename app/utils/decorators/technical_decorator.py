from functools import wraps, lru_cache
# FUNCIONES DE FLASK
from flask import session, abort, redirect, url_for, flash, make_response

# Conexión con BD
from app.repositories.utils_repository import sp_obtener_roles, sp_verificar_jti, sp_verificar_mfa

# FUNCIONES DE FLASK
from flask_jwt_extended import verify_jwt_in_request, get_jwt, unset_jwt_cookies


@lru_cache(maxsize=None)
def _get_role_id(nombre_rol):
    """Obtiene y cachea el ID de un rol por su nombre"""
    return sp_obtener_roles(nombre_rol)


def login_required(f):
    """Varifica que allá una sesión activa"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Valida firma y expiración del JWT (igual que antes) 
        verify_jwt_in_request()
        
        # Verifica que la sesión siga activa en BD
        claims = get_jwt()
        jti = claims.get("jti", "")
        
        if jti:
            resultado = sp_verificar_jti(jti)
            # sp_verificar_jti retorna [{"activo": 0}] si fue cerrada manualmente
            if not resultado or resultado[0].get("activo", 0) == 0:
                response = make_response(redirect(url_for("auth.login_technical")))
                unset_jwt_cookies(response)
                session.clear()
                flash("Su sesión actual ha sido cerrada. Si no ha sido usted, realice cambio de contraseña.", "danger")
                return response
        
        return f(*args, **kwargs)
    return decorated


def technical_required(f):
    """Verifica que el usuario sea TECNICO"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debe iniciar sesión para continuar", "warning")
            return redirect(url_for("auth.login_technical"))

        technical_id = _get_role_id("Tecnico")

        if technical_id is None:
            abort(500)

        if session.get('role_id') != technical_id:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def mfa_required(f):
    """Verifica que el usuario tenga el MFA activo y configurado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debe iniciar sesión para continuar", "warning")
            return redirect(url_for("auth.login_technical"))

        resultado = sp_verificar_mfa(session['user_id'])

        # Si no tiene MFA activo o no tiene secret configurado, redirige
        if not resultado or \
           resultado.get("Doble_Factor_Activo") != "ACTIVE" or \
           not resultado.get("MFA_Secret"):
            return make_response(redirect(url_for("auth.config_mfa"), 303))

        return f(*args, **kwargs)
    return decorated_function