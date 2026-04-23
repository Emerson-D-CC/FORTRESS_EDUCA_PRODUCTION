import io
from flask import render_template, redirect, url_for, flash, session, send_file

#  Repositories 
from app.repositories.admin_repository import (
    # Detalle
    sp_ticket_panel_consultar_detalle,
    # Comentarios
    sp_ticket_panel_comentarios_consultar,
    sp_ticket_panel_comentario_insertar,
    # Estado
    sp_ticket_panel_estado_actualizar,
    # Cupo
    sp_ticket_panel_asignar_cupo,
    # Documentos
    sp_ticket_panel_documentos_consultar,
    sp_ticket_panel_documento_descargar,
    sp_ticket_panel_documento_insertar,
    # Datos de acudiente / estudiante
    sp_ticket_panel_acudiente_consultar,
    sp_ticket_panel_estudiante_consultar,
    # Catálogos
    sp_catalogo_estados_ticket,
    sp_catalogo_colegios,
    sp_catalogo_jornadas,
    sp_catalogo_tipo_afectacion,
    sp_catalogo_cupos_disponibles,
    sp_tipo_documento_consultar,
    sp_catalogo_barrios,
)

from app.forms.admin_forms import FormCambiarEstado, FormAgregarComentario, FormAsignarCupo, FormSubirDocumentoTecnico
from app.utils.database_utils import db

# Constantes 
_ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
_MAX_FILE_BYTES = 5 * 1024 * 1024   # 5 MB


