from functools import wraps, lru_cache
from flask import session, abort, redirect, url_for, flash, make_response

# Conexión con BD
from app.repositories.utils_repository import sp_obtener_roles, sp_verificar_jti

from flask_jwt_extended import verify_jwt_in_request, get_jwt, unset_jwt_cookies


@lru_cache(maxsize=None)
def _get_role_id(nombre_rol):
    """Obtiene y cachea el ID de un rol por su nombre."""
    return sp_obtener_roles(nombre_rol)


def login_required(f):
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
                response = make_response(redirect(url_for("auth.login_admin")))
                unset_jwt_cookies(response)
                session.clear()
                flash("Su sesión actual ha sido cerrada. Si no ha sido usted, realice cambio de contraseña.", "danger")
                return response
        
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Verifica que el usuario sea ADMIN."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debe iniciar sesión para continuar", "warning")
            return redirect(url_for("auth.login_admin"))

        admin_id = _get_role_id("Admin")

        if admin_id is None:
            abort(500)

        if session.get('role_id') != admin_id:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function