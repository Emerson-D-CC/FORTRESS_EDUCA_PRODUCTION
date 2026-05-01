import math
import datetime

from flask import render_template, request, session

from app.repositories.technical_repository import (
    sp_technical_history_listar_todos,
    sp_technical_history_exportar,
)
from app.utils.export_doc_utils import ExportarReporte


# ==============================================================================
# Constantes (idénticas al módulo admin)
# ==============================================================================

TIPOS_EVENTO = [
    ("Nueva Solicitud",  "Nueva Solicitud de Cupo"),
    ("Comentario",       "Comentario"),
    ("Cambio Estado",    "Cambio de Estado"),
    ("Documento Subido", "Documento Subido"),
    ("Cambio Tecnico",   "Cambio de Técnico"),
    ("Cupo Asignado",    "Asignación de Cupo"),
    ("Cierre Solicitud", "Cierre de Solicitud"),
]

POR_PAGINA = 20
COLUMNAS = ["ID", "Fecha y Hora", "Tipo Evento", "Ticket", "Detalle", "Visibilidad"]
_TIPOS_VALIDOS = {v for v, _ in TIPOS_EVENTO}


# ==============================================================================
# Helpers de filtrado
# ==============================================================================

def _filtrar_auditoria_tecnico(registros: list[dict], tipo_evento: str | None, fecha_desde: str | None, fecha_hasta: str | None) -> list[dict]:
    """Aplica los tres filtros sobre la lista ya reducida al técnico"""
    resultado = registros

    # Filtro por tipo de evento
    if tipo_evento:
        resultado = [
            r for r in resultado
            if r["Tipo_Evento"] == tipo_evento
        ]

    # Convertir strings a date una sola vez fuera del loop
    dt_desde = _parse_fecha(fecha_desde)
    dt_hasta = _parse_fecha(fecha_hasta)

    if dt_desde:
        resultado = [
            r for r in resultado
            if r["Fecha_Comentario"] and r["Fecha_Comentario"].date() >= dt_desde
        ]

    if dt_hasta:
        resultado = [
            r for r in resultado
            if r["Fecha_Comentario"] and r["Fecha_Comentario"].date() <= dt_hasta
        ]

    return resultado


# ==============================================================================
# Helpers de ordenamiento
# ==============================================================================

def _insertion_sort_fecha_desc(registros: list[dict]) -> list[dict]:
    """Insertion Sort descendente por Fecha_Comentario. Se usa cuando hay filtros activos"""
    lista = list(registros)
    for i in range(1, len(lista)):
        actual = lista[i]
        clave = actual["Fecha_Comentario"] or datetime.datetime.min
        j = i - 1
        while j >= 0:
            clave_j = lista[j]["Fecha_Comentario"] or datetime.datetime.min
            if clave_j < clave: # DESC: el mayor (más reciente) sube
                lista[j + 1] = lista[j]
                j -= 1
            else:
                break
        lista[j + 1] = actual
    return lista


def _selection_sort_fecha_desc(registros: list[dict]) -> list[dict]:
    """Selection Sort descendente por Fecha_Comentario. Se usa sin filtros"""
    lista = list(registros)
    n = len(lista)
    for i in range(n):
        idx_max = i
        for j in range(i + 1, n):
            fecha_j = lista[j]["Fecha_Comentario"] or datetime.datetime.min
            fecha_max = lista[idx_max]["Fecha_Comentario"] or datetime.datetime.min
            if fecha_j > fecha_max:
                idx_max = j
        lista[i], lista[idx_max] = lista[idx_max], lista[i]
    return lista


# ==============================================================================
# Paginación en Python
# ==============================================================================

def _paginar(registros: list[dict], pagina: int, por_pagina: int) -> list[dict]:
    """Devuelve el slice correspondiente a la página solicitada."""
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    return registros[inicio:fin]


# ==============================================================================
# Servicio principal
# ==============================================================================

