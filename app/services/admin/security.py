from flask import render_template

from app.services.core.core_security import SharedSecurityService
from app.forms.admin_forms import FormCambiarcontraseña


class Security_Settings_Service:
    """Servicio de seguridad para el módulo Admin (contraseña + sesiones)."""

    _ENDPOINT = "admin.security"

    def __init__(self):
        self._shared = SharedSecurityService(self._ENDPOINT, FormCambiarcontraseña)

    #  Vista principal 

    def cargar_informacion_seguridad(self):
        form_password = FormCambiarcontraseña()
        sesiones = self._shared.listar_sesiones()

        return render_template(
            "admin/security.html",
            form_password=form_password,
            sesiones=sesiones,
            active_page="security",
        )

    #  Contraseña 

    def Change_Password(self):
        return self._shared.change_password()

    #  Sesiones 

    def Session_Handler_Service(self):
        return self._shared.listar_sesiones()

    def cerrar_sesiones(self):
        return self._shared.cerrar_todas_sesiones()

    def cerrar_sesion(self, jti_sesion: str):
        return self._shared.cerrar_sesion(jti_sesion)