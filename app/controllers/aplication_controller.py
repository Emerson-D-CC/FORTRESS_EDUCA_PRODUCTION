from app.services.aplication.dashboard import Dashboard_Service
from app.services.aplication.ticket_request import Ticket_Request_Service
from app.services.aplication.ticket_status import Ticket_Detail_Service
from app.services.aplication.register_student import Register_Student_Service
from app.services.aplication.profile import Profile_Data_Service
from app.services.aplication.security import Security_Settings_Service
from app.services.aplication.settings import General_Settings_Service

class AplicationController:
    """Controlador de funciones para la aplicación (Parte de Usuario)"""
    
    def __init__(self):
        self.service_dasboard = Dashboard_Service()
        self.service_ticket = Ticket_Request_Service()
        self.service_ticket_d = Ticket_Detail_Service()
        self.service_profile = Profile_Data_Service()
        self.service_student = Register_Student_Service()
        self.service_security = Security_Settings_Service()
        self.service_settings = General_Settings_Service()
    
    # PANEL PRINCIPAL
    def dashboard(self):
        return self.service_dasboard.cargar_datos_dashboard()

    # NUEVA SOLICITUD (TICKET)
    def ticket_request(self):
        return self.service_ticket.Crear_Ticket()

    # SEGUIMIENTO DE SOLICITUDES DE CUPO (TICKETS)
    def ticket_status(self):
        return self.service_ticket_d.listar_tickets()

    def ticket_detail(self, id_ticket):
        return self.service_ticket_d.cargar_datos_ticket(id_ticket)

    def ticket_detail_download_doc(self, id_ticket, id_doc):
        return self.service_ticket_d.descargar_doc(id_ticket, id_doc)

    def ticket_detail_coment(self, id_ticket):
        return self.service_ticket_d.agregar_comentario(id_ticket)

    # REGISTRO ESTUDIANTE
    def register_student(self):
        return self.service_student.registrar()

    # PERFIL USUARIO
    def profile_user(self):
        return self.service_profile.cargar_datos_perfil()

    # SEGURIDAD
    def security(self):
        return self.service_security.cargar_informacion_seguridad()
        
        # CAMBIAR CONTRASEÑA
    def security_change_password(self):
        return self.service_security.Change_Password()
        
        # MFA CONFIGURACION
    def security_mfa(self):
        return self.service_security.MFA_Activation()

    def security_mfa_confirm(self):
        return self.service_security.mfa_activacion()

    def security_mfa_disable(self):
        return self.service_security.mfa_desactivar()
    
        # SESION CONTROLADOR
    def security_session_one(self, jti_sesion):
        return self.service_security.cerrar_sesion(jti_sesion)
    
    def security_session_all(self):
        return self.service_security.cerrar_sesiones()    

    # AJUSTES
    def settings(self):
        return self.service_settings.cargar_datos_settings()

        # PERFERENCIA DE NOTIFICACIONES
    def settings_notif_email(self):
        return self.service_settings.Email_Notif()

    def settings_notif_browser(self):
        return self.service_settings.Browser_Notif()

        # ELMINAR CUENTA
    def settings_delete_account(self):
        return self.service_settings.Delete_Account()