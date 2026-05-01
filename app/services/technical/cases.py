# app/services/technical_cases_service.py

# FUNCIONES DE FLASK
from flask import render_template, request, session

from app.forms.technical_forms import FormFiltroTicketsTecnico
from app.repositories.technical_repository import (
    sp_technical_cases_listar,
    sp_technical_cases_metricas,
    sp_catalogo_estados_ticket,
    sp_catalogo_grados,
    sp_catalogo_tipo_afectacion,
)


# ---------------------------
# Helpers de filtrado 
# ---------------------------

def _filtrar_tickets_tecnico(tickets: list[dict], id_estado: int | None, id_grado: int | None, id_afectacion: int | None) -> list[dict]:
    """ Aplica filtros de estado, grado y afectación sobre la lista de tickets"""
    resultado = tickets

    # Filtro por estado del ticket
    if id_estado:
        resultado = [
            t for t in resultado
            if t["FK_ID_Estado_Ticket"] == id_estado
        ]

    # Filtro por grado: grado actual O próximo del estudiante
    if id_grado:
        resultado = [
            t for t in resultado
            if t.get("FK_ID_Grado_Actual") == id_grado
            or t.get("FK_ID_Grado_Proximo") == id_grado
        ]

    # Filtro por tipo de afectación
    if id_afectacion:
        resultado = [
            t for t in resultado
            if t["FK_ID_Tipo_Afectacion"] == id_afectacion
        ]

    return resultado


# ==============================================================================
# Helpers de ordenamiento
# ==============================================================================

def _insertion_sort_por_fecha_asc(tickets: list[dict]) -> list[dict]:
    """Insertion Sort ascendente por Fecha_Creacion. Se usa cuando hay filtros activos"""
    lista = list(tickets)
    for i in range(1, len(lista)):
        actual = lista[i]
        clave  = actual["Fecha_Creacion"]
        j = i - 1
        while j >= 0 and lista[j]["Fecha_Creacion"] > clave:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = actual
    return lista


def _selection_sort_por_prioridad_desc(tickets: list[dict]) -> list[dict]:
    """Selection Sort descendente por Puntaje_Prioridad. Se usa sin filtros"""
    lista = list(tickets)
    n = len(lista)
    for i in range(n):
        idx_max = i
        for j in range(i + 1, n):
            if lista[j]["Puntaje_Prioridad"] > lista[idx_max]["Puntaje_Prioridad"]:
                idx_max = j
        lista[i], lista[idx_max] = lista[idx_max], lista[i]
    return lista


# ==============================================================================
# Servicio principal
# ==============================================================================

class Cases_Service:
    """Servicio para la vista de tickets asignados al técnico autenticado"""

    def listar_tickets_tecnico(self):

        # ID del técnico autenticado (Flask-Login) 
        id_tecnico = session.get("user_id")
        

        # Leer filtros desde query string 
        id_estado = self._parse_int(request.args.get("estado"))
        id_grado = self._parse_int(request.args.get("grado"))
        id_afectacion = self._parse_int(request.args.get("afectacion"))

        # Catálogos y formulario de filtros 
        estados = sp_catalogo_estados_ticket()
        grados = sp_catalogo_grados()
        afectaciones = sp_catalogo_tipo_afectacion()

        choices_estados = [(0, "Todos los estados")] + [(e["ID_Estado_Ticket"], e["Nombre_Estado"]) for e in estados]
        choices_grados = [(0, "Todos los grados")] + [(g["ID_Grado"], g["Nombre_Grado"]) for g in grados]
        choices_afectaciones = [(0, "Todas las afectaciones")] + [(a["ID_Tipo_Afectacion"], a["Nombre_Afectacion"]) for a in afectaciones]

        form_filtro = FormFiltroTicketsTecnico(request.args)
        form_filtro.estado.choices = choices_estados
        form_filtro.grado.choices = choices_grados
        form_filtro.afectacion.choices = choices_afectaciones

        # Traer tickets del técnico desde BD 
        todos_tickets = sp_technical_cases_listar(id_tecnico)

        # Filtrar
        tickets_filtrados = _filtrar_tickets_tecnico(
            todos_tickets, id_estado, id_grado, id_afectacion
        )

        # Ordenar según si hay filtros activos o no
        hay_filtro = any([id_estado, id_grado, id_afectacion])
        if hay_filtro:
            # Con filtros: Insertion Sort por fecha ASC (orden de llegada)
            tickets_ordenados = _insertion_sort_por_fecha_asc(tickets_filtrados)
        else:
            # Sin filtros: Selection Sort por prioridad DESC (más urgentes primero)
            tickets_ordenados = _selection_sort_por_prioridad_desc(tickets_filtrados)

        # Métricas y render
        metricas = sp_technical_cases_metricas(id_tecnico)

        filtros_activos = {
            "estado": id_estado,
            "grado": id_grado,
            "afectacion": id_afectacion,
        }

        return render_template(
            "technical/cases.html",
            tickets = tickets_ordenados,
            total_tickets = len(tickets_ordenados),
            metricas = metricas,
            form_filtro = form_filtro,
            filtros = filtros_activos,
            active_page = "cases",
        )

    @staticmethod
    def _parse_int(valor: str | None) -> int | None:
        """Convierte string a int; retorna None si vacío, 0 o no numérico"""
        try:
            v = int(valor)
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None