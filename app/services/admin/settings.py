# FUNCIONES DE FLASK
from flask import flash, redirect, render_template, url_for

from app.forms.admin_forms import FormPrioridadAfectacion,FormPrioridadGrupo,FormPrioridadEstrato
from app.repositories.admin_repository import (
    sp_admin_prioridad_afectaciones_listar,
    sp_admin_prioridad_afectacion_insertar,
    sp_admin_prioridad_afectacion_actualizar,
    sp_admin_prioridad_afectacion_estado_cambiar,
    sp_admin_prioridad_grupos_listar,
    sp_admin_prioridad_grupo_insertar,
    sp_admin_prioridad_grupo_actualizar,
    sp_admin_prioridad_grupo_estado_cambiar,
    sp_admin_prioridad_estratos_listar,
    sp_admin_prioridad_estrato_insertar,
    sp_admin_prioridad_estrato_actualizar,
    sp_admin_prioridad_estrato_estado_cambiar,
)


class Settings_Service:
    """Servicio para la gestión de las tablas de configuración de prioridades"""

    #  Carga principal 

    def cargar_settings(self):
        return render_template(
            "admin/settings.html",
            afectaciones = sp_admin_prioridad_afectaciones_listar(),
            grupos = sp_admin_prioridad_grupos_listar(),
            estratos = sp_admin_prioridad_estratos_listar(),
            form_afectacion = FormPrioridadAfectacion(),
            form_grupo = FormPrioridadGrupo(),
            form_estrato = FormPrioridadEstrato(),
        )

    #  Tipo Afectación 

    def crear_afectacion(self):
        form = FormPrioridadAfectacion()
        if form.validate_on_submit():
            sp_admin_prioridad_afectacion_insertar(
                form.nombre.data,
                form.descripcion.data,
                form.nivel_prioridad.data,
            )
            flash("Tipo de afectación creado correctamente.", "success")
        else:
            flash("Error en los datos del formulario de afectación.", "danger")
        return redirect(url_for("admin.settings"))

    def actualizar_afectacion(self, id_afectacion: int):
        form = FormPrioridadAfectacion()
        if form.validate_on_submit():
            sp_admin_prioridad_afectacion_actualizar(
                id_afectacion,
                form.nombre.data,
                form.descripcion.data,
                form.nivel_prioridad.data,
            )
            flash("Tipo de afectación actualizado correctamente.", "success")
        else:
            flash("Error en los datos del formulario de afectación.", "danger")
        return redirect(url_for("admin.settings"))

    def cambiar_estado_afectacion(self, id_afectacion: int):
        sp_admin_prioridad_afectacion_estado_cambiar(id_afectacion)
        flash("Estado de afectación actualizado.", "info")
        return redirect(url_for("admin.settings"))

    #  Grupo Preferencial 

    def crear_grupo(self):
        form = FormPrioridadGrupo()
        if form.validate_on_submit():
            sp_admin_prioridad_grupo_insertar(
                form.nombre.data,
                form.descripcion.data,
                form.nivel_prioridad.data,
            )
            flash("Grupo preferencial creado correctamente.", "success")
        else:
            flash("Error en los datos del formulario de grupo preferencial.", "danger")
        return redirect(url_for("admin.settings"))

    def actualizar_grupo(self, id_grupo: int):
        form = FormPrioridadGrupo()
        if form.validate_on_submit():
            sp_admin_prioridad_grupo_actualizar(
                id_grupo,
                form.nombre.data,
                form.descripcion.data,
                form.nivel_prioridad.data,
            )
            flash("Grupo preferencial actualizado correctamente.", "success")
        else:
            flash("Error en los datos del formulario de grupo preferencial.", "danger")
        return redirect(url_for("admin.settings"))

    def cambiar_estado_grupo(self, id_grupo: int):
        sp_admin_prioridad_grupo_estado_cambiar(id_grupo)
        flash("Estado de grupo preferencial actualizado.", "info")
        return redirect(url_for("admin.settings"))

    #  Estrato 

    def crear_estrato(self):
        form = FormPrioridadEstrato()
        if form.validate_on_submit():
            sp_admin_prioridad_estrato_insertar(
                form.nombre.data,
                form.descripcion.data,
                form.nivel_prioridad.data,
            )
            flash("Estrato creado correctamente.", "success")
        else:
            flash("Error en los datos del formulario de estrato.", "danger")
        return redirect(url_for("admin.settings"))

    def actualizar_estrato(self, id_estrato: int):
        form = FormPrioridadEstrato()
        if form.validate_on_submit():
            sp_admin_prioridad_estrato_actualizar(
                id_estrato,
                form.nombre.data,
                form.descripcion.data,
                form.nivel_prioridad.data,
            )
            flash("Estrato actualizado correctamente.", "success")
        else:
            flash("Error en los datos del formulario de estrato.", "danger")
        return redirect(url_for("admin.settings"))

    def cambiar_estado_estrato(self, id_estrato: int):
        sp_admin_prioridad_estrato_estado_cambiar(id_estrato)
        flash("Estado de estrato actualizado.", "info")
        return redirect(url_for("admin.settings"))