class History_Service:
    """Servicio para el historial de acciones del técnico autenticado"""

    # ------------------------------------------------------------------
    # Vista principal: filtros + ordenamiento + paginación en Python
    # ------------------------------------------------------------------
    def listar_historial(self):

        # ID del técnico autenticado 
        id_tecnico = session.get("user_id")

        # Leer y sanitizar filtros 
        tipo_evento = request.args.get("tipo_evento") or None
        fecha_desde = request.args.get("fecha_desde") or None
        fecha_hasta = request.args.get("fecha_hasta") or None
        pagina = self._parse_pagina(request.args.get("pagina"))

        # Descartar tipo_evento si no pertenece al catálogo
        if tipo_evento and tipo_evento not in _TIPOS_VALIDOS:
            tipo_evento = None

        # Traer todos los registros del técnico desde BD 
        todos_registros = sp_technical_history_listar_todos(id_tecnico)

        # Filtrar en Python 
        registros_filtrados = _filtrar_auditoria_tecnico(
            todos_registros, tipo_evento, fecha_desde, fecha_hasta
        )

        # Ordenar según si hay filtros activos o no 
        hay_filtro = any([tipo_evento, fecha_desde, fecha_hasta])
        if hay_filtro:
            registros_ordenados = _insertion_sort_fecha_desc(registros_filtrados)
        else:
            registros_ordenados = _selection_sort_fecha_desc(registros_filtrados)

        # Paginación en Python 
        total_registros = len(registros_ordenados)
        total_paginas = max(1, math.ceil(total_registros / POR_PAGINA))

        if pagina > total_paginas:
            pagina = total_paginas

        registros_pagina = _paginar(registros_ordenados, pagina, POR_PAGINA)

        # Render 
        return render_template(
            "technical/history.html",
            registros = registros_pagina,
            tipos_evento = TIPOS_EVENTO,
            filtros = {
                "tipo_evento": tipo_evento,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
            },
            pagina_actual = pagina,
            total_paginas = total_paginas,
            total_registros = total_registros,
            por_pagina = POR_PAGINA,
            active_page = "history",
        )

    # ------------------------------------------------------------------
    # Exportar CSV / PDF — scoped al técnico
    # ------------------------------------------------------------------
    def exportar_historial(self):
        """El export delega los filtros al SP"""
        id_tecnico = session.get("user_id")
        formato = request.args.get("formato", "csv").lower()
        tipo_evento = request.args.get("tipo_evento") or None
        fecha_desde = request.args.get("fecha_desde") or None
        fecha_hasta = request.args.get("fecha_hasta") or None

        registros = sp_technical_history_exportar(
            id_tecnico, tipo_evento, fecha_desde, fecha_hasta
        )

        def mapeador(r):
            fecha = r["Fecha_Comentario"]
            return {
                "ID": r["ID_Ticket_Comentario"],
                "Fecha y Hora": fecha.strftime("%d/%m/%Y %I:%M %p") if fecha else "—",
                "Tipo Evento": r["Tipo_Evento"],
                "Ticket": r["FK_ID_Ticket"] or "—",
                "Detalle": r["Comentario"],
                "Visibilidad": "Interno" if r["Es_Interno"] else "Público",
            }

        fila = ExportarReporte.cargar_fila(registros, mapeador)
        fila.insertion_sort("ID", ascendente=True)
        datos = fila.a_lista_datos()

        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if formato == "pdf":
            return ExportarReporte.pdf(
                datos, COLUMNAS, "Mi Historial de Actividad",
                f"historial_tecnico_{fecha_actual}"
            )
        return ExportarReporte.csv(datos, COLUMNAS, f"historial_tecnico_{fecha_actual}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_pagina(valor: str | None) -> int:
        try:
            p = int(valor)
            return p if p >= 1 else 1
        except (TypeError, ValueError):
            return 1


# ==============================================================================
# Helpers internos del módulo
# ==============================================================================

def _parse_fecha(valor: str | None) -> datetime.date | None:
    if not valor:
        return None
    try:
        return datetime.date.fromisoformat(valor)
    except ValueError:
        return None