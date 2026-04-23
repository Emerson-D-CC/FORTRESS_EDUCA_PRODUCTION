import io

# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session, send_file

# UTILIDADES
from app.utils.database_utils import db

# CONFIGURACIONES LOCALES
from app.forms.aplication_forms import *
from app.repositories.aplication_repository import *

# ====================================================================================================================================================
#                                           SISTEMA DE TICKETS - SEGUIMIENTO DE SOLICITUDES DE CUPO
# ====================================================================================================================================================

_ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
_MAX_FILE_BYTES     = 5 * 1024 * 1024  # 5 MB


def _form_opciones_subir_documento(form):
    """Carga los tipos de documento en el SelectField."""
    tipos = sp_tipo_documento_consultar()
    form.tipo_documento.choices = [(0, "-- Seleccione --")] + [
        (t["ID_Tipo_Doc"], t["Nombre_Tipo_Doc"]) for t in tipos
    ]


# Definición del flujo de estados

_PASOS_TIMELINE = [
    {
        "label":      "Solicitud Enviada",
        "icono":      "fa-paper-plane",
        "estados_bd": ["Abierto"],
    },
    {
        "label":      "En Revisión",
        "icono":      "fa-eye",
        "estados_bd": ["En Revisión"],
    },
    {
        "label":      "Validación de Documentos",
        "icono":      "fa-clipboard-check",
        "estados_bd": ["Validación de Documentos", "Pendiente Acción de Usuario"],
    },
    {
        "label":      "Asignación de Cupo",
        "icono":      "fa-school",
        "estados_bd": ["Asignación de Cupo"],
    },
    {
        "label":      "Confirmación Final",
        "icono":      "fa-flag-checkered",
        "estados_bd": ["Solucionado"],
    },
]

# Estados que terminan el proceso de forma NO exitosa.
_ESTADOS_RECHAZO = {"Rechazado", "Cancelado a Petición"}

# Estados que terminan el proceso de forma exitosa.
_ESTADOS_EXITOSOS = {"Solucionado"}


def _construir_timeline(nombre_estado_actual: str) -> tuple[list[dict], str]:
    """Construye la lista de pasos del timeline según el estado actual del ticket"""

    # Determinar el índice del paso activo buscando qué paso del timeline corresponde al estado actual de la BD
    idx_activo = None
    for i, paso in enumerate(_PASOS_TIMELINE):
        if nombre_estado_actual in paso["estados_bd"]:
            idx_activo = i
            break

    # Si el estado no coincide con ningún paso (ej: Rechazado, Cancelado),
    estado_ticket_rechazo = nombre_estado_actual in _ESTADOS_RECHAZO
    estado_ticket_exitoso = nombre_estado_actual in _ESTADOS_EXITOSOS

    if estado_ticket_exitoso:
        # Todos los pasos completados
        idx_activo = len(_PASOS_TIMELINE)
        tipo = "exitoso"
    elif estado_ticket_rechazo:
        # El proceso terminó sin completarse: no hay paso activo,
        idx_activo = None
        tipo = "rechazo"
    else:
        tipo = "normal"

    pasos = []
    for i, paso in enumerate(_PASOS_TIMELINE):
        if estado_ticket_rechazo:
            # En rechazo: todos los pasos quedan como completados hasta donde llego
        
            estado_paso = "completed" if i < (idx_activo or 0) else ""
        elif idx_activo is None:
            estado_paso = ""
        elif i < idx_activo:
            estado_paso = "completed"
        elif i == idx_activo:
            # 'Pendiente Acción de Usuario' merece un estado visual distinto
            if nombre_estado_actual == "Pendiente Acción de Usuario":
                estado_paso = "warning"
            else:
                estado_paso = "active"
        else:
            estado_paso = ""

        pasos.append({
            "label":  paso["label"],
            "icono":  paso["icono"],
            "estado": estado_paso,
        })

    return pasos, tipo

# Clases de servicio

class Ticket_Detail_Service:
    """Mostrar tickets creados y su información"""

    def listar_tickets(self):

        user_id = session["user_id"]
        
        # Tickets Abiertos
        tickets_ab = sp_ticket_consultar_por_usuario(user_id)
        # Tickets Cerrados
        tickets_cer = sp_ticket_cerrado_consultar_por_usuario(user_id)
        
        return render_template(
            "aplication/ticket_status.html",
            tickets_ab=tickets_ab,
            tickets_cer=tickets_cer,
            active_page="status",
        )

    def cargar_datos_ticket(self, id_ticket: str):
        user_id = session["user_id"]

        ticket = sp_ticket_consultar_detalle(id_ticket, user_id)
        if not ticket:
            flash("La solicitud no existe o no tiene permisos para verla.", "danger")
            return redirect(url_for("aplication.ticket_status"))

        comentarios = sp_ticket_comentarios_consultar(id_ticket, user_id)
        documentos  = sp_ticket_documentos_consultar(id_ticket, user_id)

        # _construir_timeline ahora retorna (pasos, tipo)
        timeline, timeline_tipo = _construir_timeline(ticket["Nombre_Estado"])

        form = FormSubirDocumento()
        _form_opciones_subir_documento(form)

        ctx = dict(
            ticket = ticket,
            comentarios = comentarios,
            documentos = documentos,
            timeline = timeline,
            timeline_tipo = timeline_tipo,
            form = form,
            active_page="status",
        )

        if request.method == "GET":
            return render_template("aplication/ticket_detail.html", **ctx)

        # POST: subir documento
        if not form.validate_on_submit():
            errores = "; ".join(
                f"{field}: {', '.join(msgs)}"
                for field, msgs in form.errors.items()
            )
            print(f"[FORM ERRORS] {errores}")
            flash("Por favor revise los campos del formulario.", "danger")
            return render_template("aplication/ticket_detail.html", **ctx)

        archivo_field = form.archivo.data
        nombre_original = archivo_field.filename
        extension = nombre_original.rsplit(".", 1)[-1].lower()

        if extension not in _ALLOWED_EXTENSIONS:
            flash("Tipo de archivo no permitido.", "danger")
            return render_template("aplication/ticket_detail.html", **ctx)

        contenido = archivo_field.read()

        if len(contenido) > _MAX_FILE_BYTES:
            flash("El archivo supera el límite de 5 MB.", "danger")
            return render_template("aplication/ticket_detail.html", **ctx)

        try:
            sp_documento_ticket_insertar(
                id_ticket,
                form.tipo_documento.data,
                contenido,
                nombre_original,
            )
            sp_documento_comentario_insertar(
                id_ticket=id_ticket,
                tipo_evento="Documento Subido",
                id_usuario=session["user_id"],
                comentario=f"[Documento Subido] El usuario ha subido el documento: {nombre_original}",
                es_interno=0,
            )
            
            db.commit()
            flash("Documento subido correctamente.", "success")
            return redirect(url_for("aplication.ticket_detail", id_ticket=id_ticket, active_page="status"))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Subida de documento fallida: {e}")
            flash("Ocurrió un error al subir el documento. Intente nuevamente.", "danger")
            return render_template("aplication/ticket_detail.html", **ctx)


    def descargar_doc(self, id_ticket: str, id_doc: int):
        user_id = session["user_id"]

        doc = sp_documento_ticket_descargar(id_doc, user_id)
        if not doc:
            flash("Documento no encontrado o sin permisos.", "danger")
            return redirect(url_for("aplication.ticket_detail", id_ticket=id_ticket, active_page="status"))

        return send_file(
            io.BytesIO(doc["Archivo"]),
            download_name=doc["Nombre_Original"],
            as_attachment=True,
        )