import math
import datetime

from flask import render_template, request

from app.repositories.admin_repository import (
    sp_history_listar_todos,
    sp_history_exportar_auditoria,
)
from app.utils.export_doc_utils import ExportarReporte


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
COLUMNAS = ["ID", "Fecha y Hora", "Tipo Evento", "Usuario", "Rol", "Ticket", "Detalle", "Visibilidad"]

# Valores de tipo_evento válidos para sanitizar la entrada del filtro
_TIPOS_VALIDOS = {v for v, _ in TIPOS_EVENTO}


# ==============================================================================
# Helpers de filtrado
# ==============================================================================

def _filtrar_auditoria(registros: list[dict], tipo_evento: str | None, fecha_desde: str | None, fecha_hasta: str | None) -> list[dict]:
    """Aplica los tres filtros sobre la lista de registros"""
    resultado = registros

    # Filtro por tipo de evento
    if tipo_evento:
        resultado = [
            r for r in resultado
            if r["Tipo_Evento"] == tipo_evento
        ]

    # Convertir strings a date solo si existen, para no repetirlo por fila
    dt_desde = _parse_fecha(fecha_desde)
    dt_hasta = _parse_fecha(fecha_hasta)

    # Filtro por fecha desde
    if dt_desde:
        resultado = [
            r for r in resultado
            if r["Fecha_Comentario"] and r["Fecha_Comentario"].date() >= dt_desde
        ]

    # Filtro por fecha hasta
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
        # None va al fondo = se trata como datetime mínimo
        clave  = actual["Fecha_Comentario"] or datetime.datetime.min
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
    """Selection Sort descendente por Fecha_Comentario. Se usa cuando NO hay filtros"""
    lista = list(registros)
    n = len(lista)
    for i in range(n):
        idx_max = i
        for j in range(i + 1, n):
            fecha_j = lista[j]["Fecha_Comentario"]   or datetime.datetime.min
            fecha_max = lista[idx_max]["Fecha_Comentario"] or datetime.datetime.min
            if fecha_j > fecha_max:
                idx_max = j
        lista[i], lista[idx_max] = lista[idx_max], lista[i]
    return lista


# ==============================================================================
# Paginación en Python
# ==============================================================================

def _paginar(registros: list[dict], pagina: int, por_pagina: int) -> list[dict]:
    """Devuelve el slice correspondiente a la página solicitada"""
    inicio = (pagina - 1) * por_pagina
    fin    = inicio + por_pagina
    return registros[inicio:fin]


# ==============================================================================
# Servicio principal
# ==============================================================================

class History_Service:
    """Servicio para el módulo de historial y auditoría."""

    def listar_auditoria(self):

        #  Leer y sanitizar filtros 
        tipo_evento = request.args.get("tipo_evento") or None
        fecha_desde = request.args.get("fecha_desde") or None
        fecha_hasta = request.args.get("fecha_hasta") or None
        pagina = self._parse_pagina(request.args.get("pagina"))

        # Descartar tipo_evento si no es un valor del catálogo
        if tipo_evento and tipo_evento not in _TIPOS_VALIDOS:
            tipo_evento = None

        # Traer todos los registros desde BD 
        todos_registros = sp_history_listar_todos()

        # Filtrar en Python 
        registros_filtrados = _filtrar_auditoria(
            todos_registros, tipo_evento, fecha_desde, fecha_hasta
        )

        #  4. Ordenar según si hay filtros activos o no 
        hay_filtro = any([tipo_evento, fecha_desde, fecha_hasta])
        if hay_filtro:
            # Con filtros = Insertion Sort DESC (subconjunto, orden de recencia)
            registros_ordenados = _insertion_sort_fecha_desc(registros_filtrados)
        else:
            # Sin filtros = Selection Sort DESC (listado completo, más recientes primero)
            registros_ordenados = _selection_sort_fecha_desc(registros_filtrados)

        # Paginación en Python 
        total_registros = len(registros_ordenados)
        total_paginas   = max(1, math.ceil(total_registros / POR_PAGINA))

        # Corregir página fuera de rango
        if pagina > total_paginas:
            pagina = total_paginas

        # Slice de la página actual 
        registros_pagina = _paginar(registros_ordenados, pagina, POR_PAGINA)

        # Render (mismas variables de contexto que antes) 
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
    # Exportar CSV / PDF
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

        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS, "Registro de Auditoría", f"auditoria_history_{fecha_actual}")
        return ExportarReporte.csv(datos, COLUMNAS, f"auditoria_history_{fecha_actual}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_pagina(valor: str | None) -> int:
        """Convierte string a int; retorna 1 si inválido o menor que 1"""
        try:
            p = int(valor)
            return p if p >= 1 else 1
        except (TypeError, ValueError):
            return 1

# ==============================================================================
# Helpers internos del módulo
# ==============================================================================

def _parse_fecha(valor: str | None) -> datetime.date | None:
    """Convierte un string 'YYYY-MM-DD' a datetime.date"""
    if not valor:
        return None
    try:
        return datetime.date.fromisoformat(valor)
    except ValueError:
        return None