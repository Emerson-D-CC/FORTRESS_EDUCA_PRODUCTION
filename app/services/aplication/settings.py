# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session

# UTILIDADES
from app.utils.database_utils import db
from app.utils.password_utils import verificar_contraseña

# CONFIGURACIONES LOCALES
from app.repositories.aplication_repository import (
    sp_configuracion_obtener_notificaciones,
    sp_configuracion_actualizar_notif_email,
    sp_configuracion_actualizar_notif_navegador,
    sp_eliminar_cuenta_completa,
    sp_validar_data_autenticacion,
)

from app.forms.aplication_forms import FormNotificacionesEmail, FormNotificacionesNavegador, FormEliminarCuenta
            
# ====================================================================================================================================================
#                                           PAGINA SETTINGS.HTML
# ====================================================================================================================================================

class General_Settings_Service:
    #  Carga inicial: GET /settings 
    
    def cargar_datos_settings(self):

        id_usuario = session.get("user_id")
        
        prefs = sp_configuracion_obtener_notificaciones(id_usuario)
 
        # Si el SP no devuelve resultados, inicializamos valores seguros
        if prefs and len(prefs) > 0:
            notif_email = bool(prefs[0]["Notificaciones_Email"])
            notif_navegador = bool(prefs[0]["Notificaciones_Navegador"])
        else:
            notif_email = False
            notif_navegador = False
 
        form_email = FormNotificacionesEmail()
        form_navegador  = FormNotificacionesNavegador()
        form_eliminar = FormEliminarCuenta()
 
        # Pre-seleccionar checkboxes según el estado guardado en BD
        form_email.notificaciones_email.data = notif_email
        form_navegador.notificaciones_navegador.data  = notif_navegador
 
        return render_template(
            "aplication/settings.html",
            form_email=form_email,
            form_navegador=form_navegador,
            form_eliminar=form_eliminar,
            notif_email_activo=notif_email,
            notif_navegador_activo=notif_navegador,
            active_page="settings",
        )
# ==========================================================================
# ACTUALIZAR NOTIFICACIONES AL CORREO

    def Email_Notif(self):
        """Procesa el formulario de notificaciones por correo electrónico"""
        
        form_email = FormNotificacionesEmail()
 
        if form_email.validate_on_submit():
            activo = 1 if form_email.notificaciones_email.data else 0
 
            try:
                id_usuario = session.get("user_id")

                sp_configuracion_actualizar_notif_email(id_usuario, activo)
 
                estado = "activadas" if activo else "desactivadas"
                flash(
                    f"Las notificaciones por correo han sido {estado} correctamente.",
                    "success"
                )
 
            except Exception:
                flash(
                    "Ocurrió un error al actualizar las notificaciones por correo. "
                    "Intenta de nuevo más tarde.",
                    "danger"
                )
        else:
            flash("Solicitud inválida. Por favor recarga la página e intenta de nuevo.", "warning")
 
        return redirect(url_for("aplication.settings"))
 

# ==========================================================================
# ACTUALIZAR NOTIFICACIONES EN EL NAVEGADOR

    def Browser_Notif(self):
        """Procesa el formulario de notificaciones del navegador"""
        
        # Cargar formularios
        form_navegador = FormNotificacionesNavegador()

        if form_navegador.validate_on_submit():
            activo = 1 if form_navegador.notificaciones_navegador.data else 0

            try:
                id_usuario = session.get("user_id")
                sp_configuracion_actualizar_notif_navegador(id_usuario, activo)

                estado = "activadas" if activo else "desactivadas"
                flash(
                    f"Las notificaciones del navegador han sido {estado} correctamente.",
                    "success"
                )

            except Exception:
                flash(
                    "Ocurrió un error al actualizar las notificaciones del navegador. "
                    "Intenta de nuevo más tarde.",
                    "danger"
                )
        else:
            flash("Solicitud inválida. Por favor recarga la página e intenta de nuevo.", "warning")

        return redirect(url_for("aplication.settings"))


# ==========================================================================
# ELIMINAR CUENTA
    
    def Delete_Account(self):
        form_eliminar = FormEliminarCuenta()
        
        if form_eliminar.validate_on_submit():
            id_usuario = session.get("user_id")
            username = session.get("username_login")
            
            if not id_usuario or not username:
                flash("Sesión no válida. Por favor inicia sesión de nuevo.", "danger")
                return redirect(url_for("auth.login_user"))
            
            password = form_eliminar.contraseña.data

            try:
                # 1. Obtener hash y validar contraseña
                data_user = sp_validar_data_autenticacion(username)  # igual que en Login
                if not data_user:
                    raise Exception("Usuario no encontrado")

                hash_almacenado = data_user[0].get("Contraseña_Hash")
                if not hash_almacenado:
                    raise Exception("Hash no disponible")

                if not self._validar_usuario(password, hash_almacenado):
                    flash("Contraseña incorrecta. No se procedió con la eliminación.", "danger")
                    return redirect(url_for("aplication.settings"))
                
                # 2. Proceder con la eliminación lógica
                ip = request.remote_addr or ""
                user_agent = request.headers.get("User-Agent", "")
                
                with db.transaction() as conn:
                    sp_eliminar_cuenta_completa(id_usuario, ip, user_agent, conn=conn)
                
                session.clear()
                flash("Cuenta eliminada correctamente. Hasta pronto.", "success")
                return redirect(url_for("auth.login_user"))

            except Exception as e:
                print(f"[ERROR] eliminar_cuenta: {e}")
                flash("Error de sistema al procesar la solicitud.", "danger")
                return redirect(url_for("aplication.settings"))
            
        flash("Debe ingresar su contraseña para confirmar.", "warning")
        return redirect(url_for("aplication.settings"))

    def _validar_usuario(self, password, hash_almacenado):
        try:
            return verificar_contraseña(password, hash_almacenado)
        except Exception as e:
            print(f"[ERROR] _validar_usuario: {e}")
            return False