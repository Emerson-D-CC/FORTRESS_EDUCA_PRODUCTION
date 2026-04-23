from flask import render_template, redirect, url_for, flash, request

from app.forms.admin_forms import FormFiltroColegios, FormAgregarColegio
from app.repositories.admin_repository import (
    sp_admin_colegios_estadisticas,
    sp_admin_colegios_listar,
    sp_admin_colegio_insertar,
    sp_admin_colegio_jornada_agregar,
    sp_catalogo_barrios_activos,
    sp_catalogo_jornadas_activas,
)


    # ------------------------------------------------------------------
    # Helpers de ordenamiento
    # ------------------------------------------------------------------

def _insertion_sort_por_nombre(colegios: list[dict]) -> list[dict]:
    """Insertion Sort ascendente sobre la clave 'Nombre_Colegio'"""
    
    lista = list(colegios)
    for i in range(1, len(lista)):
        actual = lista[i]
        clave  = actual["Nombre_Colegio"].lower()
        j = i - 1
        while j >= 0 and lista[j]["Nombre_Colegio"].lower() > clave:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = actual
    return lista


def _selection_sort_por_cupos_desc(colegios: list[dict]) -> list[dict]:
    """
        Selection Sort descendente sobre la clave 'Total_Cupos'. 
        Se usa cuando el usuario no aplica ningún filtro, mostrando primero los colegios con más cupos configurados.
    """
    lista = list(colegios)
    n = len(lista)
    for i in range(n):
        idx_max = i
        for j in range(i + 1, n):
            if lista[j]["Total_Cupos"] > lista[idx_max]["Total_Cupos"]:
                idx_max = j
        lista[i], lista[idx_max] = lista[idx_max], lista[i]
    return lista


def _filtrar_colegios(colegios: list[dict], nombre: str, estado: str, id_barrio: int, id_jornada: int, jornadas_catalogo: list[dict]) -> list[dict]:
    """
    Aplica los filtros de la barra de búsqueda sobre la lista completa.
    Toda la lógica vive aquí, sin cláusulas WHERE en SQL.

    Parámetros
    ----------
    colegios : lista completa devuelta por sp_admin_colegios_listar
    nombre : texto libre (busca en Nombre_Colegio y Codigo_DANE)
    estado : "1", "0" o "" (todos)
    id_barrio : ID del barrio o 0 (todos)
    id_jornada : ID de la jornada o 0 (todos)
    jornadas_catalogo : lista [{ID_Jornada, Nombre_Jornada}] para resolver nombre
    """
    resultado = colegios

    # Filtro por nombre / DANE (búsqueda parcial, insensible a mayúsculas)
    if nombre:
        termino = nombre.strip().lower()
        resultado = [
            c for c in resultado
            if termino in c["Nombre_Colegio"].lower()
            or termino in c["Codigo_DANE"].lower()
        ]

    # Filtro por estado
    if estado in ("0", "1"):
        resultado = [
            c for c in resultado
            if str(c["Estado_Colegio"]) == estado
        ]

    # Filtro por barrio
    if id_barrio:
        resultado = [
            c for c in resultado
            if c["ID_Barrio"] == id_barrio
        ]

    # Filtro por jornada (busca el nombre dentro de Jornadas_Activas)
    if id_jornada:
        nombre_jornada = next(
            (j["Nombre_Jornada"] for j in jornadas_catalogo if j["ID_Jornada"] == id_jornada),
            None,
        )
        if nombre_jornada:
            resultado = [
                c for c in resultado
                if nombre_jornada in (c.get("Jornadas_Activas") or "")
            ]

    return resultado


