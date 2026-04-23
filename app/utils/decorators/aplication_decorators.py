from functools import wraps, lru_cache
from flask import session, abort, redirect, url_for, flash, make_response

# Conexión con BD
from app.repositories.utils_repository import *


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
                response = make_response(redirect(url_for("auth.login_user")))
                unset_jwt_cookies(response)
                session.clear()
                flash("Su sesión actual ha sido cerrada. Si no ha sido usted, realice cambio de contraseña.", "danger")
                return response
        
        return f(*args, **kwargs)
    return decorated


def acudiente_required(f):
    """Verifica que el usuario sea ACUDIENTE."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debe iniciar sesión para continuar", "warning")
            return redirect(url_for("auth.login_user"))

        acudiente_id = _get_role_id("Acudiente")

        if acudiente_id is None:
            abort(500)

        if session.get('role_id') != acudiente_id:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Bloquea el acceso a rutas del dashboard si el acudienteno tiene un estudiante registrado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Ya verificado en esta sesión — acceso directo sin consultar BD
        if session.get("estudiante_verificado"):
            return f(*args, **kwargs)

        id_acudiente = session.get("user_id")

        try:
            resultado = sp_verificar_estudiante_acudiente(id_acudiente)
            tiene_estudiante = (
                resultado
                and resultado[0].get("tiene_estudiante", 0) > 0
            )
        except Exception as e:
            # print(f"[ERROR] Decorador estudiante_requerido: {e}")
            # Ante error técnico se permite el paso para no bloquear al usuario
            tiene_estudiante = True

        if tiene_estudiante:
            # Guardar en sesión para no repetir la consulta
            session["estudiante_verificado"] = True
            return f(*args, **kwargs)

        # Sin estudiante: redirigir a registro
        flash("Debe registrar al estudiante a su cargo para continuar.", "warning")
        return redirect(url_for("aplication.register_student"))

    return decorated_function