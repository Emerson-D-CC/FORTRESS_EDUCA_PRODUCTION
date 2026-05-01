from app.services.technical.dashboard import Dashboard_Service
from app.services.technical.cases import Cases_Service
from app.services.technical.history import History_Service
from app.services.technical.security import Security_Settings_Service


class TechnicalController:
    """Controlador de funciones para la parte de tecnicos"""

    def __init__(self):
        self.dashboard_service = Dashboard_Service()        
        self.cases_service = Cases_Service()
        self.history_service = History_Service()
        self.security_service = Security_Settings_Service()
        
    # DASHBOARD
    def dashboard(self):
        return self.dashboard_service.cargar_dashboard()
        
    # CASES
    def cases(self):
        return self.cases_service.listar_tickets_tecnico()
    
    # HISTORY
    def history(self):
        return self.history_service.listar_historial()

    def history_export(self):
        return self.history_service.exportar_historial()    
    
    # SEGURIDAD
    def security(self):
        return self.security_service.cargar_informacion_seguridad()
      
        # CAMBIAR CONTRASEÑA
    def security_change_password(self):
        return self.security_service.Change_Password()
    
        # SESION CONTROLADOR
    def security_session_one(self, jti_sesion):
        return self.security_service.cerrar_sesion(jti_sesion)
    
    def security_session_all(self):
        return self.security_service.cerrar_sesiones()