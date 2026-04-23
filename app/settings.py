import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

# Obtener ruta raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar archivo .env
load_dotenv(BASE_DIR / ".env")


class Config:
    """Clase de variables globales generales"""
    SECRET_KEY =os.getenv("SECRET_KEY", "dev-secret")


class Config_Security:
    """Varibles del sistema de seguridad"""
    #reCAPCHA
    RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")

    #HASHING
    PEPPER = os.getenv("PASSWORD_PEPPER", "default-pepper")

    # MFA
    MFA_ISSUER = os.getenv("MFA_ISSUER")


class Config_JWT:
    """Variables de Jason Web Token"""
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_COOKIE_CSRF_PROTECT = False


class Config_Email:
    """Variblaes para Flask-Email"""
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "").replace(" ", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class Config_Session:
    """Variables de configuración del tiempo de una sesión"""
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    MAX_SESSION_DURATION = timedelta(hours=24)
    SESSION_MAX_ACTIVAS = int(os.getenv("SESSION_MAX_ACTIVAS", 3))
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    

class Config_DB:
    """Variables de conexión a la Base de Datos"""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_SSL = os.getenv("DB_SSL", "false").lower() == "true"

    @classmethod
    def validate(cls):
        """Lanza error si faltan variables críticas"""
        missing = [k for k, v in {
            "DB_USER": cls.DB_USER,
            "DB_PASSWORD": cls.DB_PASSWORD,
            "DB_NAME": cls.DB_NAME,
        }.items() if not v]
        if missing:
            raise EnvironmentError(f"[CONFIG] Faltan variables de entorno: {missing}")
    

class DevelopmentConfig(Config, Config_Security, Config_JWT, Config_Email, Config_Session, Config_DB):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False