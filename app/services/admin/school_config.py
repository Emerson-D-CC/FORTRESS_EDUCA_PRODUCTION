from flask import render_template, redirect, url_for, flash, request

from app.forms.admin_forms import FormEditarColegio, FormGuardarJornadas, FormCambiarEstadoColegio
from app.repositories.admin_repository import (
    sp_admin_colegio_detalle,
    sp_admin_colegio_actualizar,
    sp_admin_colegio_estado_cambiar,
    sp_admin_colegio_jornadas_activas,
    sp_admin_colegio_jornada_agregar,
    sp_admin_colegio_jornada_quitar,
    sp_admin_colegio_cupos_obtener,
    sp_admin_colegio_cupo_guardar,
    sp_catalogo_barrios_activos,
    sp_catalogo_jornadas_activas,
)


    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    
def _construir_matriz_cupos(cupos_raw: list[dict]) -> dict:
    """
    Convierte la lista plana de cupos en una estructura anidada:
    {
      niveles_ordenados: ['Preescolar', 'Primaria', ...],
      grados_por_nivel:  { nivel: [{ ID_Grado, Nombre_Grado }, ...] },
      jornadas:          [{ ID_Jornada, Nombre_Jornada }, ...],
      cupos:             { (id_grado, id_jornada): Cupos_Disponibles }
    }
    Esto simplifica el renderizado en la plantilla Jinja2.
    """
    jornadas_vistas = {}
    grados_por_nivel: dict[str, list] = {}
    cupos: dict[tuple, int] = {}
    orden_niveles = ["Preescolar", "Primaria", "Secundaria", "Bachiller"]

    for fila in cupos_raw:
        nivel = fila["Nivel_Educativo"]
        id_grado = fila["ID_Grado"]
        id_jorn = fila["ID_Jornada"]

        # Acumular jornadas (dict preserva orden de inserción en Python 3.7+)
        if id_jorn not in jornadas_vistas:
            jornadas_vistas[id_jorn] = fila["Nombre_Jornada"]

        # Acumular grados por nivel
        if nivel not in grados_por_nivel:
            grados_por_nivel[nivel] = []
        grado_entrada = {"ID_Grado": id_grado, "Nombre_Grado": fila["Nombre_Grado"]}
        if grado_entrada not in grados_por_nivel[nivel]:
            grados_por_nivel[nivel].append(grado_entrada)

        # Mapa de cupos
        cupos[(id_grado, id_jorn)] = fila["Cupos_Disponibles"]

    jornadas = [
        {"ID_Jornada": k, "Nombre_Jornada": v}
        for k, v in jornadas_vistas.items()
    ]
    niveles_ordenados = [n for n in orden_niveles if n in grados_por_nivel]

    return {
        "niveles_ordenados": niveles_ordenados,
        "grados_por_nivel": grados_por_nivel,
        "jornadas": jornadas,
        "cupos": cupos,
    }
    
    

