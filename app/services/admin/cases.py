from __future__ import annotations

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
from app.utils.sp_cache_utils import sp_cache

# ==============================================================================
# Constantes
# ==============================================================================

POR_PAGINA = 20

COLUMNAS_EXPORT = [
    "ID Ticket", "Estudiante", "Acudiente", "Edad",
    "Grado", "Afectación", "Estado", "Prioridad",
    "Colegio Asignado", "Técnico",
]

_CAMPOS_BUSQUEDA = (
    "ID_Ticket", "Nombre_Estudiante", "Nombre_Acudiente",
    "Nombre_Estado", "Nombre_Grado", "Nombre_Afectacion",
    "Colegio_Asignado", "Nombre_Tecnico",
)

# ==============================================================================
# Índice de búsqueda — se construye una vez por bloque cacheado
# ==============================================================================

def _construir_indice(registros: list[dict]) -> list[tuple[dict, str]]:
    """Pre-computa cadena de búsqueda por registro"""
    return [
        (r, " ".join(
            str(r.get(c, "")).lower() for c in _CAMPOS_BUSQUEDA
        ))
        for r in registros
    ]


def _buscar_tickets(indexado: list[tuple[dict, str]], query: str | None) -> list[dict]:
    """Filtra sobre el índice pre-computado"""
    if not query:
        return [r for r, _ in indexado]
    terminos = [t for t in query.strip().lower().split() if t]
    if not terminos:
        return [r for r, _ in indexado]
    return [
        r for r, cadena in indexado
        if all(t in cadena for t in terminos)
    ]

# ==============================================================================
# Filtrado por selectores
# ==============================================================================

def _filtrar_tickets(registros: list[dict], id_estado: int | None, id_grado: int | None, id_afectacion: int | None) -> list[dict]:
    if id_estado:
        registros = [r for r in registros if r["FK_ID_Estado_Ticket"] == id_estado]
    if id_grado:
        registros = [r for r in registros if r["FK_ID_Grado"] == id_grado]
    if id_afectacion:
        registros = [r for r in registros if r["FK_ID_Tipo_Afectacion"] == id_afectacion]
    return registros

# ==============================================================================
# Ordenamiento  —  Timsort O(n log n)
# ==============================================================================

_FECHA_MIN = datetime.datetime.min


def _ordenar_fecha_desc(registros: list[dict]) -> list[dict]:
    return sorted(
        registros,
        key=lambda r: r["Fecha_Creacion"] or _FECHA_MIN,
        reverse=True,
    )


def _ordenar_prioridad_desc(registros: list[dict]) -> list[dict]:
    return sorted(
        registros,
        key=lambda r: r["Puntaje_Prioridad"] or 0,
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

class Cases_Service:

    def listar_todos_tickets(self):
        id_estado = self._parse_int(request.args.get("estado"))
        id_grado = self._parse_int(request.args.get("grado"))
        id_afectacion = self._parse_int(request.args.get("afectacion"))
        busqueda = (request.args.get("busqueda") or "").strip()[:100]
        pagina = self._parse_pagina(request.args.get("pagina"))

        # ── Catálogos ─────────────────────────────────────────────────
        estados = sp_cache.get_or_set("cases:cat:estados", sp_catalogo_estados_ticket)
        grados = sp_cache.get_or_set("cases:cat:grados", sp_catalogo_grados)
        afectaciones = sp_cache.get_or_set("cases:cat:afectaciones", sp_catalogo_tipo_afectacion)

        form_filtro = FormFiltroTickets(request.args, meta={"csrf": False})
        form_filtro.estado.choices = (
            [(0, "Todos los estados")] +
            [(e["ID_Estado_Ticket"], e["Nombre_Estado"]) for e in estados]
        )
        form_filtro.grado.choices = (
            [(0, "Todos los grados")] +
            [(g["ID_Grado"], g["Nombre_Grado"]) for g in grados]
        )
        form_filtro.afectacion.choices = (
            [(0, "Todas las afectaciones")] +
            [(a["ID_Tipo_Afectacion"], a["Nombre_Afectacion"]) for a in afectaciones]
        )

        # ── Datos + índice de búsqueda  ───────────────
        todos   = sp_cache.get_or_set("cases:todos", sp_cases_listar_todos)
        indexado = sp_cache.get_or_set(
            "cases:indice",
            lambda: _construir_indice(todos),
        )

        hay_restriccion = any([id_estado, id_grado, id_afectacion, busqueda])

        buscados = _buscar_tickets(indexado, busqueda)
        filtrados = _filtrar_tickets(buscados, id_estado, id_grado, id_afectacion)

        ordenados = (
            _ordenar_fecha_desc(filtrados)
            if hay_restriccion
            else _ordenar_prioridad_desc(filtrados)
        )

        total_tickets = len(ordenados)
        total_paginas = max(1, math.ceil(total_tickets / POR_PAGINA))
        pagina = min(pagina, total_paginas)

        tickets_pagina = _paginar(ordenados, pagina, POR_PAGINA)
        metricas = sp_cache.get_or_set("cases:metricas", sp_cases_metricas) or {}

        return render_template(
            "admin/cases.html",
            tickets = tickets_pagina,
            total_tickets = total_tickets,
            metricas = metricas,
            form_filtro = form_filtro,
            filtros = {
                "estado": id_estado, "grado": id_grado,
                "afectacion": id_afectacion, "busqueda": busqueda,
            },
            pagina_actual = pagina,
            total_paginas = total_paginas,
            por_pagina = POR_PAGINA,
            active_page = "cases",
        )

    # ------------------------------------------------------------------
    def exportar_tickets(self):
        formato = request.args.get("formato", "csv").lower()
        id_estado = self._parse_int(request.args.get("estado"))
        id_grado = self._parse_int(request.args.get("grado"))
        id_afectacion = self._parse_int(request.args.get("afectacion"))
        busqueda = (request.args.get("busqueda") or "").strip()[:100]

        todos = sp_cases_exportar_todos()
        indexado = _construir_indice(todos)
        buscados = _buscar_tickets(indexado, busqueda)
        filtrados = _filtrar_tickets(buscados, id_estado, id_grado, id_afectacion)

        hay_restriccion = any([id_estado, id_grado, id_afectacion, busqueda])
        ordenados = (
            _ordenar_fecha_desc(filtrados)
            if hay_restriccion
            else _ordenar_prioridad_desc(filtrados)
        )

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
                "Técnico":         r.get("Nombre_Tecnico") or "Sin asignar",
            }

        fila  = ExportarReporte.cargar_fila(ordenados, mapeador)
        datos = fila.a_lista_datos()
        marca = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS_EXPORT,
                                       "Solicitudes de Cupo", f"solicitudes_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS_EXPORT, f"solicitudes_{marca}")

    # ------------------------------------------------------------------
    @staticmethod
    def _parse_int(valor) -> int | None:
        try:
            v = int(valor)
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_pagina(valor) -> int:
        try:
            p = int(valor)
            return max(1, p)
        except (TypeError, ValueError):
            return 1