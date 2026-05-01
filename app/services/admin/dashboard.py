# FUNCIONES DE FLASK
from flask import session, render_template
from app.repositories.admin_repository import (
    sp_dashboard_metricas, 
    sp_cases_listar_todos, 
    sp_dashboard_chart_actividad,
)

# Mapa de días en español para el gráfico
DIAS_ES = {
    'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié',
    'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sáb', 'Sun': 'Dom'
}

class Dashboard_Service:
    """Servicio para la vista de dashboard del admin"""

    def cargar_dashboard(self):
        """Obtiene las métricas y datos necesarios para el dashboard"""

        # --- Métricas principales ---
        resultado_metricas = sp_dashboard_metricas()
        if isinstance(resultado_metricas, list) and len(resultado_metricas) > 0:
            metricas = resultado_metricas[0]
        elif isinstance(resultado_metricas, dict):
            metricas = resultado_metricas
        else:
            metricas = {}

        # --- Datos del admin desde sesión ---
        resumen = {
            "Nombre_Admin": session.get('user', {}).get('nombre', 'Admin')
        }

        # --- Últimas 5 solicitudes ---
        todas_solicitudes = sp_cases_listar_todos()
        ultimas_solicitudes = todas_solicitudes[:5] if todas_solicitudes else []

        # --- Datos reales para el gráfico ---
        actividad_raw = sp_dashboard_chart_actividad()

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
                ]
            }
        else:
            # Fallback con ceros si la DB no retorna datos
            chart_data = {
                "labels": ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                "nuevas_solicitudes": [0, 0, 0, 0, 0, 0, 0],
                "cupos_asignados":    [0, 0, 0, 0, 0, 0, 0]
            }

        return render_template(
            "admin/dashboard.html",
            resumen=resumen,
            metricas=metricas,
            ultimas_solicitudes=ultimas_solicitudes,
            chart_data=chart_data,
            active_page="dashboard"
        )