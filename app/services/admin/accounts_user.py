from __future__ import annotations

import datetime
import math

from flask import request, render_template, redirect, url_for, flash, session

from app.repositories.admin_repository import (
    sp_admin_acudientes_listar,
    sp_admin_estudiantes_listar,
    sp_admin_metricas_usuarios,
    sp_admin_toggle_estado_estudiante,
    sp_admin_toggle_estado_usuario,
)
from app.forms.admin_forms import FormToggleEstado
from app.utils.export_doc_utils import ExportarReporte
from app.utils.sp_cache_utils import sp_cache

# ==============================================================================
# Constantes
# ==============================================================================

POR_PAGINA   = 20
COLUMNAS_ACU = ["ID", "Nombre", "Correo", "MFA", "Solicitudes", "Estado"]
COLUMNAS_EST = ["ID", "Nombre", "Acudiente", "Edad", "Género", "Estado"]

# ==============================================================================
# Helpers de filtrado
# ==============================================================================

def _filtrar_por_estado(
    registros: list[dict], estado: int | None, campo: str
) -> list[dict]:
    if estado is None:
        return registros
    return [r for r in registros if r.get(campo) == estado]


def _buscar_por_id(
    registros: list[dict], query: str | None, campos: tuple
) -> list[dict]:
    if not query:
        return registros
    termino = query.strip().lower()
    return [
        r for r in registros
        if any(termino in str(r.get(c, "")).lower() for c in campos)
    ]

# ==============================================================================
# Ordenamiento  —  Timsort O(n log n)
# ==============================================================================

def _ordenar_solicitudes_desc(registros: list[dict]) -> list[dict]:
    """Mayor número de solicitudes primero (vista sin restricciones)."""
    return sorted(
        registros,
        key=lambda r: r.get("Total_Solicitudes") or 0,
        reverse=True,
    )


