from flask import session, url_for
from app.repositories.utils_repository import sp_obtener_roles

# Cache en memoria para evitar consultas repetidas a BD
_role_id_cache: dict = {}

def _get_role_id_cached(nombre_rol: str):
    """Obtiene y cachea el ID de un rol por nombre para evitar hits continuos a BD"""
    if nombre_rol not in _role_id_cache:
        _role_id_cache[nombre_rol] = sp_obtener_roles(nombre_rol)
    return _role_id_cache[nombre_rol]


def get_login_url_por_rol(role_id=None) -> str:
    """Retorna la URL de login correcta según el role_id"""
    
    if role_id is None:
        role_id = session.get("role_id")

    admin_id = _get_role_id_cached("Admin")

    if role_id is not None and admin_id is not None and role_id == admin_id:
        return url_for("auth.login_admin")

    return url_for("auth.login_user")