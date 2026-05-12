import datetime
import math

from flask import request, render_template, redirect, url_for, flash, session

from app.repositories.admin_repository import (
    sp_admin_administradores_exportar,
    sp_admin_administradores_listar,
    sp_admin_metricas_funcionarios,
    sp_admin_tecnicos_exportar,
    sp_admin_tecnicos_listar,
    sp_admin_toggle_estado_tecnico,
)
from app.forms.admin_forms import FormToggleEstado, FormFiltroFuncionarios
from app.utils.export_doc_utils import ExportarReporte

POR_PAGINA = 20

COLUMNAS_TEC = ["ID", "Nombre", "Correo", "Casos Asignados", "Casos Cerrados", "Estado"]
COLUMNAS_ADM = ["ID", "Nombre", "Último Acceso", "Estado"]


# ==============================================================================
# Helpers de filtrado
# ==============================================================================

def _filtrar_por_estado(registros: list[dict], estado: int | None, campo: str = "Estado_Usuario") -> list[dict]:
    """Filtra por campo de estado genérico. None = sin filtro."""
    if estado is None:
        return registros
    return [r for r in registros if r.get(campo) == estado]


def _buscar_por_id(registros: list[dict], query: str | None, campos: tuple = ("ID_Formateado", "ID_Usuario")) -> list[dict]:
    """Búsqueda exacta/parcial solo sobre campos de ID."""
    if not query:
        return registros
    termino = query.strip().lower()
    return [
        r for r in registros
        if any(termino in str(r.get(c, "")).lower() for c in campos)
    ]


# ==============================================================================
# Helpers de ordenamiento
# ==============================================================================

def _insertion_sort_casos_desc(registros: list[dict]) -> list[dict]:
    lista = list(registros)
    for i in range(1, len(lista)):
        actual = lista[i]
        clave  = actual.get("Casos_Asignados") or 0
        j = i - 1
        while j >= 0:
            if (lista[j].get("Casos_Asignados") or 0) < clave:
                lista[j + 1] = lista[j]
                j -= 1
            else:
                break
        lista[j + 1] = actual
    return lista


def _selection_sort_id_desc(registros: list[dict], campo: str = "ID_Usuario") -> list[dict]:
    lista = list(registros)
    n = len(lista)
    for i in range(n):
        idx_max = i
        for j in range(i + 1, n):
            if (lista[j].get(campo) or 0) > (lista[idx_max].get(campo) or 0):
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