class School_Config_Service:

    def _cargar_catalogo_barrios_choices(self) -> list[tuple]:
        barrios = sp_catalogo_barrios_activos()
        return [(b["ID_Barrio"], b["Nombre_Barrio"]) for b in barrios]

    def _cargar_catalogo_jornadas_choices(self) -> list[tuple]:
        jornadas = sp_catalogo_jornadas_activas()
        return [(j["ID_Jornada"], j["Nombre_Jornada"]) for j in jornadas]

    # Cargar página de configuración
    def cargar_config(self, id_colegio: int):
        """
        Carga school_config.html con todos los datos del colegio:
        datos generales, jornadas activas y matriz de cupos.
        """
        colegio = sp_admin_colegio_detalle(id_colegio)
        if not colegio:
            flash("Colegio no encontrado.", "danger")
            return redirect(url_for("admin.school_status"))

        # --- Formularios ---
        choices_barrios = self._cargar_catalogo_barrios_choices()
        choices_jornadas = self._cargar_catalogo_jornadas_choices()

        form_datos = FormEditarColegio(obj=None)
        form_datos.id_barrio.choices = choices_barrios
        # Precargar valores
        form_datos.nombre.data = colegio["Nombre_Colegio"]
        form_datos.dane.data = colegio["Codigo_DANE"]
        form_datos.email.data = colegio["Email"]
        form_datos.telefono.data = colegio["Telefono"]
        form_datos.direccion.data = colegio["Direccion_Colegio"]
        form_datos.id_barrio.data = colegio["ID_Barrio"]

        form_jornadas = FormGuardarJornadas()
        form_jornadas.jornadas_activas.choices = choices_jornadas

        # Jornadas activas actuales
        jornadas_activas_raw = sp_admin_colegio_jornadas_activas(id_colegio)
        ids_activos = [j["ID_Jornada"] for j in jornadas_activas_raw]
        form_jornadas.jornadas_activas.data = ids_activos

        # Formularios menores
        form_estado = FormCambiarEstadoColegio()

        # --- Matriz de cupos ---
        cupos_raw = sp_admin_colegio_cupos_obtener(id_colegio)
        matriz = _construir_matriz_cupos(cupos_raw)

        return render_template(
            "admin/school_config.html",
            colegio = colegio,
            form_datos = form_datos,
            form_jornadas = form_jornadas,
            form_estado = form_estado,
            jornadas_activas = jornadas_activas_raw,
            matriz_cupos = matriz,
            total_cupos = colegio["Total_Cupos"],
        )

    # ── Guardar datos institucionales ─────────────────────────────────
    def guardar_datos(self, id_colegio: int):
        """Procesa el POST de la Sección 1 (datos del colegio)."""
        form = FormEditarColegio()
        form.id_barrio.choices = self._cargar_catalogo_barrios_choices()

        if form.validate_on_submit():
            sp_admin_colegio_actualizar(
                id_colegio = id_colegio,
                nombre = form.nombre.data.strip(),
                dane = form.dane.data.strip(),
                email = form.email.data.strip() if form.email.data else "",
                telefono = form.telefono.data.strip() if form.telefono.data else "",
                direccion = form.direccion.data.strip(),
                id_barrio = form.id_barrio.data,
            )
            flash("Datos del colegio actualizados correctamente.", "success")
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    flash(f"{error}", "warning")

        return redirect(url_for("admin.school_config", id_colegio=id_colegio))

    # ── Guardar jornadas ─────────────────────────────────────────────
    def guardar_jornadas(self, id_colegio: int):
        """
        Procesa el POST de la Sección 2 (jornadas).
        Compara las jornadas actuales con las enviadas y aplica
        los cambios: agrega las nuevas, quita las removidas.
        """
        form = FormGuardarJornadas()
        form.jornadas_activas.choices = self._cargar_catalogo_jornadas_choices()

        if form.validate_on_submit():
            nuevas_ids = set(form.jornadas_activas.data)
            actuales_raw = sp_admin_colegio_jornadas_activas(id_colegio)
            actuales_ids = {j["ID_Jornada"] for j in actuales_raw}

            agregar = nuevas_ids - actuales_ids
            quitar = actuales_ids - nuevas_ids

            for id_jornada in agregar:
                sp_admin_colegio_jornada_agregar(id_colegio, id_jornada)
            for id_jornada in quitar:
                sp_admin_colegio_jornada_quitar(id_colegio, id_jornada)

            flash("Jornadas actualizadas correctamente.", "success")
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    flash(f"{error}", "warning")

        return redirect(url_for("admin.school_config", id_colegio=id_colegio))

    # ── Guardar cupos ────────────────────────────────────────────────
    def guardar_cupos(self, id_colegio: int):
        """
        Procesa el POST de la Sección 3 (cupos).
        Los campos tienen el formato: cupo_g{id_grado}_j{id_jornada}
        Se parsean manualmente desde request.form y se persiste
        cada celda con sp_admin_colegio_cupo_guardar.
        No usa WTForms porque los campos son completamente dinámicos.
        """
        errores_guardado = []

        for clave, valor in request.form.items():
            # Ignorar campos que no sean cupos
            if not clave.startswith("cupo_g"):
                continue
            try:
                # Parsear "cupo_g3_j1" → id_grado=3, id_jornada=1
                partes = clave.split("_")     # ['cupo', 'g3', 'j1']
                id_grado = int(partes[1][1:])   # 'g3' → 3
                id_jornada = int(partes[2][1:])   # 'j1' → 1
                cupos = max(0, int(valor or 0))

                sp_admin_colegio_cupo_guardar(id_colegio, id_grado, id_jornada, cupos)
            except (ValueError, IndexError, KeyError):
                errores_guardado.append(clave)

        if errores_guardado:
            flash(f"Algunos cupos no pudieron guardarse ({len(errores_guardado)} error/es).", "warning")
        else:
            flash("Cupos guardados correctamente.", "success")

        return redirect(url_for("admin.school_config", id_colegio=id_colegio))

    # Cambiar estado
    def cambiar_estado(self, id_colegio: int):
        """Procesa el POST de la Sección 4 (activar/desactivar)."""
        form = FormCambiarEstadoColegio()

        if form.validate_on_submit():
            nuevo_estado = sp_admin_colegio_estado_cambiar(id_colegio)
            if nuevo_estado == 1:
                flash("El colegio ha sido activado.", "success")
            else:
                flash("El colegio ha sido desactivado.", "warning")
        else:
            flash("Acción no válida.", "danger")

        return redirect(url_for("admin.school_config", id_colegio=id_colegio))