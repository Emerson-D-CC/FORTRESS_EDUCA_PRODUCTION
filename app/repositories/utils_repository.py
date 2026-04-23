from app.utils.database_utils import db


# ====================================================================================================================================================
#                                           DECORADORES / JWT
# ====================================================================================================================================================
 
# Decorador lru_cache
def sp_obtener_roles(nombre_rol):
    try:

        resultado = db.call_procedure("sp_tbl_rol_consultar_nombre", (nombre_rol,)) or []

        if not resultado:
            print(f"[WARNING] Rol '{nombre_rol}' no encontrado en BD")
            return None

        return resultado[0]["ID_Rol"]

    except Exception as e:
        print(f"[ERROR] No se pudo consultar rol '{nombre_rol}': {e}")
        return None

# Decorador login_required
def sp_verificar_jti(jti):
    """Verifica si un JTI está activo (para token blacklist)."""
    return db.call_procedure(
        "sp_tbl_sesion_activa_verificar_jti",
        (jti,),
        commit=False
    )


# Decorador 
def sp_verificar_estudiante_acudiente(id_acudiente):
    """Retorna {'total_estudiantes': N} — si N > 0 el acudiente ya tiene al menos uno."""
    resultado = db.call_procedure(
        "sp_tbl_estudiante_verificar_por_acudiente", (id_acudiente,)
    )
    return resultado[0] if resultado else {"total_estudiantes": 0}


# ====================================================================================================================================================
#                                           SESSION_CONTROLER
# ====================================================================================================================================================

def sp_cerrar_sesion(jti):
    """Marca como inactiva una sesión por su JTI."""
    return db.call_procedure(
        "sp_tbl_sesion_activa_cerrar_sesion",
        (jti,),
        commit=False
    )
