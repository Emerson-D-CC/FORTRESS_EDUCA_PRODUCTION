# FUNCIONES DE FLASK
from flask import Flask, redirect, url_for
# FUNCIONES DE FLASK
from flask_wtf.csrf import CSRFProtect
# FUNCIONES DE FLASK
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from app.settings import Config_Security, Config_JWT, Config_Email, Config_Session, DevelopmentConfig

# Importación de blueprints
from app.blueprints.home.routes import home_bp
from app.blueprints.auth.routes import auth_bp
from app.blueprints.aplication.routes import aplication_bp
from app.blueprints.tickets.routes import tickets_bp
from app.blueprints.admin.routes import admin_bp
from app.blueprints.technical.routes import technical_bp

# Funciones para el manejo de la sesion
from app.security.jwt_controller import handle_unauthorized_error, handle_expired_error, handle_invalid_error
from app.security.session_controller import controlar_sesion

from app.utils.extensions_utils import mail, register_context_processors
from app.controllers.error_controller import register_error_handlers


# Cargar variables de entorno desde .env
load_dotenv()

def create_app():

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Cargar configuración
    app.config.from_object(DevelopmentConfig)
    app.config.from_object(Config_Security)
    app.config.from_object(Config_JWT)
    app.config.from_object(Config_Email)
    app.config.from_object(Config_Session)

    # Controlador de sesiones
    controlar_sesion(app)

    # Inicializar extensiones
    mail.init_app(app)
    
    csrf = CSRFProtect()    
    csrf.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(aplication_bp)
    app.register_blueprint(tickets_bp)    
    app.register_blueprint(admin_bp)
    app.register_blueprint(technical_bp)

    # Controlador de errores 
    register_error_handlers(app)
    
    # Datos del usuario/admin requiridos en header 
    register_context_processors(app)
    
    # Manejador en caso de fallo del token JWT
    jwt = JWTManager(app)
    jwt.unauthorized_loader(handle_unauthorized_error)
    jwt.expired_token_loader(handle_expired_error)
    jwt.invalid_token_loader(handle_invalid_error)
    
    @app.after_request
    def add_no_cache_headers(response):
        if response.content_type and response.content_type.startswith("text/html"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
    
    # Inicializar en pagina principal
    @app.route("/")
    def index():
        return redirect(url_for('home.public_home'))
    
    return app