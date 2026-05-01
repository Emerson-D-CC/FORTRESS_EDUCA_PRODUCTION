from functools import wraps, lru_cache
# FUNCIONES DE FLASK
from flask import session, abort, redirect, url_for, flash

# Conexión con BD
from app.repositories.utils_repository import sp_obtener_roles

@lru_cache(maxsize=None)
def _get_role_id(nombre_rol):
    """Obtiene y cachea el ID de un rol por su nombre"""
    return sp_obtener_roles(nombre_rol)


def role_required(f):
    """Verifica que el usuario sea ADMIN o TECNICO"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debe iniciar sesión para continuar", "warning")
            return redirect(url_for("home.public_home"))
        
        role_ids = [_get_role_id("Admin"), _get_role_id("Tecnico")]     

        if role_ids is None:
            abort(500)

        if session.get('role_id') not in role_ids:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function