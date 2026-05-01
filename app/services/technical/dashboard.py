# FUNCIONES DE FLASK
from flask import session, render_template

from app.repositories.technical_repository import sp_technical_dashboard_metricas, sp_technical_cases_listar_asignados, sp_technical_dashboard_chart_actividad

# Traducción de abreviaturas de días (MySQL usa inglés por defecto)
DIAS_ES = {
    'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié',
    'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sáb', 'Sun': 'Dom'
}

# Fallback cuando la BD no retorna datos para el gráfico
CHART_FALLBACK = {
    "labels": ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
    "nuevas_solicitudes": [0, 0, 0, 0, 0, 0, 0],
    "cupos_asignados": [0, 0, 0, 0, 0, 0, 0],
}


class Dashboard_Service:
    """Servicio que construye el contexto del dashboard del técnico."""

    def cargar_dashboard(self):
        # Datos del técnico desde sesión 
        user = session.get('user', {})
        id_usuario = session.get('user_id')
        nombre = user.get('nombre', 'Técnico')

        resumen = {"Nombre_Technical": nombre}

        # Métricas propias del técnico 
        raw_metricas = sp_technical_dashboard_metricas(id_usuario)

        # call_procedure puede devolver dict o lista[dict]; normalizamos
        if isinstance(raw_metricas, list) and raw_metricas:
            metricas = raw_metricas[0]
        elif isinstance(raw_metricas, dict):
            metricas = raw_metricas
        else:
            metricas = {}

        # Últimas solicitudes asignadas al técnico 
        ultimas_solicitudes = sp_technical_cases_listar_asignados(id_usuario)

        # Datos del gráfico de actividad 
        actividad_raw = sp_technical_dashboard_chart_actividad(id_usuario)

        if actividad_raw:
            chart_data = {
                "labels": [
                    DIAS_ES.get(fila.get('label', ''), fila.get('label', ''))
                    for fila in actividad_raw
                ],
                "nuevas_solicitudes": [
                    int(fila.get('nuevas_solicitudes', 0)) for fila in actividad_raw
                ],
                "cupos_asignados": [
                    int(fila.get('cupos_asignados', 0)) for fila in actividad_raw
                ],
            }
        else:
            chart_data = CHART_FALLBACK

        # Render 
        return render_template(
            "technical/dashboard.html",
            resumen=resumen,
            metricas=metricas,
            ultimas_solicitudes=ultimas_solicitudes,
            chart_data=chart_data,
            active_page="dashboard",
        )