from __future__ import annotations

import datetime
import math

from flask import render_template, request

from app.repositories.admin_repository import (
    sp_history_listar_todos,
    sp_history_exportar_auditoria,
)
from app.utils.export_doc_utils import ExportarReporte
from app.utils.sp_cache_utils import sp_cache

# ==============================================================================
# Constantes
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
COLUMNAS = ["ID", "Fecha y Hora", "Tipo Evento", "Usuario", "Rol",
                "Ticket", "Detalle", "Visibilidad"]
_TIPOS_VALIDOS = {v for v, _ in TIPOS_EVENTO}

# ==============================================================================
# Helpers de filtrado
# ==============================================================================

def _filtrar_auditoria(registros: list[dict], tipo_evento: str | None, fecha_desde: str | None, fecha_hasta: str | None) -> list[dict]:
    resultado = registros

    if tipo_evento:
        resultado = [r for r in resultado if r["Tipo_Evento"] == tipo_evento]

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
# Ordenamiento  —  Timsort O(n log n)  en lugar de O(n²)
# ==============================================================================

_FECHA_MIN = datetime.datetime.min


def _ordenar_fecha_desc(registros: list[dict]) -> list[dict]:
    """Timsort descendente por Fecha_Comentario"""
    return sorted(
        registros,
        key=lambda r: r["Fecha_Comentario"] or _FECHA_MIN,
        reverse=True,
    )

# ==============================================================================
# Paginación
# ==============================================================================

def _paginar(registros: list[dict], pagina: int, por_pagina: int) -> list[dict]:
    inicio = (pagina - 1) * por_pagina
    return registros[inicio: inicio + por_pagina]

# ==============================================================================
# Servicio
# ==============================================================================

class History_Service:

    def listar_auditoria(self):
        tipo_evento = request.args.get("tipo_evento") or None
        fecha_desde = request.args.get("fecha_desde") or None
        fecha_hasta = request.args.get("fecha_hasta") or None
        pagina = self._parse_pagina(request.args.get("pagina"))

        if tipo_evento and tipo_evento not in _TIPOS_VALIDOS:
            tipo_evento = None

        # ── Obtener datos (cacheados 45 s) ───────────────────────────
        todos = sp_cache.get_or_set("history:todos", sp_history_listar_todos)

        # ── Filtrar ───────────────────────────────────────────────────
        filtrados = _filtrar_auditoria(todos, tipo_evento, fecha_desde, fecha_hasta)

        # ── Ordenar con Timsort ───────────────────────────────────────
        ordenados = _ordenar_fecha_desc(filtrados)

        # ── Paginar ───────────────────────────────────────────────────
        total_registros = len(ordenados)
        total_paginas = max(1, math.ceil(total_registros / POR_PAGINA))
        pagina = min(pagina, total_paginas)
        registros_pagina = _paginar(ordenados, pagina, POR_PAGINA)

        return render_template(
            "admin/history.html",
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
    def exportar_auditoria(self):
        formato = request.args.get("formato", "csv").lower()
        tipo_evento = request.args.get("tipo_evento") or None
        fecha_desde = request.args.get("fecha_desde") or None
        fecha_hasta = request.args.get("fecha_hasta") or None

        registros = sp_history_exportar_auditoria(tipo_evento, fecha_desde, fecha_hasta)

        def mapeador(r):
            fecha = r["Fecha_Comentario"]
            return {
                "ID": r["ID_Ticket_Comentario"],
                "Fecha y Hora": fecha.strftime("%d/%m/%Y %I:%M %p") if fecha else "—",
                "Tipo Evento": r["Tipo_Evento"],
                "Usuario": r["Nombre_Completo_Usuario"],
                "Rol": r["Nombre_Rol"],
                "Ticket": r["FK_ID_Ticket"] or "—",
                "Detalle": r["Comentario"],
                "Visibilidad": "Interno" if r["Es_Interno"] else "Público",
            }

        fila = ExportarReporte.cargar_fila(registros, mapeador)
        fila.insertion_sort("ID", ascendente=True)
        datos = fila.a_lista_datos()
        marca = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS, "Registro de Auditoría",
                                       f"auditoria_history_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS, f"auditoria_history_{marca}")

    # ------------------------------------------------------------------
    @staticmethod
    def _parse_pagina(valor) -> int:
        try:
            p = int(valor)
            return max(1, p)
        except (TypeError, ValueError):
            return 1


# ==============================================================================
# Helpers de módulo
# ==============================================================================

def _parse_fecha(valor: str | None) -> datetime.date | None:
    if not valor:
        return None
    try:
        return datetime.date.fromisoformat(valor)
    except ValueError:
        return None