class School_Status_Service:

    # Cargar listado con filtros
    def listar_colegios(self):
        """
        Carga la página school_status.html con filtros y estadísticas.
        Flujo:
          1. Cargar catálogos para poblar los SelectField del formulario.
          2. Obtener TODOS los colegios desde la BD (sin filtros SQL).
          3. Aplicar filtros y ordenamiento en Python.
          4. Renderizar template con los datos ya filtrados.
        """
        # --- Catálogos ---
        barrios = sp_catalogo_barrios_activos()
        jornadas = sp_catalogo_jornadas_activas()
        choices_barrios = [(0, "Todos los barrios")] + [(b["ID_Barrio"], b["Nombre_Barrio"]) for b in barrios]
        choices_jornadas = [(0, "Todas")] + [(j["ID_Jornada"], j["Nombre_Jornada"]) for j in jornadas]

        # --- Formularios ---
        form_filtro = FormFiltroColegios(request.args)
        form_agregar = FormAgregarColegio()

        form_filtro.id_barrio.choices = choices_barrios
        form_filtro.id_jornada.choices = choices_jornadas
        form_agregar.id_barrio.choices = [(0, "Seleccione un barrio…")] + [(b["ID_Barrio"], b["Nombre_Barrio"]) for b in barrios]
        form_agregar.jornadas.choices = [(j["ID_Jornada"], j["Nombre_Jornada"]) for j in jornadas]

        # --- Estadísticas (tarjetas) ---
        stats = sp_admin_colegios_estadisticas()

        # --- Todos los colegios desde BD ---
        todos_colegios = sp_admin_colegios_listar()

        # --- Leer parámetros del filtro ---
        nombre = (form_filtro.nombre.data or "").strip()
        estado = form_filtro.estado.data or ""
        id_barrio = form_filtro.id_barrio.data  or 0
        id_jornada = form_filtro.id_jornada.data or 0

        # --- Filtrar en Python ---
        colegios_filtrados = _filtrar_colegios(
            todos_colegios, nombre, estado, id_barrio, id_jornada, jornadas
        )

        # --- Ordenar:
        #     · Con filtro activo = insertion sort por nombre (A-Z)
        #     · Sin filtro        = selection sort por cupos (mayor primero)
        hay_filtro = any([nombre, estado, id_barrio, id_jornada])
        if hay_filtro:
            colegios_ordenados = _insertion_sort_por_nombre(colegios_filtrados)
        else:
            colegios_ordenados = _selection_sort_por_cupos_desc(colegios_filtrados)

        return render_template(
            "admin/school_status.html",
            colegios=colegios_ordenados,
            total_colegios=len(colegios_ordenados),
            stats=stats,
            form_filtro=form_filtro,
            form_agregar=form_agregar,
        )

    # Agregar nuevo colegio
    def agregar_colegio(self):
        """Procesa el POST del modal de agregar colegio."""
        barrios = sp_catalogo_barrios_activos()
        jornadas = sp_catalogo_jornadas_activas()

        form = FormAgregarColegio()
        form.id_barrio.choices = [(0, "Seleccione un barrio…")] + [(b["ID_Barrio"], b["Nombre_Barrio"]) for b in barrios]
        form.jornadas.choices = [(j["ID_Jornada"], j["Nombre_Jornada"]) for j in jornadas]

        if form.validate_on_submit():
            nuevo_id = sp_admin_colegio_insertar(
                nombre = form.nombre.data.strip(),
                dane = form.dane.data.strip(),
                email = form.email.data.strip() if form.email.data    else "",
                telefono = form.telefono.data.strip() if form.telefono.data else "",
                direccion = form.direccion.data.strip(),
                id_barrio = form.id_barrio.data,
            )
            if nuevo_id:
                # Activar jornadas seleccionadas
                for id_jornada in form.jornadas.data:
                    sp_admin_colegio_jornada_agregar(nuevo_id, id_jornada)
                flash("Colegio registrado exitosamente.", "success")
            else:
                flash("No se pudo registrar el colegio. Verifique que el nombre y el DANE no estén duplicados.", "danger")
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    flash(f"{error}", "warning")

        return redirect(url_for("admin.school_status"))