def _ordenar_id_desc(registros: list[dict], campo: str) -> list[dict]:
    """Mayor ID primero (vista con filtros activos)."""
    return sorted(
        registros,
        key=lambda r: r.get(campo) or 0,
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

class Accounts_User_Service:

    # ------------------------------------------------------------------
    @staticmethod
    def _int_or_none(value) -> int | None:
        try:
            v = int(value)
            return v if v >= 0 else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_busqueda(valor) -> str:
        return (valor or "").strip()[:100]

    @staticmethod
    def _parse_pagina(valor) -> int:
        try:
            return max(1, int(valor))
        except (TypeError, ValueError):
            return 1

    # ------------------------------------------------------------------
    def listar_usuarios(self):
        form_toggle = FormToggleEstado()

        busqueda = self._parse_busqueda(request.args.get("busqueda"))
        estado_acu = self._int_or_none(request.args.get("estado_acu"))
        estado_est = self._int_or_none(request.args.get("estado_est"))
        pagina_acu = self._parse_pagina(request.args.get("pagina_acu"))
        pagina_est = self._parse_pagina(request.args.get("pagina_est"))

        datos_metricas = sp_cache.get_or_set(
            "accounts:metricas", sp_admin_metricas_usuarios
        )

        # ── Acudientes (cacheados) ────────────────────────────────────
        todos_acu = sp_cache.get_or_set("accounts:acudientes", sp_admin_acudientes_listar)
        buscados_acu = _buscar_por_id(todos_acu, busqueda, ("ID_Formateado", "ID_Usuario"))
        filtrados_acu = _filtrar_por_estado(buscados_acu, estado_acu, "Estado_Usuario")

        hay_restriccion_acu = estado_acu is not None or bool(busqueda)
        ordenados_acu = (
            _ordenar_id_desc(filtrados_acu, "ID_Usuario")
            if hay_restriccion_acu
            else _ordenar_solicitudes_desc(filtrados_acu)
        )

        total_acu = len(ordenados_acu)
        total_paginas_acu = max(1, math.ceil(total_acu / POR_PAGINA))
        pagina_acu = min(pagina_acu, total_paginas_acu)
        acudientes_pagina = _paginar(ordenados_acu, pagina_acu, POR_PAGINA)

        # ── Estudiantes (cacheados) ───────────────────────────────────
        todos_est = sp_cache.get_or_set("accounts:estudiantes", sp_admin_estudiantes_listar)
        buscados_est  = _buscar_por_id(todos_est, busqueda, ("ID_Formateado", "ID_Estudiante"))
        filtrados_est = _filtrar_por_estado(buscados_est, estado_est, "Estado_Estudiante")
        ordenados_est = _ordenar_id_desc(filtrados_est, "ID_Estudiante")

        total_est = len(ordenados_est)
        total_paginas_est = max(1, math.ceil(total_est / POR_PAGINA))
        pagina_est = min(pagina_est, total_paginas_est)
        estudiantes_pagina = _paginar(ordenados_est, pagina_est, POR_PAGINA)

        return render_template(
            "admin/accounts_user.html",
            active_page = "users",
            form_toggle = form_toggle,
            metricas = datos_metricas,
            acudientes = acudientes_pagina,
            estudiantes = estudiantes_pagina,
            total_acu = total_acu,
            total_est = total_est,
            pagina_acu = pagina_acu,
            pagina_est = pagina_est,
            total_paginas_acu = total_paginas_acu,
            total_paginas_est = total_paginas_est,
            por_pagina = POR_PAGINA,
            filtros = {
                "busqueda": busqueda,
                "estado_acu": estado_acu,
                "estado_est": estado_est,
            },
            tab_activo = request.args.get("tab", "acudientes"),
        )

    # ------------------------------------------------------------------
    def toggle_estado_usuario(self, id_usuario: int):
        nuevo_estado = self._int_or_none(request.form.get("nuevo_estado"))
        if nuevo_estado not in (0, 1):
            flash("Estado inválido.", "danger")
            return redirect(url_for("admin.accounts_user"))

        ejecutor_id = session.get("user_id")
        if not ejecutor_id:
            flash("No se pudo obtener el usuario autenticado.", "danger")
            return redirect(url_for("admin.accounts_user"))

        sp_admin_toggle_estado_usuario(
            id_usuario, nuevo_estado, ejecutor_id,
            request.remote_addr, request.user_agent.string,
        )

        # Invalidar caché para que la próxima carga refleje el cambio
        sp_cache.invalidate("accounts:acudientes", "accounts:metricas")

        accion = "activado" if nuevo_estado == 1 else "desactivado"
        flash(f"Usuario ACU-{id_usuario} {accion} correctamente.", "success")
        return redirect(url_for("admin.accounts_user", tab="acudientes"))

    # ------------------------------------------------------------------
    def toggle_estado_estudiante(self, id_estudiante: int):
        nuevo_estado = self._int_or_none(request.form.get("nuevo_estado"))
        if nuevo_estado not in (0, 1):
            flash("Estado inválido.", "danger")
            return redirect(url_for("admin.accounts_user"))

        ejecutor_id = session.get("user_id")
        if not ejecutor_id:
            flash("No se pudo obtener el usuario autenticado.", "danger")
            return redirect(url_for("admin.accounts_user"))

        sp_admin_toggle_estado_estudiante(
            id_estudiante, nuevo_estado, ejecutor_id,
            request.remote_addr, request.user_agent.string,
        )

        # Invalidar caché de estudiantes
        sp_cache.invalidate("accounts:estudiantes", "accounts:metricas")

        accion = "activado" if nuevo_estado == 1 else "eliminado"
        flash(f"Estudiante EST-{id_estudiante} {accion} correctamente.", "success")
        return redirect(url_for("admin.accounts_user", tab="estudiantes"))

    # ------------------------------------------------------------------
    def exportar_acudientes(self):
        formato = request.args.get("formato", "csv").lower()
        busqueda = self._parse_busqueda(request.args.get("busqueda"))
        estado_acu = self._int_or_none(request.args.get("estado_acu"))

        todos = sp_admin_acudientes_listar()
        buscados = _buscar_por_id(todos, busqueda, ("ID_Formateado", "ID_Usuario"))
        filtrados = _filtrar_por_estado(buscados, estado_acu, "Estado_Usuario")
        ordenados = _ordenar_solicitudes_desc(filtrados)

        def mapeador(r):
            return {
                "ID": r["ID_Formateado"],
                "Nombre": r["Nombre_Completo"],
                "Correo": r.get("Email") or "—",
                "MFA": "Activo" if r.get("MFA") == "ACTIVE" else "Inactivo",
                "Solicitudes": r.get("Total_Solicitudes", 0),
                "Estado": "Activo" if r["Estado_Usuario"] == 1 else "Eliminado",
            }

        fila = ExportarReporte.cargar_fila(ordenados, mapeador)
        datos = fila.a_lista_datos()
        marca = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS_ACU,
                                       "Acudientes Registrados", f"acudientes_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS_ACU, f"acudientes_{marca}")

    # ------------------------------------------------------------------
    def exportar_estudiantes(self):
        formato = request.args.get("formato", "csv").lower()
        busqueda = self._parse_busqueda(request.args.get("busqueda"))
        estado_est = self._int_or_none(request.args.get("estado_est"))

        todos = sp_admin_estudiantes_listar()
        buscados = _buscar_por_id(todos, busqueda, ("ID_Formateado", "ID_Estudiante"))
        filtrados = _filtrar_por_estado(buscados, estado_est, "Estado_Estudiante")
        ordenados = _ordenar_id_desc(filtrados, "ID_Estudiante")

        def mapeador(r):
            return {
                "ID": r["ID_Formateado"],
                "Nombre": r["Nombre_Estudiante"],
                "Acudiente": r.get("Nombre_Acudiente") or "—",
                "Edad": f"{r.get('Edad', '—')} años",
                "Género": r.get("Genero") or "—",
                "Estado": "Activo" if r["Estado_Estudiante"] == 1 else "Eliminado",
            }

        fila = ExportarReporte.cargar_fila(ordenados, mapeador)
        datos = fila.a_lista_datos()
        marca = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS_EST,
                                       "Estudiantes Registrados", f"estudiantes_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS_EST, f"estudiantes_{marca}")