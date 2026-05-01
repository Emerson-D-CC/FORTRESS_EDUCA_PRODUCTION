# FUNCIONES DE FLASK
from flask import render_template, request
from werkzeug.exceptions import HTTPException

# DECLARACIÓN DE CONSTANTES

    # Errores especificos validados por es sistema
ERROR_CODES = [400, 401, 403, 404, 405, 410, 500, 502, 503, 504]

    # Información del error enviada a la plantilla error.html
ERROR_CONFIG = {
    400: {
        "title": "Solicitud Incorrecta",
        "description": "La solicitud enviada es inválida. Verifica los datos.",
        "icon": "fas fa-exclamation-circle",
        "color": "text-warning",
    },
    401: {
        "title": "No Autorizado",
        "description": "Debes iniciar sesión para acceder.",
        "icon": "fas fa-lock",
        "color": "text-danger",
    },
    403: {
        "title": "Acceso Denegado",
        "description": "No tienes permisos para acceder a este recurso.",
        "icon": "fas fa-ban",
        "color": "text-danger",
    },
    404: {
        "title": "Página No Encontrada",
        "description": "El recurso solicitado no existe.",
        "icon": "fas fa-search",
        "color": "text-secondary",
    },
    405: {
        "title": "Metodo No Permitido",
        "description": "Este método no está permitido para la URL solicitada.",
        "icon": "fas fa-ban",
        "color": "text-secondary",
    },
    410: {
        "title": "Recurso Eliminado",
        "description": "Este recurso ya no está disponible.",
        "icon": "fas fa-trash",
        "color": "text-muted",
    },
    500: {
        "title": "Error Interno",
        "description": "Ocurrió un error inesperado.",
        "icon": "fas fa-server",
        "color": "text-danger",
    },
    502: {
        "title": "Error de Conexión",
        "description": "El servidor recibió una respuesta inválida.",
        "icon": "fas fa-plug",
        "color": "text-warning",
    },
    503: {
        "title": "Servicio No Disponible",
        "description": "El servidor está temporalmente fuera de servicio.",
        "icon": "fas fa-tools",
        "color": "text-warning",
    },
    504: {
        "title": "Tiempo de Espera Agotado",
        "description": "El servidor tardó demasiado en responder.",
        "icon": "fas fa-clock",
        "color": "text-warning",
    },
}


# LAYOUT DINÁMICO SEGÚN APARTADO
def get_layout_for_request():
    path = request.path

    if path.startswith("/admin"):
        return "layout_admin.html"
    elif path.startswith("/dashboard"):
        return "layout_aplication.html"
    return "layout_public.html"


# RENDER CENTRALIZADO
def render_error(e, code=None, custom_message=None):

    layout = get_layout_for_request()
    error_code = code if code else getattr(e, "code", 500)

    config = ERROR_CONFIG.get(error_code, {
        "title": "Error",
        "description": "Ocurrió un problema inesperado.",
        "icon": "fas fa-exclamation-triangle",
        "color": "text-danger",
    })

    return render_template(
        "errors/error.html",
        layout=layout,
        error_code=error_code,
        error_title=config["title"],
        error_description=custom_message or getattr(e, "description", None) or config["description"],
        error_icon=config["icon"],
        error_color=config["color"],
    ), error_code


# FACTORY DE HANDLERS
def make_handler(code):
    def handler(e):
        return render_error(e, code=code)
    return handler


# REGISTRO DE HANDLERS
def register_error_handlers(app):

    # Handlers específicos
    for code in ERROR_CODES:
        app.register_error_handler(code, make_handler(code))

    # HTTPException (otros códigos no definidos)
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return render_error(e)

    # Excepciones generales (errores inesperados)
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return render_error(
            e,
            code=500,
            custom_message="Error interno inesperado."
        )

