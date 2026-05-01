# FUNCIONES DE FLASK
from flask import make_response, render_template

def render_no_cache(template: str, **ctx):
    """Renderiza una plantilla con cabeceras que impiden que el navegador 
    almacene la respuesta en caché o la muestre al navegar hacia atrás.
    """
    
    resp = make_response(render_template(template, **ctx))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    
    return resp