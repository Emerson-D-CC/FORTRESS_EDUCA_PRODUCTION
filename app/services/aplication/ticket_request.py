# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session

# UTILIDADES
from app.utils.database_utils import db


# CONFIGURACIONES LOCALES
from app.forms.aplication_forms import *
from app.repositories.aplication_repository import *


# ====================================================================================================================================================
#                                           PÁGINA TICKET_REQUEST.HTML
# ====================================================================================================================================================

# Tamaño máximo de archivo en bytes
_MAX_FILE_SIZE = 5 * 1024 * 1024   # 5 MB
_MAX_FILE_SIZE_CERTS = 10 * 1024 * 1024  # 10 MB para certificados

# SelectFields obligatorios del ticket (valor 0 = sin selección)
_SELECTS_REQUERIDOS_TICKET = {
    "id_estudiante":       "form_p1",
    "id_tipo_afectacion":  "form_p2",
    "id_barrio":           "form_p3",
    "id_tiempo_residencia":"form_p3",
    "id_jornada":          "form_p4",
}


def _generar_id_ticket():
    """Genera el ID de ticket en formato EDU-000000"""
    ultimo = sp_ticket_obtener_ultimo_numero()
    
    if ultimo is None:
        ultimo = 0
        
    ultimo = int(ultimo)
    siguiente = ultimo + 1
    return f"EDU-{siguiente:06d}"


def _form_opciones_ticket(form_p1, form_p2, form_p3, form_p4, lista_est):
    """Pobla los choices de los SelectFields del wizard"""
    # Paso 1 — estudiantes
    form_p1.id_estudiante.choices = (
        [(0, "— Seleccione un estudiante —")] +
        [
            (e["ID_Estudiante"],
             f"{e['Primer_Nombre']} {e['Primer_Apellido']}"
             f" — {e.get('Nombre_Grado_Proximo') or e.get('Nombre_Grado_Actual', '')}")
            for e in lista_est
        ]
    )

    # Paso 2 — tipos de afectación
    form_p2.id_tipo_afectacion.choices = (
        [(0, "— Seleccione una afectación —")] +
        [(a["ID_Tipo_Afectacion"], a["Nombre_Afectacion"])
         for a in sp_obtener_tipos_afectacion()]
    )

    # Paso 3 — barrios y tiempos de residencia
    form_p3.id_barrio.choices = (
        [(0, "— Seleccione un barrio —")] +
        [(b["ID_Barrio"], b["Nombre_Barrio"]) for b in sp_obtener_barrios()]
    )
    form_p3.id_tiempo_residencia.choices = (
        [(0, "— Seleccione —")] +
        [(t["ID_Tiempo_Residencia"], t["Nombre_Tiempo"])
         for t in sp_obtener_tiempos_residencia()]
    )

    # Paso 4 — jornadas y colegios
    form_p4.id_jornada.choices = (
        [(0, "— Seleccione una jornada —")] +
        [(j["ID_Jornada"], j["Nombre_Jornada"]) for j in sp_obtener_jornadas()]
    )
    form_p4.id_colegio.choices = (
        [(0, "Sin preferencia (el sistema asignará)")] +
        [(c["ID_Colegio"], c["Nombre_Colegio"]) for c in sp_obtener_colegios()]
    )


def _leer_archivo(file_storage, max_size=_MAX_FILE_SIZE):
    """Lee un FileStorage y retorna los bytes"""
    if not file_storage or file_storage.filename == "":
        return None
    datos = file_storage.read()
    if len(datos) > max_size:
        raise ValueError(f"El archivo '{file_storage.filename}' supera el tamaño permitido.")
    return datos



