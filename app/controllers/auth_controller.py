from app.services.auth.login_user import Login_User_Service
from app.services.auth.login_admin import Login_Admin_Service
from app.services.auth.login_technical import Login_Technical_Service
from app.services.auth.verify_mfa import Verify_MFA_Service
from app.services.auth.config_mfa import Config_MFA_Service
from app.services.auth.password_recovery import Password_Recovery_Service
from app.services.auth.register  import Register_Service

class AuthController:
    """Controlador intermediario entre service y routes"""
    
    # Constructor de la clase
    def __init__(self):
        self.service_login_us = Login_User_Service()
        self.service_login_ad = Login_Admin_Service()
        self.service_login_tec = Login_Technical_Service()
        self.service_verify_mfa = Verify_MFA_Service()
        self.service_config_mfa = Config_MFA_Service()
        self.service_password = Password_Recovery_Service()
        self.service_register = Register_Service()

    # LOGIN
    def login(self):
        return self.service_login_us.Login_User()

    def login_ad(self):
        return self.service_login_ad.Login_Admin()

    def login_tec(self):
        return self.service_login_tec.Login_Technical()

    # LOGOUT
    def logout(self):
        return self.service_login_us.Logout()

    def logout_ad(self):
            return self.service_login_ad.Logout()
        
    def logout_tec(self):
            return self.service_login_tec.Logout()    

    # MFA
        # VERIFICAR MFA
    def verify_mfa(self):
        return self.service_verify_mfa.Verify_MFA()

        # CONDIGURAR MFA
    def config_mfa(self):
        return self.service_config_mfa.Config_MFA()

    def verify_config_mfa(self):
        return self.service_config_mfa.Verify_Config_MFA()

    # RECUPERACIÓN DE CONTRASEÑA
    def recover_password_code(self):
        return self.service_password.Password_Recovery()

    def recover_password_verify(self):
        return self.service_password.Verify_Code()
    
    def recover_password_new(self):
        return self.service_password.New_Password()

    # REGISTRO
    def register(self):
        return self.service_register.Register()
    