class Ticket_Panel_Service:
    """Servicio principal para el panel técnico de tickets."""

    def __init__(self):
        self._allowed_extensions = _ALLOWED_EXTENSIONS
        self._max_file_bytes = _MAX_FILE_BYTES

    def _cargar_formularios(self, id_ticket: str) -> dict:
        """Instancia y rellena los formularios del panel del ticket."""
        form_estado = FormCambiarEstado()
        estados = sp_catalogo_estados_ticket()
        form_estado.estado.choices = [(0, "-- Seleccione --")] + [
            (e["ID_Estado_Ticket"], e["Nombre_Estado"]) for e in estados
        ]

        form_comentario = FormAgregarComentario()

        form_asignacion = FormAsignarCupo()
        colegios = sp_catalogo_colegios()
        jornadas = sp_catalogo_jornadas()
        afectaciones = sp_catalogo_tipo_afectacion()
        barrios = sp_catalogo_barrios()
        cupos = sp_catalogo_cupos_disponibles(id_ticket)

        form_asignacion.colegio_asignado.choices = [(0, "-- Seleccione --")] + [
            (c["ID_Colegio"], c["Nombre_Colegio"]) for c in colegios
        ]
        form_asignacion.jornada_asignada.choices = [(0, "-- Seleccione --")] + [
            (j["ID_Jornada"], j["Nombre_Jornada"]) for j in jornadas
        ]
        form_asignacion.tipo_afectacion.choices = [(0, "-- Seleccione --")] + [
            (a["ID_Tipo_Afectacion"], a["Nombre_Afectacion"]) for a in afectaciones
        ]
        form_asignacion.barrio.choices = [(0, "-- Seleccione --")] + [
            (b["ID_Barrio"], b["Nombre_Barrio"]) for b in barrios
        ]
        form_asignacion.cupo.choices = [(0, "-- Seleccione --")] + [
            (cu["ID_Cupos"], cu["Label_Cupo"]) for cu in cupos
        ]

        form_doc = FormSubirDocumentoTecnico()
        tipos_doc = sp_tipo_documento_consultar()
        form_doc.tipo_documento.choices = [(0, "-- Seleccione --")] + [
            (t["ID_Tipo_Doc"], t["Nombre_Tipo_Doc"]) for t in tipos_doc
        ]

        return {
            "form_estado": form_estado,
            "form_comentario": form_comentario,
            "form_asignacion": form_asignacion,
            "form_doc": form_doc,
        }

    def _cargar_contexto_ticket(self, id_ticket: str) -> dict | None:
        """Carga los datos completos del ticket para el panel."""
        ticket = sp_ticket_panel_consultar_detalle(id_ticket)
        if not ticket:
            return None

        comentarios = sp_ticket_panel_comentarios_consultar(id_ticket)
        documentos = sp_ticket_panel_documentos_consultar(id_ticket)
        acudiente = sp_ticket_panel_acudiente_consultar(id_ticket)
        estudiante = sp_ticket_panel_estudiante_consultar(id_ticket)

        return {
            "ticket": ticket,
            "comentarios": comentarios,
            "documentos": documentos,
            "acudiente": acudiente,
            "estudiante": estudiante,
        }   

    def _contexto_tecnico(self) -> dict:
        """Construye datos de contexto del técnico para el navbar."""
        nombre = session.get("nombre_usuario", "Técnico")
        partes = nombre.strip().split()
        iniciales = "".join(p[0].upper() for p in partes[:2]) if partes else "T"
        return {"nombre_usuario": nombre, "iniciales": iniciales}

    def cargar_ticket_panel(self, id_ticket: str):
        """Retorna la vista del detalle del ticket."""
        ctx = self._cargar_contexto_ticket(id_ticket)
        if not ctx:
            flash("El ticket no existe o no está disponible.", "danger")
            return redirect(url_for("admin.ticket_panel"))

        forms = self._cargar_formularios(id_ticket)
        forms["form_estado"].estado.data = ctx["ticket"]["ID_Estado_Ticket"]

        return render_template(
            "admin/ticket_panel.html",
            **ctx,
            **forms,
            tecnico=self._contexto_tecnico(),
        )

    def agregar_comentario(self, id_ticket: str):
        """Agrega un comentario interno o público al ticket."""
        form = FormAgregarComentario()
        if not form.validate_on_submit():
            errores = "; ".join(
                f"{f}: {', '.join(msgs)}" for f, msgs in form.errors.items()
            )
            print(f"[FORM ERROR - comentario] {errores}")
            flash("Por favor revise el comentario antes de enviarlo.", "danger")
            return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

        try:
            sp_ticket_panel_comentario_insertar(
                id_ticket=id_ticket,
                id_usuario=session["user_id"],
                comentario=form.comentario.data.strip(),
                es_interno=form.es_interno.data,
            )
            db.commit()
            flash("Comentario agregado correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - comentario] {e}")
            flash("Ocurrió un error al guardar el comentario.", "danger")

        return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

    def actualizar_estado(self, id_ticket: str):
        """Actualiza el estado del ticket."""
        form_estado = FormCambiarEstado()
        estados = sp_catalogo_estados_ticket()
        form_estado.estado.choices = [(0, "-- Seleccione --")] + [
            (e["ID_Estado_Ticket"], e["Nombre_Estado"]) for e in estados
        ]

        if not form_estado.validate_on_submit():
            errores = "; ".join(
                f"{f}: {', '.join(msgs)}" for f, msgs in form_estado.errors.items()
            )
            print(f"[FORM ERROR - estado] {errores}")
            flash("Por favor revise los campos antes de guardar.", "danger")
            return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

        fecha_cierre = form_estado.fecha_cierre.data if form_estado.fecha_cierre.data else None

        try:
            sp_ticket_panel_estado_actualizar(
                id_ticket=id_ticket,
                id_estado_nuevo=form_estado.estado.data,
                fecha_cierre=fecha_cierre,
                resolucion=form_estado.resolucion.data.strip(),
                id_tecnico=session["user_id"],
            )
            db.commit()
            flash("Estado del ticket actualizado correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - estado] {e}")
            flash("No se pudo actualizar el estado. Intente nuevamente.", "danger")

        return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

    def asignar_cupo(self, id_ticket: str):
        """Asigna el cupo seleccionado al ticket."""
        form_asignacion = FormAsignarCupo()
        form_asignacion.colegio_asignado.choices = [(0, "-- Seleccione --")] + [
            (c["ID_Colegio"], c["Nombre_Colegio"]) for c in sp_catalogo_colegios()
        ]
        form_asignacion.jornada_asignada.choices = [(0, "-- Seleccione --")] + [
            (j["ID_Jornada"], j["Nombre_Jornada"]) for j in sp_catalogo_jornadas()
        ]
        form_asignacion.tipo_afectacion.choices = [(0, "-- Seleccione --")] + [
            (a["ID_Tipo_Afectacion"], a["Nombre_Afectacion"]) for a in sp_catalogo_tipo_afectacion()
        ]
        form_asignacion.barrio.choices = [(0, "-- Seleccione --")] + [
            (b["ID_Barrio"], b["Nombre_Barrio"]) for b in sp_catalogo_barrios()
        ]
        form_asignacion.cupo.choices = [(0, "-- Seleccione --")] + [
            (cu["ID_Cupos"], cu["Label_Cupo"]) for cu in sp_catalogo_cupos_disponibles(id_ticket)
        ]

        if not form_asignacion.validate_on_submit():
            errores = "; ".join(
                f"{f}: {', '.join(msgs)}" for f, msgs in form_asignacion.errors.items()
            )
            print(f"[FORM ERROR - cupo] {errores}")
            flash("Por favor revise los campos de asignación.", "danger")
            return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

        try:
            sp_ticket_panel_asignar_cupo(
                id_ticket=id_ticket,
                id_cupo=form_asignacion.cupo.data,
                id_tecnico=session["user_id"],
            )
            db.commit()
            flash("Cupo asignado correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - cupo] {e}")
            flash("No se pudo asignar el cupo. Intente nuevamente.", "danger")

        return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

    def subir_documento(self, id_ticket: str):
        """Sube un documento adicional al ticket."""
        form_doc = FormSubirDocumentoTecnico()
        tipos_doc = sp_tipo_documento_consultar()
        form_doc.tipo_documento.choices = [(0, "-- Seleccione --")] + [
            (t["ID_Tipo_Doc"], t["Nombre_Tipo_Doc"]) for t in tipos_doc
        ]

        if not form_doc.validate_on_submit():
            errores = "; ".join(
                f"{f}: {', '.join(msgs)}" for f, msgs in form_doc.errors.items()
            )
            print(f"[FORM ERROR - documento] {errores}")
            flash("Por favor revise el formulario de documentos.", "danger")
            return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

        archivo_field = form_doc.archivo.data
        nombre_original = archivo_field.filename
        extension = nombre_original.rsplit(".", 1)[-1].lower()

        if extension not in self._allowed_extensions:
            flash("Tipo de archivo no permitido. Solo PDF, JPG o PNG.", "danger")
            return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

        contenido = archivo_field.read()
        if len(contenido) > self._max_file_bytes:
            flash("El archivo supera el límite de 5 MB.", "danger")
            return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

        try:
            sp_ticket_panel_documento_insertar(
                id_ticket=id_ticket,
                id_tipo_doc=form_doc.tipo_documento.data,
                archivo=contenido,
                nombre_original=nombre_original,
            )
            sp_ticket_panel_comentario_insertar(
                id_ticket=id_ticket,
                id_usuario=session["user_id"],
                comentario=f"[Documento Subido] {nombre_original}",
                es_interno=True,
            )
            db.commit()
            flash("Documento subido correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - documento upload] {e}")
            flash("Ocurrió un error al subir el documento.", "danger")

        return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

    def descargar_documento(self, id_ticket: str, id_doc: int):
        """Descarga el documento asociado al ticket."""
        doc = sp_ticket_panel_documento_descargar(id_doc)
        if not doc:
            flash("Documento no encontrado.", "danger")
            return redirect(url_for("admin.ticket_panel_detail", id_ticket=id_ticket))

        return send_file(
            io.BytesIO(doc["Archivo"]),
            download_name=doc["Nombre_Original"],
            as_attachment=True,
        )
        
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestión Ticket {{ ticket.ID_Ticket }} - Fortress Educa</title>

    <!-- Bootstrap 5.3 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='lib/bootstrap/css/bootstrap.min.css') }}">
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='lib/fontawesome/css/all.min.css') }}">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/ticket_panel.css') }}">

