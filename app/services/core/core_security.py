# SERVICIOS DE FLASK
from flask import request, redirect, url_for, flash, session
from flask_jwt_extended import get_jwt, verify_jwt_in_request
# UTILIDADES
from app.utils.database_utils import db
from app.utils.password_utils import hashear_contraseña, verificar_contraseña

from app.repositories.core_repository import (
    sp_validar_data_user,
    sp_validar_data_autenticacion,
    sp_exito_login,
    sp_cambiar_contraseña_perfil,
    sp_listar_sesiones,
    sp_cerrar_sesion,
    sp_cerrar_todas_sesiones,
)


class SharedSecurityService:
    """Servicio compartido de seguridad (contraseña + sesiones)"""

    def __init__(self, security_endpoint: str, form_class):
        self.security_endpoint = security_endpoint
        self.form_class = form_class

    #  JWT seguro 

    def _get_jti_actual(self) -> str:
        """Obtiene el JTI del token activo de forma segura"""
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            return claims.get("jti", "") if claims else ""
        except Exception as e:
            print(f"[WARN] _get_jti_actual: {e}")
            return ""

    #  Contraseña 

    def change_password(self):
        """Gestiona el cambio de contraseña. Llamar desde la ruta POST"""
        form = self.form_class()
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")
        id_usuario = session.get("user_id")
        username = session.get("username_login")

        if not form.validate_on_submit():
            errores = "; ".join(
                msg for msgs in form.errors.values() for msg in msgs
            )
            flash(errores, "danger")
            return redirect(url_for(self.security_endpoint))

        contraseña_actual = form.contraseña_actual.data
        nueva_contraseña = form.nueva_contraseña.data

        try:
            if not sp_validar_data_user(username):
                flash("Sesión inválida. Por favor inicie sesión nuevamente.", "danger")
                return redirect(url_for(self.security_endpoint))

            if not self._validar_usuario(username, contraseña_actual):
                flash("La contraseña actual no es correcta.", "danger")
                return redirect(url_for(self.security_endpoint))

            nuevo_hash = hashear_contraseña(nueva_contraseña)
            sp_cambiar_contraseña_perfil(id_usuario, nuevo_hash, ip, user_agent)
            db.commit()
            flash("Contraseña actualizada correctamente.", "success")

        except Exception as e:
            db.rollback()
            print(f"[ERROR] change_password [{self.security_endpoint}]: {e}")
            flash("Error interno. Intente nuevamente.", "danger")

        return redirect(url_for(self.security_endpoint))

    def _validar_usuario(self, username: str, password_ingresada: str) -> bool:
        """Valida credenciales contra BD. Retorna True si son correctas."""
        try:
            user_data = sp_validar_data_autenticacion(username)
            if not user_data:
                return False

            id_usuario = user_data[0].get("ID_Usuario")
            hash_db = user_data[0].get("Contraseña_Hash")

            if not hash_db:
                return False

            if verificar_contraseña(password_ingresada, hash_db):
                sp_exito_login(id_usuario)
                return True

            return False

        except Exception as e:
            print(f"[ERROR] _validar_usuario: {e}")
            return False

    #  Sesiones 

    def listar_sesiones(self) -> list:
        """Consulta y formatea las sesiones activas del usuario en sesión."""
        id_usuario = session.get("user_id")
        try:
            raw = sp_listar_sesiones(id_usuario)
            jti_actual = self._get_jti_actual()

            sesiones = []
            for s in (raw or []):
                sesiones.append({
                    "id":          s["ID_Sesion"],
                    "JTI":         s["JTI"],
                    "dispositivo": s.get("Dispositivo") or "Desconocido",
                    "ip":          s.get("IP") or "—",
                    "inicio":      s["Fecha_Inicio"].strftime("%d/%m/%Y %H:%M")
                                   if s.get("Fecha_Inicio") else "—",
                    "ultimo":      s["Ultimo_Acceso"].strftime("%d/%m/%Y %H:%M")
                                   if s.get("Ultimo_Acceso") else "—",
                    "es_actual":   s["JTI"] == jti_actual,
                })

            session["sesiones_activas"] = sesiones
            return sesiones

        except Exception as e:
            print(f"[ERROR] listar_sesiones [{self.security_endpoint}]: {e}")
            return []

    def cerrar_todas_sesiones(self):
        """Cierra todas las sesiones excepto la actual."""
        id_usuario = session.get("user_id")
        try:
            jti_actual = self._get_jti_actual()
            sp_cerrar_todas_sesiones(id_usuario, jti_actual)
            db.commit()
            flash("Todas las demás sesiones han sido cerradas.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR] cerrar_todas_sesiones [{self.security_endpoint}]: {e}")
            flash("Error al cerrar sesiones. Intente nuevamente.", "danger")

        return redirect(url_for(self.security_endpoint))

    def cerrar_sesion(self, jti_sesion: str):
        """Cierra una sesión específica por JTI."""
        id_usuario = session.get("user_id")
        try:
            sesiones = sp_listar_sesiones(id_usuario) or []
            sesion = next((s for s in sesiones if s["JTI"] == jti_sesion), None)

            if not sesion:
                flash("Sesión no encontrada.", "warning")
                return redirect(url_for(self.security_endpoint))

            jti_actual = self._get_jti_actual()
            if jti_sesion == jti_actual:
                flash("No puede cerrar su sesión actual desde aquí.", "danger")
                return redirect(url_for(self.security_endpoint))

            sp_cerrar_sesion(jti_sesion)
            db.commit()
            flash("Sesión cerrada correctamente.", "success")

        except Exception as e:
            db.rollback()
            print(f"[ERROR] cerrar_sesion [{self.security_endpoint}]: {e}")
            flash("Error al cerrar sesión. Intente nuevamente.", "danger")

        return redirect(url_for(self.security_endpoint))