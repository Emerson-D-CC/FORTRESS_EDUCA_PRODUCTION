import datetime
import math

from flask import render_template, request

from app.repositories.admin_repository import (
    sp_cases_exportar_todos,
    sp_cases_listar_todos,
    sp_cases_metricas,
    sp_catalogo_estados_ticket,
    sp_catalogo_grados,
    sp_catalogo_tipo_afectacion,
)
from app.forms.admin_forms import FormFiltroTickets
from app.utils.export_doc_utils import ExportarReporte

POR_PAGINA = 20

COLUMNAS_EXPORT = [
    "ID Ticket", "Estudiante", "Acudiente", "Edad",
    "Grado", "Afectación", "Estado", "Prioridad",
    "Colegio Asignado", "Técnico",
]


# ==============================================================================
# Helpers de filtrado en Python
# ==============================================================================

def _filtrar_tickets(
    registros: list[dict],
    id_estado: int | None,
    id_grado: int | None,
    id_afectacion: int | None,
) -> list[dict]:
    resultado = registros
    if id_estado:
        resultado = [r for r in resultado if r["FK_ID_Estado_Ticket"] == id_estado]
    if id_grado:
        resultado = [r for r in resultado if r["FK_ID_Grado"] == id_grado]
    if id_afectacion:
        resultado = [r for r in resultado if r["FK_ID_Tipo_Afectacion"] == id_afectacion]
    return resultado


# ==============================================================================
# Helpers de ordenamiento
# ==============================================================================

def _insertion_sort_fecha_desc(registros: list[dict]) -> list[dict]:
    """Insertion Sort DESC por Fecha_Creacion — se usa cuando hay filtros activos."""
    lista = list(registros)
    for i in range(1, len(lista)):
        actual = lista[i]
        clave = actual["Fecha_Creacion"] or datetime.datetime.min
        j = i - 1
        while j >= 0:
            clave_j = lista[j]["Fecha_Creacion"] or datetime.datetime.min
            if clave_j < clave:
                lista[j + 1] = lista[j]
                j -= 1
            else:
                break
        lista[j + 1] = actual
    return lista


def _selection_sort_prioridad_desc(registros: list[dict]) -> list[dict]:
    """Selection Sort DESC por Puntaje_Prioridad — se usa sin filtros."""
    lista = list(registros)
    n = len(lista)
    for i in range(n):
        idx_max = i
        for j in range(i + 1, n):
            if (lista[j]["Puntaje_Prioridad"] or 0) > (lista[idx_max]["Puntaje_Prioridad"] or 0):
                idx_max = j
        lista[i], lista[idx_max] = lista[idx_max], lista[i]
    return lista


# ==============================================================================
# Paginación
# ==============================================================================

def _paginar(registros: list[dict], pagina: int, por_pagina: int) -> list[dict]:
    inicio = (pagina - 1) * por_pagina
    return registros[inicio: inicio + por_pagina]


# ==============================================================================
# Servicio
# ==============================================================================

class Cases_Service:
    """Servicio para la vista de listado de todos los tickets (admin)."""

    # ------------------------------------------------------------------
    # Vista principal
    # ------------------------------------------------------------------
    def listar_todos_tickets(self):

        # Leer y sanitizar filtros desde GET
        id_estado = self._parse_int(request.args.get("estado"))
        id_grado = self._parse_int(request.args.get("grado"))
        id_afectacion = self._parse_int(request.args.get("afectacion"))
        pagina = self._parse_pagina(request.args.get("pagina"))

        # Catálogos para los <select>
        estados = sp_catalogo_estados_ticket()
        grados = sp_catalogo_grados()
        afectaciones = sp_catalogo_tipo_afectacion()

        # Poblar el formulario y pre-seleccionar opciones
        form_filtro = FormFiltroTickets(request.args, meta={"csrf": False})
        form_filtro.estado.choices = [(0, "Todos los estados")] + [(e["ID_Estado_Ticket"], e["Nombre_Estado"]) for e in estados]
        form_filtro.grado.choices = [(0, "Todos los grados")] + [(g["ID_Grado"], g["Nombre_Grado"]) for g in grados]
        form_filtro.afectacion.choices = [(0, "Todas las afectaciones")] + [(a["ID_Tipo_Afectacion"], a["Nombre_Afectacion"]) for a in afectaciones]

        # Traer todos desde BD y filtrar en Python
        todos = sp_cases_listar_todos()
        filtrados = _filtrar_tickets(todos, id_estado, id_grado, id_afectacion)

        # Ordenar según si hay filtros activos
        hay_filtro = any([id_estado, id_grado, id_afectacion])
        if hay_filtro:
            ordenados = _insertion_sort_fecha_desc(filtrados)
        else:
            ordenados = _selection_sort_prioridad_desc(filtrados)

        # Paginación
        total_tickets = len(ordenados)
        total_paginas = max(1, math.ceil(total_tickets / POR_PAGINA))
        if pagina > total_paginas:
            pagina = total_paginas

        tickets_pagina = _paginar(ordenados, pagina, POR_PAGINA)

        # Métricas (no se filtran: siempre sobre el total del sistema)
        metricas = sp_cases_metricas() or {}

        filtros_activos = {
            "estado": id_estado,
            "grado": id_grado,
            "afectacion": id_afectacion,
        }

        return render_template(
            "admin/cases.html",
            tickets = tickets_pagina,
            total_tickets = total_tickets,
            metricas = metricas,
            form_filtro = form_filtro,
            filtros = filtros_activos,
            pagina_actual = pagina,
            total_paginas = total_paginas,
            por_pagina = POR_PAGINA,
            active_page = "cases",
        )

    # ------------------------------------------------------------------
    # Exportar CSV / PDF
    # ------------------------------------------------------------------
    def exportar_tickets(self):
        formato = request.args.get("formato", "csv").lower()
        id_estado = self._parse_int(request.args.get("estado"))
        id_grado = self._parse_int(request.args.get("grado"))
        id_afectacion = self._parse_int(request.args.get("afectacion"))

        todos = sp_cases_exportar_todos()
        filtrados = _filtrar_tickets(todos, id_estado, id_grado, id_afectacion)
        ordenados = _insertion_sort_fecha_desc(filtrados) if any([id_estado, id_grado, id_afectacion]) \
                    else _selection_sort_prioridad_desc(filtrados)

        def mapeador(r):
            return {
                "ID Ticket": r["ID_Ticket"],
                "Estudiante": r["Nombre_Estudiante"],
                "Acudiente": r.get("Nombre_Acudiente", "—"),
                "Edad": f"{r.get('Edad_Estudiante', '—')} años",
                "Grado": r["Nombre_Grado"],
                "Afectación": r["Nombre_Afectacion"],
                "Estado": r["Nombre_Estado"],
                "Prioridad": r["Puntaje_Prioridad"],
                "Colegio Asignado": r.get("Colegio_Asignado") or "Sin asignar",
                "Técnico": r.get("Nombre_Tecnico") or "Sin asignar",
            }

        fila = ExportarReporte.cargar_fila(ordenados, mapeador)
        datos = fila.a_lista_datos()

        fecha = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS_EXPORT, "Solicitudes de Cupo", f"solicitudes_tickets_{fecha}")
        return ExportarReporte.csv(datos, COLUMNAS_EXPORT, f"solicitudes_tickets_{fecha}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_int(valor: str | None) -> int | None:
        try:
            v = int(valor)
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_pagina(valor: str | None) -> int:
        try:
            p = int(valor)
            return p if p >= 1 else 1
        except (TypeError, ValueError):
            return 1