</head>

    <!--
        FORTRESS EDUCA - PLATAFORMA DE CUPOS EDUCATIVOS
        Archivo: ticket_panel.html
        Función: Panel de visualización de toda la información de un ticket. Además, de permitir ver su seguimiento y cerrarlo
    -->

<body>

    <!-- TOP NAV -->
    <nav class="topnav">
        <a class="topnav-brand" href="#">
            <i class="fas fa-shield-halved"></i>
            Fortress <span>Educa</span>
            <span class="badge bg-warning text-dark ms-2" style="font-size:.65rem; font-weight:600;">TÉCNICO</span>
        </a>
        <div class="topnav-user">
            <span class="d-none d-sm-inline">{{ tecnico.nombre_usuario }}</span>
            <div class="avatar-sm">{{ tecnico.iniciales }}</div>
        </div>
    </nav>


    <!--  PAGE WRAPPER -->
    <div class="container-fluid">

        <!-- Encabezado de página -->
        <div class="page-header">
            <h1 class="page-header-title">
                <i class="fas fa-ticket-alt text-primary"></i>
                Gestión de Ticket &nbsp;
                <code class="text-primary fw-bold" style="font-size:.95rem;">#{{ ticket.ID_Ticket }}</code>
            </h1>
            <nav aria-label="breadcrumb" class="mb-0">
                <ol class="breadcrumb mb-0" style="font-size:.8rem;">
                    <li class="breadcrumb-item"><a href="#">Panel Técnico</a></li>
                    <li class="breadcrumb-item"><a href="#">Tickets</a></li>
                    <li class="breadcrumb-item active">#{{ ticket.ID_Ticket }}</li>
                </ol>
            </nav>
        </div>

        <!-- ── Mensajes flash ── -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show mb-3" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- LAYOUT: SIDEBAR  +  PANEL PRINCIPAL  -->
        <div class="row g-4">

            <!-- SIDEBAR — INFORMACIÓN DEL TICKET -->
            <aside class="col-12 col-lg-4 col-xl-3 sticky-lg-top" style="top: 20px;">
                <div class="sidebar-card">

                    <!-- Cabecera oscura -->
                    <div class="sidebar-head">
                        <p class="ticket-id mb-0">
                            <i class="fas fa-hashtag me-1"></i>{{ ticket.ID_Ticket }}
                        </p>
                        <p class="ticket-title">{{ ticket.Titulo_Ticket }}</p>
                    </div>

                    <!-- Información básica -->
                    <div class="sidebar-body">

                        <div class="d-flex align-items-center justify-content-between mb-3">
                            <span class="info-label mb-0">Puntaje de Prioridad</span>
                            <div class="puntaje-pill">{{ ticket.Puntaje_Prioridad }}</div>
                        </div>

                        <div class="info-row">
                            <span class="info-label">Fecha de Apertura</span>
                            <span class="info-value">
                                <i class="fas fa-calendar-plus fa-xs text-muted me-1"></i>
                                {{ ticket.Fecha_Creacion.strftime('%d/%m/%Y %I:%M %p') if ticket.Fecha_Creacion else '—' }}
                            </span>
                        </div>

                        <div class="info-row">
                            <span class="info-label">Fecha de Cierre</span>
                            <span class="info-value">
                                <i class="fas fa-calendar-check fa-xs text-muted me-1"></i>
                                {{ ticket.Fecha_Cierre.strftime('%d/%m/%Y %I:%M %p') if ticket.Fecha_Cierre else 'En proceso' }}
                            </span>
                        </div>

                        <div class="info-row">
                            <span class="info-label">Estado Actual</span>
                            <span>
                                {% if ticket.Nombre_Estado == 'En Revisión' %}
                                    <span class="badge bg-warning text-dark badge-estado">{{ ticket.Nombre_Estado }}</span>
                                {% elif ticket.Nombre_Estado in ['Cerrado', 'Archivado'] %}
                                    <span class="badge bg-secondary badge-estado">{{ ticket.Nombre_Estado }}</span>
                                {% elif ticket.Nombre_Estado == 'Asignación de Cupo' %}
                                    <span class="badge bg-info text-dark badge-estado">{{ ticket.Nombre_Estado }}</span>
                                {% elif ticket.Nombre_Estado == 'Confirmación Final' %}
                                    <span class="badge bg-success badge-estado">{{ ticket.Nombre_Estado }}</span>
                                {% else %}
                                    <span class="badge bg-primary badge-estado">{{ ticket.Nombre_Estado }}</span>
                                {% endif %}
                            </span>
                        </div>

                        <div class="info-row">
                            <span class="info-label">Descripción</span>
                            <div class="desc-box">{{ ticket.Descripcion_Ticket }}</div>
                        </div>

                    </div><!-- /sidebar-body -->

                    <!-- Técnico asignado -->
                    <div class="divider-label">
                        <i class="fas fa-user-tie me-1"></i> Técnico Asignado
                    </div>
                    <div class="sidebar-body">
                        <div class="info-row">
                            <span class="info-label">ID</span>
                            <span class="info-value">
                                {{ ticket.ID_Tecnico if ticket.ID_Tecnico else '—' }}
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Nombre</span>
                            <span class="info-value">
                                <i class="fas fa-user-circle fa-xs text-muted me-1"></i>
                                {{ ticket.Nombre_Tecnico if ticket.Nombre_Tecnico else 'Sin asignar' }}
                            </span>
                        </div>
                    </div>

                    <!-- Acciones del Técnico (estado + cierre) -->
                    <div class="divider-label">
                        <i class="fas fa-sliders me-1"></i> Acciones del Ticket
                    </div>
                    <div class="sidebar-body">
                        {% if ticket.Estado_Final == 0 %}
                        <form method="POST"
                            action="{{ url_for('admin.ticket_update_estado', id_ticket=ticket.ID_Ticket) }}">
                            {{ form_estado.hidden_tag() }}

                            <div class="mb-3">
                                <label class="form-label text-muted small fw-bold">
                                    Cambiar Estado <span class="text-danger">*</span>
                                </label>
                                {{ form_estado.estado(class="form-select form-select-sm") }}
                            </div>

                            <div class="mb-3">
                                <label class="form-label text-muted small fw-bold">Fecha de Cierre</label>
                                {{ form_estado.fecha_cierre(class="form-control form-control-sm",
                                placeholder="Se establece al cerrar") }}
                                <div class="form-text">Déjela vacía si el ticket continúa abierto.</div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label text-muted small fw-bold">
                                    Resolución <span class="text-danger">*</span>
                                </label>
                                {{ form_estado.resolucion(class="form-control form-control-sm",
                                rows="3", placeholder="Describe la resolución o el motivo del cierre…") }}
                            </div>

                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary btn-sm">
                                    <i class="fas fa-save me-1"></i> Guardar Cambios
                                </button>
                            </div>
                        </form>
                        {% else %}
                        <div class="alert alert-secondary py-2 small mb-0">
                            <i class="fas fa-lock me-1"></i>
                            Este ticket está cerrado y no puede modificarse.
                        </div>
                        {% endif %}
                    </div>

                </div><!-- /sidebar-card -->
            </aside><!-- /sidebar -->


            <!-- PANEL PRINCIPAL — TABS -->
            <section class="col-12 col-lg-8 col-xl-9">

                <!-- TABS NAV -->
                <ul class="nav nav-tabs" id="ticketAdminTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="tab-comentarios"
                                data-bs-toggle="tab" data-bs-target="#pane-comentarios"
                                type="button" role="tab">
                            <i class="fas fa-comments me-1"></i> Comentarios
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="tab-asignacion"
                                data-bs-toggle="tab" data-bs-target="#pane-asignacion"
                                type="button" role="tab">
                            <i class="fas fa-school me-1"></i> Asignación Cupo
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="tab-acudiente"
                                data-bs-toggle="tab" data-bs-target="#pane-acudiente"
                                type="button" role="tab">
                            <i class="fas fa-user me-1"></i> Info Acudiente
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="tab-estudiante"
                                data-bs-toggle="tab" data-bs-target="#pane-estudiante"
                                type="button" role="tab">
                            <i class="fas fa-child me-1"></i> Info Estudiante
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="tab-documentos"
                                data-bs-toggle="tab" data-bs-target="#pane-documentos"
                                type="button" role="tab">
                            <i class="fas fa-paperclip me-1"></i> Documentos
                        </button>
                    </li>
                </ul>

                <div class="tab-content">

                    <!--  TAB 1 — COMENTARIOS -->
                    <div class="tab-pane fade show active tab-content-inner"
                        id="pane-comentarios" role="tabpanel">

                        <!-- Tabla de comentarios -->
                        <div class="inner-card mb-3">
                            <div class="inner-card-head">
                                <i class="fas fa-list-ul"></i> Historial de Comentarios
                            </div>
                            <div class="inner-card-body p-0">
                                {% if comentarios %}
                                <div class="table-responsive">
                                    <table class="table table-hover mb-0 comments-table">
                                        <thead>
                                            <tr>
                                                <th style="width:140px;">Fecha</th>
                                                <th>Comentario</th>
                                                <th style="width:90px;" class="text-center">Interno</th>
                                                <th style="width:140px;">Usuario</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for com in comentarios %}
                                            <tr>
                                                <td class="text-muted" style="font-size:.75rem; white-space:nowrap;">
                                                    {{ com.Fecha_Comentario.strftime('%d/%m/%Y') if com.Fecha_Comentario else '—' }}<br>
                                                    <span style="font-size:.7rem;">
                                                        {{ com.Fecha_Comentario.strftime('%I:%M %p') if com.Fecha_Comentario else '' }}
                                                    </span>
                                                </td>
                                                <td>{{ com.Comentario }}</td>
                                                <td class="text-center">
                                                    {% if com.Es_Interno %}
                                                        <span class="badge-interno">
                                                            <i class="fas fa-lock fa-xs me-1"></i>Interno
                                                        </span>
                                                    {% else %}
                                                        <span class="badge-publico">
                                                            <i class="fas fa-globe fa-xs me-1"></i>Público
                                                        </span>
                                                    {% endif %}
                                                </td>
                                                <td>
                                                    <span class="fw-semibold" style="font-size:.82rem;">
                                                        {{ com.Nombre_Usuario }}
                                                    </span><br>
                                                    <span class="badge bg-secondary" style="font-size:.65rem;">
                                                        {{ com.Nombre_Rol }}
                                                    </span>
                                                </td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                                {% else %}
                                <div class="text-center text-muted py-5">
                                    <i class="fas fa-comment-slash fa-2x mb-2 d-block opacity-50"></i>
                                    <p class="mb-0 small">Aún no hay comentarios en esta solicitud.</p>
                                </div>
                                {% endif %}
                            </div>
                        </div><!-- /tabla comentarios -->

                        <!-- Formulario nuevo comentario -->
                        {% if ticket.Estado_Final == 0 %}
                        <div class="inner-card">
                            <div class="inner-card-head">
                                <i class="fas fa-plus-circle"></i> Agregar Comentario
                            </div>
                            <div class="inner-card-body">
                                <form method="POST"
                                    action="{{ url_for('admin.ticket_add_comentario', id_ticket=ticket.ID_Ticket) }}">
                                    {{ form_comentario.hidden_tag() }}
                                    <div class="row g-3 align-items-end">
                                        <div class="col-12">
                                            <label class="form-label text-muted small fw-bold">
                                                Comentario <span class="text-danger">*</span>
                                            </label>
                                            {{ form_comentario.comentario(
                                                class="form-control",
                                                rows="3",
                                                placeholder="Escribe tu comentario aquí…") }}
                                        </div>
                                        <div class="col-auto d-flex align-items-center gap-2">
                                            <div class="form-check form-switch mb-0">
                                                {{ form_comentario.es_interno(class="form-check-input") }}
                                                <label class="form-check-label small fw-bold" for="{{ form_comentario.es_interno.id }}">
                                                    <i class="fas fa-lock fa-xs me-1 text-warning"></i>Interno
                                                </label>
                                            </div>
                                            <div class="form-text m-0">Solo visible para técnicos</div>
                                        </div>
                                        <div class="col-auto ms-auto">
                                            <button type="submit" class="btn btn-primary">
                                                <i class="fas fa-paper-plane me-1"></i> Agregar Comentario
                                            </button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                        {% else %}
                        <div class="alert alert-secondary py-2 small">
                            <i class="fas fa-lock me-1"></i>
                            Este ticket está cerrado. No es posible agregar comentarios.
                        </div>
                        {% endif %}

                    </div><!-- /tab comentarios -->


                    <!-- TAB 2 — ASIGNACIÓN DE CUPO -->
                    <div class="tab-pane fade tab-content-inner"
                        id="pane-asignacion" role="tabpanel">

                        <div class="alert alert-info small py-2 mb-3">
                            <i class="fas fa-info-circle me-1"></i>
                            <strong>Izquierda:</strong> datos declarados por el acudiente.
                            <strong>Derecha:</strong> campos editables para la asignación oficial del cupo.
                        </div>

                        <div class="asignacion-grid">

                            <!-- Columna lectura -->
                            <div class="inner-card">
                                <div class="inner-card-head">
                                    <i class="fas fa-eye"></i> Preferencias del Acudiente
                                </div>
                                <div class="inner-card-body">
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold">Colegio de Preferencia</label>
                                        <input type="text" class="form-control form-control-sm"
                                            value="{{ ticket.Colegio_Preferencia }}" readonly>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold">Jornada Preferida</label>
                                        <input type="text" class="form-control form-control-sm"
                                            value="{{ ticket.Jornada_Preferencia }}" readonly>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold">Tipo de Afectación</label>
                                        <input type="text" class="form-control form-control-sm"
                                            value="{{ ticket.Nombre_Afectacion }}" readonly>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold">Barrio de Residencia</label>
                                        <input type="text" class="form-control form-control-sm"
                                            value="{{ ticket.Nombre_Barrio }}" readonly>
                                    </div>
                                    <div class="mb-0">
                                        <label class="form-label text-muted small fw-bold">Tiempo de Residencia</label>
                                        <input type="text" class="form-control form-control-sm"
                                            value="{{ ticket.Tiempo_Residencia or '—' }}" readonly>
                                    </div>
                                </div>
                            </div>

                            <!-- Columna asignación (editable) -->
                            <div class="inner-card">
                                <div class="inner-card-head">
                                    <i class="fas fa-pen-to-square"></i> Asignación Oficial
                                </div>
                                <div class="inner-card-body">
                                    {% if ticket.Estado_Final == 0 %}
                                    <form method="POST"
                                        action="{{ url_for('admin.ticket_asignar_cupo', id_ticket=ticket.ID_Ticket) }}">
                                        {{ form_asignacion.hidden_tag() }}

                                        <div class="mb-3">
                                            <label class="form-label text-muted small fw-bold">
                                                Colegio Asignado <span class="text-danger">*</span>
                                            </label>
                                            {{ form_asignacion.colegio_asignado(class="form-select form-select-sm") }}
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label text-muted small fw-bold">
                                                Jornada Asignada <span class="text-danger">*</span>
                                            </label>
                                            {{ form_asignacion.jornada_asignada(class="form-select form-select-sm") }}
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label text-muted small fw-bold">
                                                Tipo de Afectación <span class="text-danger">*</span>
                                            </label>
                                            {{ form_asignacion.tipo_afectacion(class="form-select form-select-sm") }}
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label text-muted small fw-bold">
                                                Barrio <span class="text-danger">*</span>
                                            </label>
                                            {{ form_asignacion.barrio(class="form-select form-select-sm") }}
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label text-muted small fw-bold">
                                                Cupo Asignado <span class="text-danger">*</span>
                                            </label>
                                            {{ form_asignacion.cupo(class="form-select form-select-sm") }}
                                            <div class="form-text">Seleccione el cupo disponible en el sistema.</div>
                                        </div>

                                        <div class="d-grid">
                                            <button type="submit" class="btn btn-success btn-sm">
                                                <i class="fas fa-check-circle me-1"></i> Confirmar Asignación
                                            </button>
                                        </div>
                                    </form>
                                    {% else %}
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold">Colegio Asignado</label>
                                        <input type="text" class="form-control form-control-sm"
                                            value="{{ ticket.Colegio_Asignado }}" readonly>
                                    </div>
                                    <div class="alert alert-secondary py-2 small mb-0">
                                        <i class="fas fa-lock me-1"></i>
                                        Asignación bloqueada. El ticket está cerrado.
                                    </div>
                                    {% endif %}
                                </div>
                            </div>

                        </div><!-- /asignacion-grid -->
                    </div><!-- /tab asignacion -->


                    <!-- TAB 3 — INFO ACUDIENTE (solo lectura) -->
                    <div class="tab-pane fade tab-content-inner"
                        id="pane-acudiente" role="tabpanel">

                        <div class="row g-4">

                            <!-- Panel lateral -->
                            <div class="col-lg-3">
                                <div class="inner-card text-center p-3">
                                    <div class="user-avatar">{{ acudiente.iniciales }}</div>
                                    <h6 class="fw-bold mb-1">{{ acudiente.nombre_acudiente }}</h6>
                                    <p class="text-muted small mb-2">Acudiente Registrado</p>
                                    <span class="badge bg-success">Cuenta Activa</span>
                                </div>
                            </div>

                            <!-- Datos -->
                            <div class="col-lg-9">

                                <!-- Identidad -->
                                <div class="inner-card mb-3">
                                    <div class="inner-card-head">
                                        <i class="fas fa-id-card"></i> Identidad
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Primer Nombre</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Primer_Nombre }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Segundo Nombre</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Segundo_Nombre or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Primer Apellido</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Primer_Apellido }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Segundo Apellido</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Segundo_Apellido or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Tipo de Documento</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Nombre_Tipo_Iden }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Número de Documento</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Numero_Documento }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Parentesco con el Menor</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Nombre_Parentesco }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Fecha de Creación</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Fecha_Creacion }}" readonly>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Contacto -->
                                <div class="inner-card mb-3">
                                    <div class="inner-card-head">
                                        <i class="fas fa-phone"></i> Contacto
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Teléfono / Celular</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Telefono or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Correo Electrónico</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Email }}" readonly>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Ubicación -->
                                <div class="inner-card mb-3">
                                    <div class="inner-card-head">
                                        <i class="fas fa-map-marker-alt"></i> Ubicación
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-4">
                                                <label class="form-label text-muted small fw-bold">Barrio</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Nombre_Barrio or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label text-muted small fw-bold">Localidad</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Nombre_Localidad or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label text-muted small fw-bold">Estrato</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Estrato or '—' }}" readonly>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Datos demográficos -->
                                <div class="inner-card">
                                    <div class="inner-card-head">
                                        <i class="fas fa-users"></i> Datos Demográficos
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Género</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Nombre_Genero or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Grupo Preferencial</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ acudiente.Nombre_Grupo_Preferencial or '—' }}" readonly>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div><!-- /col datos -->
                        </div><!-- /row -->
                    </div><!-- /tab acudiente -->


                    <!-- TAB 4 — INFO ESTUDIANTE (solo lectura) -->
                    <div class="tab-pane fade tab-content-inner"
                        id="pane-estudiante" role="tabpanel">

                        <div class="row g-4">

                            <!-- Panel lateral -->
                            <div class="col-lg-3">
                                <div class="inner-card text-center p-3">
                                    <div class="user-avatar" style="background: linear-gradient(135deg,#16a34a,#4ade80);">
                                        <i class="fas fa-child" style="font-size:1.4rem;"></i>
                                    </div>
                                    <h6 class="fw-bold mb-1">
                                        {{ estudiante.Primer_Nombre }} {{ estudiante.Primer_Apellido }}
                                    </h6>
                                    <p class="text-muted small mb-2">Estudiante</p>
                                    <span class="badge bg-primary small">
                                        {{ estudiante.Nombre_Grado_Proximo or estudiante.Nombre_Grado_Actual }}
                                    </span>
                                </div>
                            </div>

                            <!-- Datos estudiante -->
                            <div class="col-lg-9">

                                <!-- Identificación -->
                                <div class="inner-card mb-3">
                                    <div class="inner-card-head">
                                        <i class="fas fa-id-card"></i> Identificación del Menor
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Tipo de Identificación</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Nombre_Tipo_Iden }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Número de Documento</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Numero_Documento }}" readonly>
                                            </div>
                                        </div>
                                        <p class="info-notice mb-0">
                                            <i class="fas fa-lock fa-xs"></i>
                                            El tipo de identificación no puede modificarse una vez registrado.
                                        </p>
                                    </div>
                                </div>

                                <!-- Nombre completo -->
                                <div class="inner-card mb-3">
                                    <div class="inner-card-head">
                                        <i class="fas fa-user"></i> Nombre Completo del Menor
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Primer Nombre</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Primer_Nombre }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Segundo Nombre</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Segundo_Nombre or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Primer Apellido</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Primer_Apellido }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Segundo Apellido</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Segundo_Apellido or '—' }}" readonly>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Datos demográficos -->
                                <div class="inner-card mb-3">
                                    <div class="inner-card-head">
                                        <i class="fas fa-calendar-alt"></i> Datos Demográficos
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-4">
                                                <label class="form-label text-muted small fw-bold">Fecha de Nacimiento</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Fecha_Nacimiento }}" readonly>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label text-muted small fw-bold">Edad</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Edad }}" readonly>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label text-muted small fw-bold">Género</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Nombre_Genero or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Grupo Preferencial</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Nombre_Grupo_Preferencial or '—' }}" readonly>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Datos académicos -->
                                <div class="inner-card">
                                    <div class="inner-card-head">
                                        <i class="fas fa-graduation-cap"></i> Datos Académicos
                                    </div>
                                    <div class="inner-card-body">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Último Grado Aprobado</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Nombre_Grado_Actual }}" readonly>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label text-muted small fw-bold">Grado a Cursar</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Nombre_Grado_Proximo or '—' }}" readonly>
                                            </div>
                                            <div class="col-md-12">
                                                <label class="form-label text-muted small fw-bold">Última Institución Educativa</label>
                                                <input type="text" class="form-control form-control-sm"
                                                    value="{{ estudiante.Nombre_Colegio_Anterior or '—' }}" readonly>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div><!-- /col datos estudiante -->
                        </div><!-- /row -->
                    </div><!-- /tab estudiante -->


                    <!-- TAB 5 — DOCUMENTOS -->
                    <div class="tab-pane fade tab-content-inner"
                        id="pane-documentos" role="tabpanel">

                        <!-- Lista documentos -->
                        <div class="inner-card mb-3">
                            <div class="inner-card-head">
                                <i class="fas fa-folder-open"></i> Documentos Adjuntos
                            </div>
                            <div class="inner-card-body">
                                {% if documentos %}
                                    {% for doc in documentos %}
                                    {% set ext = doc.Nombre_Original.rsplit('.', 1)[-1].lower() %}
                                    <div class="doc-item">
                                        <div class="d-flex align-items-center gap-3">
                                            {% if ext == 'pdf' %}
                                                <i class="fas fa-file-pdf text-danger fa-lg"></i>
                                            {% elif ext in ['jpg', 'jpeg', 'png'] %}
                                                <i class="fas fa-file-image text-info fa-lg"></i>
                                            {% else %}
                                                <i class="fas fa-file text-secondary fa-lg"></i>
                                            {% endif %}
                                            <div>
                                                <span class="fw-semibold" style="font-size:.85rem;">
                                                    {{ doc.Nombre_Original }}
                                                </span>
                                                <div class="doc-meta">
                                                    {{ doc.Nombre_Tipo_Doc }} ·
                                                    {{ doc.Fecha_Subida.strftime('%d/%m/%Y') if doc.Fecha_Subida else '' }}
                                                </div>
                                            </div>
                                        </div>
                                        <a href="{{ url_for('admin.ticket_download_doc', id_ticket=ticket.ID_Ticket, id_doc=doc.ID_Doc_Ticket) }}"
                                        class="btn btn-outline-primary btn-sm"
                                        title="Descargar {{ doc.Nombre_Original }}">
                                            <i class="fas fa-download"></i>
                                        </a>
                                    </div>
                                    {% endfor %}
                                {% else %}
                                    <div class="text-center text-muted py-4">
                                        <i class="fas fa-inbox fa-2x mb-2 d-block opacity-50"></i>
                                        <p class="mb-0 small">No hay documentos adjuntos en esta solicitud.</p>
                                    </div>
                                {% endif %}
                            </div>
                        </div>

                        <!-- Subir documento -->
                        <div class="inner-card">
                            <div class="inner-card-head">
                                <i class="fas fa-upload"></i> Subir Nuevo Documento
                            </div>
                            <div class="inner-card-body">
                                {% if ticket.Estado_Final == 0 %}
                                <form method="POST"
                                    action="{{ url_for('admin.ticket_upload_doc', id_ticket=ticket.ID_Ticket) }}"
                                    enctype="multipart/form-data"
                                    novalidate>
                                    {{ form_doc.hidden_tag() }}

                                    <div class="row g-3">
                                        <div class="col-md-5">
                                            <label class="form-label text-muted small fw-bold">
                                                Tipo de Documento <span class="text-danger">*</span>
                                            </label>
                                            {{ form_doc.tipo_documento(
                                                class="form-select form-select-sm" +
                                                (" is-invalid" if form_doc.tipo_documento.errors else "")) }}
                                            {% for error in form_doc.tipo_documento.errors %}
                                                <div class="invalid-feedback">{{ error }}</div>
                                            {% endfor %}
                                        </div>
                                        <div class="col-md-5">
                                            <label class="form-label text-muted small fw-bold">
                                                Seleccionar Archivo <span class="text-danger">*</span>
                                            </label>
                                            {{ form_doc.archivo(
                                                class="form-control form-control-sm" +
                                                (" is-invalid" if form_doc.archivo.errors else ""),
                                                accept=".pdf,.jpg,.jpeg,.png") }}
                                            <div class="form-text">PDF, JPG, PNG · Máx. 5 MB</div>
                                            {% for error in form_doc.archivo.errors %}
                                                <div class="invalid-feedback">{{ error }}</div>
                                            {% endfor %}
                                        </div>
                                        <div class="col-md-2 d-flex align-items-end">
                                            <button type="submit" class="btn btn-primary btn-sm w-100">
                                                <i class="fas fa-upload me-1"></i> Subir
                                            </button>
                                        </div>
                                    </div>
                                </form>
                                {% else %}
                                <div class="alert alert-secondary py-2 small mb-0">
                                    <i class="fas fa-lock me-1"></i>
                                    Esta solicitud está cerrada. No es posible adjuntar nuevos documentos.
                                </div>
                                {% endif %}
                            </div>
                        </div>

                    </div><!-- /tab documentos -->

                </div><!-- /tab-content -->
            </section><!-- /main-panel -->

        </div><!-- /ticket-layout -->
    </div><!-- /page-wrapper -->


    <!-- Bootstrap 5.3 JS (solo bundle para tabs) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
