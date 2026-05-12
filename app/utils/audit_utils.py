from app.repositories.auth_repository import *
from app.utils.database_utils import db


def Auditoria_Session(usuario, ip, evento, agent):
    """Registra eventos de sesión. Falla/Ingreso"""
    try:
        with db.transaction() as conn:
            sp_auditoria_sesion(usuario, ip, evento, agent, conn=conn)
    except Exception as e:
        print(f"[ERROR] Auditoría fallida: {e}")