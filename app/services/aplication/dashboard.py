# FUNCIONES DE FLASK
from flask import render_template, session

# CONFIGURACIONES LOCALES
from app.forms.aplication_forms import *
from app.repositories.aplication_repository import *

# ====================================================================================================================================================
#                                           PÁGINA INDEX.HTML
# ====================================================================================================================================================

# Mapa de prioridad numérica a etiqueta visual
_PRIORIDAD_LABEL = {
    range(0,  30):  ("Baja","danger", "fa-arrow-down"),
    range(30, 60):  ("Media", "danger", "fa-equals"),
    range(60, 85):  ("Alta", "danger", "fa-arrow-up"),
    range(85, 9999):("Crítica","danger", "fa-exclamation-circle"),
}

def _resolver_prioridad(puntaje: int) -> tuple[str, str, str]:
    """Convierte el puntaje numérico en (etiqueta, color_badge, icono)"""
    for rango, datos in _PRIORIDAD_LABEL.items():
        if puntaje in rango:
            return datos
    return ("Media", "warning", "fa-equals")


# Pasos del proceso en orden — reutiliza la misma lógica del módulo de tickets
_PASOS_PROCESO = [
    {
        "label": "Solicitud Enviada",
        "icono": "fa-paper-plane",
        "estado_bd": "Abierto"
    },
    {
        "label": "En Revisión",
        "icono": "fa-eye",
        "estado_bd": "En Revisión"
    },
    {
        "label": "Validación Documentos",
        "icono": "fa-clipboard-check",
        "estado_bd": "Validación de Documentos"
    },
    {
        "label": "Asignación de Cupo",
        "icono": "fa-school",
        "estado_bd": "Asignación de Cupo"
    },
    {
        "label": "Confirmación Final",
        "icono": "fa-flag-checkered",
        "estado_bd": "Confirmación Final"
    },
]

def _construir_pasos(nombre_estado: str | None) -> list[dict]:
    """Devuelve pasos con estado: 'done', 'active' o '' (pendiente)."""
    if not nombre_estado:
        return [dict(p, cls="") for p in _PASOS_PROCESO]

    estados_bd = [p["estado_bd"] for p in _PASOS_PROCESO]
    try:
        idx_actual = estados_bd.index(nombre_estado)
    except ValueError:
        idx_actual = 0

    pasos = []
    for i, paso in enumerate(_PASOS_PROCESO):
        if i < idx_actual:
            pasos.append(dict(paso, cls="done"))
        elif i == idx_actual:
            pasos.append(dict(paso, cls="active"))
        else:
            pasos.append(dict(paso, cls=""))
    return pasos


class Dashboard_Service:

    def cargar_datos_dashboard(self):
        user_id = session["user_id"]
        resumen = sp_dashboard_resumen_acudiente(user_id)

        # Sin datos → el acudiente no tiene estudiante ni tickets aún
        pasos = []
        prioridad = None

        if resumen and resumen.get("ID_Ticket"):
            pasos  = _construir_pasos(resumen.get("Nombre_Estado"))
            prioridad = _resolver_prioridad(resumen.get("Puntaje_Prioridad", 0))

        return render_template(
            "aplication/index.html",
            resumen = resumen,
            pasos = pasos,
            prioridad = prioridad,
            mostrar_modal_estudiante = not resumen,
            actiive_page = 'home',
        )
