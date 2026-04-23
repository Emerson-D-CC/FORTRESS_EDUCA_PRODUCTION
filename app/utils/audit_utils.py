from app.repositories.auth_repository import *
from app.utils.database_utils import db


def Auditoria_Session(usuario, ip, evento, agent):
    """Registra eventos de sesión. Falla/Ingreso"""
    try:
        sp_auditoria_sesion(usuario, ip, evento, agent)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Auditoría fallida: {e}")