class Ticket_Request_Service:
    """Gestión de opciones para la creación de un tickets"""

    def Crear_Ticket(self):
        user_id = session.get("user_id")
        if not user_id:
            flash("Sesión no encontrada.", "danger")
            return redirect(url_for("aplication.dashboard"))

        # Verificar que el acudiente tiene al menos un estudiante
        lista_est = sp_obtener_estudiantes_por_acudiente(user_id)
        if not lista_est:
            flash("Debes registrar al menos un estudiante antes de crear una solicitud.", "info")
            return redirect(url_for("aplication.register_student"))

        # Instanciar todos los formularios
        form_p1 = FormTicketPaso1()
        form_p2 = FormTicketPaso2()
        form_p3 = FormTicketPaso3()
        form_p4 = FormTicketPaso4()
        form_p5 = FormTicketPaso5()
        form_p6 = FormTicketPaso6()

        # Poblar SelectFields
        _form_opciones_ticket(form_p1, form_p2, form_p3, form_p4, lista_est)

        # Catálogo de afectaciones para el template (radio buttons)
        tipos_afectacion = sp_obtener_tipos_afectacion()

        if request.method == "GET":
            return render_template(
                "aplication/ticket_request.html",
                form_p1=form_p1,
                form_p2=form_p2,
                form_p3=form_p3,
                form_p4=form_p4,
                form_p5=form_p5,
                form_p6=form_p6,
                tipos_afectacion=tipos_afectacion,
                active_page="request",
            )

        # POST

        # Validar todos los formularios juntos
        forms_validos = all([
            form_p1.validate_on_submit(),
            form_p2.validate_on_submit(),
            form_p3.validate_on_submit(),
            form_p4.validate_on_submit(),
            form_p5.validate_on_submit(),
            form_p6.validate_on_submit(),
        ])

        if not forms_validos:
            errores = {}
            for f in [form_p1, form_p2, form_p3, form_p4, form_p5, form_p6]:
                errores.update(f.errors)
            print(f"[FORM ERRORS TICKET] {errores}")
            flash("Por favor revise todos los campos del formulario.", "danger")
            return render_template(
                "aplication/ticket_request.html",
                form_p1=form_p1,
                form_p2=form_p2,
                form_p3=form_p3,
                form_p4=form_p4,
                form_p5=form_p5,
                form_p6=form_p6,
                tipos_afectacion=tipos_afectacion,
                active_page="request",
            )

        # Segunda validación para SelectFields == 0
        form_map = {
            "form_p1": form_p1, "form_p2": form_p2,
            "form_p3": form_p3, "form_p4": form_p4,
        }
        
        campos_invalidos = [
            campo for campo, form_key in _SELECTS_REQUERIDOS_TICKET.items()
            if getattr(form_map[form_key], campo).data == 0
        ]
        
        if campos_invalidos:
            flash("Hay campos de selección sin completar.", "danger")
            return render_template(
                "aplication/ticket_request.html",
                form_p1=form_p1,
                form_p2=form_p2,
                form_p3=form_p3,
                form_p4=form_p4,
                form_p5=form_p5,
                form_p6=form_p6,
                tipos_afectacion=tipos_afectacion,
                active_page="request",
            )

        id_estudiante = form_p1.id_estudiante.data

        # Verificar que el estudiante no tenga ya un ticket activo
        if sp_ticket_verificar_activo(id_estudiante, user_id):
            flash("Este estudiante ya tiene una solicitud activa en proceso.", "warning")
            return render_template(
                "aplication/ticket_request.html",
                form_p1=form_p1,
                form_p2=form_p2, 
                form_p3=form_p3,
                form_p4=form_p4,
                form_p5=form_p5,
                form_p6=form_p6,
                tipos_afectacion=tipos_afectacion,
                active_page="request",
            )

        # Colegio: 0 = sin preferencia → NULL
        id_colegio = form_p4.id_colegio.data if form_p4.id_colegio.data != 0 else None
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent")
        
        id_ticket = _generar_id_ticket()

        try:
            sp_ticket_crear((
                id_ticket,
                user_id,
                id_estudiante,
                form_p2.id_tipo_afectacion.data,
                form_p2.descripcion.data,
                form_p3.id_barrio.data,
                form_p3.id_tiempo_residencia.data,
                form_p4.id_jornada.data,
                id_colegio,
                ip,
                user_agent,
            ))

            # Documentos individuales: (file_storage, id_tipo_doc, max_size)
            archivos = [
                (form_p5.doc_acudiente.data, 1, _MAX_FILE_SIZE),
                (form_p5.doc_menor.data, 2, _MAX_FILE_SIZE),
                (form_p5.doc_victima.data, 4, _MAX_FILE_SIZE),
            ]
            for file_storage, id_tipo_doc, max_size in archivos:
                datos = _leer_archivo(file_storage, max_size)
                if datos:
                    sp_documento_ticket_insertar(
                        id_ticket, id_tipo_doc, datos, file_storage.filename
                    )

            # Certificados múltiples
            for cert in (form_p5.doc_certificados.data or []):
                datos = _leer_archivo(cert, _MAX_FILE_SIZE_CERTS)
                if datos:
                    sp_documento_ticket_insertar(
                        id_ticket, 3, datos, cert.filename
                    )

            db.commit()
            flash(f"Solicitud {id_ticket} creada correctamente. La revisaremos pronto.", "success")
            return redirect(url_for("aplication.ticket_status"))

        except ValueError as ve:
            db.rollback()
            flash(str(ve), "warning")
        except Exception as e:  
            db.rollback()
            print(f"[ERROR] Creación de ticket fallida: {e}")
            flash("Ocurrió un error al crear la solicitud. Intente nuevamente.", "danger")

        return render_template(
            "aplication/ticket_request.html",
            form_p1=form_p1,
            form_p2=form_p2,
            form_p3=form_p3,
            form_p4=form_p4,
            form_p5=form_p5,
            form_p6=form_p6,
            tipos_afectacion=tipos_afectacion,
            active_page="request",
        )