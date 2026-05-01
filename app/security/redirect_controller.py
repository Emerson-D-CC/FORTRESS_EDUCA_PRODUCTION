# FUNCIONES DE FLASK
from flask import session, request, url_for
from app.repositories.utils_repository import sp_obtener_roles

# Cache en memoria para evitar consultas repetidas a BD
_role_id_cache: dict = {}

def _get_role_id_cached(nombre_rol: str):
    """Obtiene y cachea el ID de un rol por nombre para evitar hits continuos a BD"""
    if nombre_rol not in _role_id_cache:
        _role_id_cache[nombre_rol] = sp_obtener_roles(nombre_rol)
    return _role_id_cache[nombre_rol]


def _get_login_url_by_path():
    if request.path.startswith("/fortress_administrativo"):
        return url_for("auth.login_admin")
    if request.path.startswith("/fortress_tecnicos"):
        return url_for("auth.login_technical")
    if request.path.startswith("/sistema_cupos"):
        return url_for("auth.login_user")
    return None


def get_login_url_por_rol(role_id=None) -> str:
    """Retorna la URL de login correcta según el role_id o la ruta actual."""
    
    if role_id is None:
        role_id = session.get("role_id")

    login_url = _get_login_url_by_path()
    if login_url:
        return login_url

    admin_id = _get_role_id_cached("Admin")
    technical_id = _get_role_id_cached("Tecnico")

    if role_id is not None:
        if technical_id is not None and role_id == technical_id:
            return url_for("auth.login_technical")
        if admin_id is not None and role_id == admin_id:
            return url_for("auth.login_admin")

    return url_for("auth.login_user")