# app/services/admin/accounts_user.py
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

POR_PAGINA = 20

COLUMNAS_ACU = ["ID", "Nombre", "Correo", "MFA", "Solicitudes", "Estado"]
COLUMNAS_EST = ["ID", "Nombre", "Acudiente", "Edad", "Género", "Estado"]


# ==============================================================================
# Helpers de ordenamiento
# ==============================================================================

def _insertion_sort_solicitudes_desc(registros: list[dict]) -> list[dict]:
    """Insertion Sort DESC por Total_Solicitudes."""
    lista = list(registros)
    for i in range(1, len(lista)):
        actual = lista[i]
        clave  = actual.get("Total_Solicitudes") or 0
        j = i - 1
        while j >= 0:
            if (lista[j].get("Total_Solicitudes") or 0) < clave:
                lista[j + 1] = lista[j]
                j -= 1
            else:
                break
        lista[j + 1] = actual
    return lista


def _selection_sort_id_desc(registros: list[dict], campo: str = "ID_Usuario") -> list[dict]:
    """Selection Sort DESC por ID."""
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

class Accounts_User_Service:
    """Lógica de negocio para accounts_user.html (acudientes y estudiantes)."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _int_or_none(value) -> int | None:
        try:
            return int(value) if value is not None and str(value).strip() != "" else None
        except (ValueError, TypeError):
            return None

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
    def listar_usuarios(self):
        form_toggle = FormToggleEstado()

        pagina_acu = self._parse_pagina(request.args.get("pagina_acu"))
        pagina_est = self._parse_pagina(request.args.get("pagina_est"))

        datos_metricas = sp_admin_metricas_usuarios()

        # ── Acudientes ──
        todos_acu = sp_admin_acudientes_listar()
        ordenados_acu = _selection_sort_id_desc(todos_acu, "ID_Usuario")

        total_acu = len(ordenados_acu)
        total_paginas_acu = max(1, math.ceil(total_acu / POR_PAGINA))
        if pagina_acu > total_paginas_acu:
            pagina_acu = total_paginas_acu
        acudientes_pagina = _paginar(ordenados_acu, pagina_acu, POR_PAGINA)

        # ── Estudiantes ──
        todos_est  = sp_admin_estudiantes_listar()
        ordenados_est = _selection_sort_id_desc(todos_est, "ID_Estudiante")

        total_est = len(ordenados_est)
        total_paginas_est = max(1, math.ceil(total_est / POR_PAGINA))
        if pagina_est > total_paginas_est:
            pagina_est = total_paginas_est
        estudiantes_pagina = _paginar(ordenados_est, pagina_est, POR_PAGINA)

        return render_template(
            "admin/accounts_user.html",
            active_page = "users",
            form_toggle = form_toggle,
            metricas = datos_metricas,
            # datos paginados
            acudientes = acudientes_pagina,
            estudiantes = estudiantes_pagina,
            # totales
            total_acu = total_acu,
            total_est = total_est,
            # paginación
            pagina_acu = pagina_acu,
            pagina_est = pagina_est,
            total_paginas_acu = total_paginas_acu,
            total_paginas_est = total_paginas_est,
            por_pagina = POR_PAGINA,
            tab_activo = request.args.get("tab", "acudientes"),
        )

    # ------------------------------------------------------------------
    # Toggle estado acudiente (POST)
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
        accion = "activado" if nuevo_estado == 1 else "desactivado"
        flash(f"Usuario ACU-{id_usuario} {accion} correctamente.", "success")
        return redirect(url_for("admin.accounts_user", tab="acudientes"))

    # ------------------------------------------------------------------
    # Toggle estado estudiante (POST)
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
        accion = "activado" if nuevo_estado == 1 else "eliminado"
        flash(f"Estudiante EST-{id_estudiante} {accion} correctamente.", "success")
        return redirect(url_for("admin.accounts_user", tab="estudiantes"))

    # ------------------------------------------------------------------
    # Exportar Acudientes
    # ------------------------------------------------------------------
    def exportar_acudientes(self):
        formato = request.args.get("formato", "csv").lower()
        todos = sp_admin_acudientes_listar()
        ordenados = _insertion_sort_solicitudes_desc(todos)

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
            return ExportarReporte.pdf(datos, COLUMNAS_ACU, "Acudientes Registrados", f"acudientes_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS_ACU, f"acudientes_{marca}")

    # ------------------------------------------------------------------
    # Exportar Estudiantes
    # ------------------------------------------------------------------
    def exportar_estudiantes(self):
        formato = request.args.get("formato", "csv").lower()
        todos = sp_admin_estudiantes_listar()
        ordenados = _selection_sort_id_desc(todos, "ID_Estudiante")

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
            return ExportarReporte.pdf(datos, COLUMNAS_EST, "Estudiantes Registrados", f"estudiantes_{marca}")
        return ExportarReporte.csv(datos, COLUMNAS_EST, f"estudiantes_{marca}")