class Accounts_Func_Service:

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------
    @staticmethod
    def _int_or_none(value) -> int | None:
        try:
            v = int(value)
            return v if v >= 0 else None   # acepta 0 (Desactivado)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_busqueda(valor) -> str:
        return (valor or "").strip()[:100]

    @staticmethod
    def _parse_pagina(valor) -> int:
        try:
            p = int(valor)
            return p if p >= 1 else 1
        except (TypeError, ValueError):
            return 1

    # ------------------------------------------------------------------
    # Vista principal
    # ------------------------------------------------------------------
    def listar_funcionarios(self):
        form_toggle = FormToggleEstado()

        # Filtros técnicos
        busqueda   = self._parse_busqueda(request.args.get("busqueda"))
        estado_tec = self._int_or_none(request.args.get("estado_tec"))

        # Filtros admins (parámetros separados para no contaminar tabs)
        estado_adm = self._int_or_none(request.args.get("estado_adm"))

        pagina_tec = self._parse_pagina(request.args.get("pagina_tec"))
        pagina_adm = self._parse_pagina(request.args.get("pagina_adm"))

        datos_metricas = sp_admin_metricas_funcionarios()

        # ── Técnicos ──────────────────────────────────────────────────
        todos_tec    = sp_admin_tecnicos_listar(None)
        buscados_tec = _buscar_por_id(todos_tec, busqueda)
        filtrados_tec = _filtrar_por_estado(buscados_tec, estado_tec)

        hay_filtro_tec = estado_tec is not None or bool(busqueda)
        ordenados_tec  = _insertion_sort_casos_desc(filtrados_tec) if hay_filtro_tec \
                         else _selection_sort_id_desc(filtrados_tec)

        total_tec         = len(ordenados_tec)
        total_paginas_tec = max(1, math.ceil(total_tec / POR_PAGINA))
        if pagina_tec > total_paginas_tec:
            pagina_tec = total_paginas_tec
        tecnicos_pagina = _paginar(ordenados_tec, pagina_tec, POR_PAGINA)

        # ── Administradores ────────────────────────────────────────────
        todos_adm    = sp_admin_administradores_listar()
        buscados_adm = _buscar_por_id(todos_adm, busqueda)
        filtrados_adm = _filtrar_por_estado(buscados_adm, estado_adm)
        ordenados_adm = _selection_sort_id_desc(filtrados_adm)

        total_adm         = len(ordenados_adm)
        total_paginas_adm = max(1, math.ceil(total_adm / POR_PAGINA))
        if pagina_adm > total_paginas_adm:
            pagina_adm = total_paginas_adm
        admins_pagina = _paginar(ordenados_adm, pagina_adm, POR_PAGINA)

        return render_template(
            "admin/accounts_func.html",
            active_page       = "staff",
            form_toggle       = form_toggle,
            metricas          = datos_metricas,
            tecnicos          = tecnicos_pagina,
            admins            = admins_pagina,
            total_tec         = total_tec,
            total_adm         = total_adm,
            pagina_tec        = pagina_tec,
            pagina_adm        = pagina_adm,
            total_paginas_tec = total_paginas_tec,
            total_paginas_adm = total_paginas_adm,
            por_pagina        = POR_PAGINA,
            filtros = {
                "busqueda":   busqueda,
                "estado_tec": estado_tec,
                "estado_adm": estado_adm,
            },
            tab_activo = request.args.get("tab", "funcionarios"),
        )

    # ------------------------------------------------------------------
    # Toggle estado técnico (POST)
    # ------------------------------------------------------------------
    def toggle_estado_tecnico(self, id_usuario: int):
        nuevo_estado = self._int_or_none(request.form.get("nuevo_estado"))
        if nuevo_estado not in (0, 1):
            flash("Estado inválido.", "danger")
            return redirect(url_for("admin.accounts_func"))

        ejecutor_id = session.get("user_id")
        if not ejecutor_id:
            flash("No se pudo obtener el usuario autenticado.", "danger")
            return redirect(url_for("admin.accounts_func"))

        sp_admin_toggle_estado_tecnico(
            id_usuario, nuevo_estado, ejecutor_id,
            request.remote_addr, request.user_agent.string,
        )
        accion = "activado" if nuevo_estado == 1 else "desactivado"
        flash(f"Técnico TEC-{id_usuario} {accion} correctamente.", "success")
        return redirect(url_for("admin.accounts_func", tab="funcionarios"))

    # ------------------------------------------------------------------
    # Exportar Técnicos
    # ------------------------------------------------------------------
    def exportar_tecnicos(self):
        formato    = request.args.get("formato", "csv").lower()
        busqueda   = self._parse_busqueda(request.args.get("busqueda"))
        estado_tec = self._int_or_none(request.args.get("estado_tec"))

        todos     = sp_admin_tecnicos_exportar()
        buscados  = _buscar_por_id(todos, busqueda)
        filtrados = _filtrar_por_estado(buscados, estado_tec)
        ordenados = _insertion_sort_casos_desc(filtrados) if estado_tec is not None \
                    else _selection_sort_id_desc(filtrados)

        def mapeador(r):
            return {
                "ID":              r["ID_Formateado"],
                "Nombre":          r["Nombre_Completo"],
                "Correo":          r.get("Email") or "—",
                "Casos Asignados": r.get("Casos_Asignados", 0),
                "Casos Cerrados":  r.get("Casos_Cerrados", 0),
                "Estado":          "Activo" if r["Estado_Usuario"] == 1 else "Desactivado",
            }

        fila  = ExportarReporte.cargar_fila(ordenados, mapeador)
        datos = fila.a_lista_datos()
        marca = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS_TEC, "Funcionarios Técnicos", f"tecnicos_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS_TEC, f"tecnicos_{marca}")

    # ------------------------------------------------------------------
    # Exportar Administradores
    # ------------------------------------------------------------------
    def exportar_admins(self):
        formato    = request.args.get("formato", "csv").lower()
        busqueda   = self._parse_busqueda(request.args.get("busqueda"))
        estado_adm = self._int_or_none(request.args.get("estado_adm"))

        todos     = sp_admin_administradores_exportar()
        buscados  = _buscar_por_id(todos, busqueda)
        filtrados = _filtrar_por_estado(buscados, estado_adm)
        ordenados = _selection_sort_id_desc(filtrados)

        def mapeador(r):
            ultimo = r.get("Ultimo_Login")
            return {
                "ID":            r["ID_Formateado"],
                "Nombre":        r["Nombre_Completo"],
                "Último Acceso": ultimo.strftime("%d/%m/%Y %I:%M %p") if ultimo else "—",
                "Estado":        "Activo" if r["Estado_Usuario"] == 1 else "Desactivado",
            }

        fila  = ExportarReporte.cargar_fila(ordenados, mapeador)
        datos = fila.a_lista_datos()
        marca = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS_ADM, "Administradores del Sistema", f"admins_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS_ADM, f"admins_{marca}")