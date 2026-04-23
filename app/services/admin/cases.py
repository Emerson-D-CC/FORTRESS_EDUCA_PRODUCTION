from flask import render_template, request
 
from app.repositories.admin_repository import sp_cases_listar_todos, sp_cases_metricas, sp_catalogo_estados_ticket, sp_catalogo_grados, sp_catalogo_tipo_afectacion

class Cases_Service:
    """Servicio para la vista de listado de todos los tickets (admin)."""
 
    def listar_todos_tickets(self):
        """Obtiene los tickets aplicando los filtros enviados por GET, las métricas para las tarjetas y los catálogos para los <select>"""
    
        # =====================================================
        # SOLICITUD GET — Leer filtros desde la query string 

        id_estado = self._parse_int(request.args.get("estado"))
        id_grado = self._parse_int(request.args.get("grado"))
        id_afectacion = self._parse_int(request.args.get("afectacion"))
 
        # Consultar datos 
        tickets = sp_cases_listar_todos(id_estado, id_grado, id_afectacion)
        metricas = sp_cases_metricas() or {}
 
        # Catálogos para los <select> de filtros
        estados = sp_catalogo_estados_ticket()
        grados = sp_catalogo_grados()
        afectaciones = sp_catalogo_tipo_afectacion()
 
        # Valores seleccionados (para mantener el estado del formulario
        filtros_activos = {
            "estado": id_estado,
            "grado": id_grado,
            "afectacion": id_afectacion,
        }
 
        return render_template(
            "admin/cases.html",
            tickets = tickets,
            metricas = metricas,
            estados = estados,
            grados = grados,
            afectaciones = afectaciones,
            filtros = filtros_activos,
            active_page = "cases",
        )
 
    @staticmethod
    def _parse_int(valor: str | None) -> int | None:
        """Convierte un string a int; retorna None si está vacío o no es numérico."""
        try:
            v = int(valor)
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None