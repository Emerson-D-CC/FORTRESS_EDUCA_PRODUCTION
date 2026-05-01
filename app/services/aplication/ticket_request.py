# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session

# UTILIDADES
from app.utils.database_utils import db

# REPOSITORIO
from app.repositories.aplication_repository import (
    sp_ticket_obtener_ultimo_numero,
    sp_obtener_estudiantes_por_acudiente,
    sp_obtener_tipos_afectacion,
    sp_obtener_barrios,
    sp_obtener_tiempos_residencia,
    sp_obtener_jornadas,
    sp_obtener_colegios,
    sp_ticket_verificar_activo,
    sp_ticket_crear,
    sp_documento_ticket_insertar,
)

# FORMULARIOS
from app.forms.aplication_forms import (
    FormTicketPaso1, FormTicketPaso2, FormTicketPaso3,
    FormTicketPaso4, FormTicketPaso5, FormTicketPaso6,
)

# ====================================================================================================================================================
#                                           PÁGINA TICKET_REQUEST.HTML
# ====================================================================================================================================================

# Tamaño máximo de archivo en bytes
_MAX_FILE_SIZE = 5  * 1024 * 1024   # 5  MB — documentos individuales
_MAX_FILE_SIZE_CERTS = 10 * 1024 * 1024   # 10 MB — certificados/boletines

# SelectFields obligatorios (valor 0 = sin selección)
_SELECTS_REQUERIDOS_TICKET = {
    "id_estudiante": "form_p1",
    "id_tipo_afectacion": "form_p2",
    "id_barrio": "form_p3",
    "id_tiempo_residencia": "form_p3",
    "id_jornada": "form_p4",
}

# Mapeo campo → paso del wizard (para llevar al usuario al paso correcto)
_CAMPO_A_PASO = {
    "id_estudiante": 1,
    "id_tipo_afectacion": 2,
    "descripcion": 2,
    "id_barrio": 3,
    "id_tiempo_residencia": 3,
    "id_jornada": 4,
    "id_colegio": 4,
    "doc_acudiente": 5,
    "doc_menor": 5,
    "doc_certificados": 5,
    "doc_victima": 5,
    "acepta_terminos": 6,
}

# Campos de archivo — no se pueden almacenar en sesión
_CAMPOS_ARCHIVO = {"doc_acudiente", "doc_menor", "doc_certificados", "doc_victima"}


# ==============================================================================
# Helpers privados
# ==============================================================================

def _generar_id_ticket() -> str:
    """Genera el ID de ticket en formato EDU-000000"""
    ultimo = sp_ticket_obtener_ultimo_numero()
    ultimo = int(ultimo) if ultimo is not None else 0
    return f"EDU-{(ultimo + 1):06d}"


def _form_opciones_ticket(form_p1, form_p2, form_p3, form_p4, lista_est: list) -> None:
    """Pobla los choices de los SelectFields del wizard desde la BD"""

    # Paso 1 — estudiantes del acudiente
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


def _leer_archivo(file_storage, max_size: int = _MAX_FILE_SIZE) -> bytes | None:
    """Lee un FileStorage y retorna los bytes. Lanza ValueError si supera el límite"""
    if not file_storage or file_storage.filename == "":
        return None
    datos = file_storage.read()
    if len(datos) > max_size:
        raise ValueError(f"El archivo '{file_storage.filename}' supera el tamaño permitido.")
    return datos


def _detectar_paso_error(errores: dict) -> int:
    """Recorre el diccionario de errores y retorna el número del primer paso que contiene un campo inválido"""
    for campo in errores:
        if campo in _CAMPO_A_PASO:
            return _CAMPO_A_PASO[campo]
    return 1


def _recopilar_datos_sesion() -> dict:
    """Extrae los datos del request.form excluyendo archivos y el token CSRF"""
    excluir = _CAMPOS_ARCHIVO | {"csrf_token"}
    return {k: v for k, v in request.form.to_dict().items() if k not in excluir}


def _repoblar_formularios(form_data: dict, forms: list) -> None:
    """Itera sobre los campos de cada formulario y asigna el valor guardado en sesión"""
    for form in forms:
        for field_name, field in form._fields.items():
            # Omitir csrf_token y campos de archivo
            if field_name in _CAMPOS_ARCHIVO or field_name == "csrf_token":
                continue

            valor = form_data.get(field_name)
            if valor is None:
                continue

            # BooleanField: 'y' o 'on' = True
            if hasattr(field, '_value') and isinstance(field.widget.__class__.__name__, str) \
                    and 'checkbox' in field.widget.__class__.__name__.lower():
                field.data = valor in ('y', 'on', 'true', '1')

            # SelectField con coerce=int
            elif hasattr(field, 'coerce') and field.coerce == int:
                try:
                    field.data = int(valor)
                except (ValueError, TypeError):
                    field.data = 0

            else:
                field.data = valor


def _inyectar_errores(form_errors: dict, forms: list) -> None:
    """Asigna la lista de mensajes de error a cada campo del formulario correspondiente para que Jinja2 los muestre en el template"""
    for form in forms:
        for field_name in form._fields:
            if field_name in form_errors:
                getattr(form, field_name).errors = form_errors[field_name]


def _render_ticket(form_p1, form_p2, form_p3, form_p4, form_p5, form_p6, tipos_afectacion, mostrar_modal_estudiante=False, initial_step=1):
    """Helper centralizado para renderizar el template del wizard."""
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
        mostrar_modal_estudiante=mostrar_modal_estudiante,
        initial_step=initial_step,
    )


# ==============================================================================
# Servicio principal
# ==============================================================================

class Ticket_Request_Service:
    """Gestión de la creación de tickets con retroalimentación por sesión."""

    def Crear_Ticket(self):

        # Verificar sesión activa
        user_id = session.get("user_id")
        if not user_id:
            flash("Sesión no encontrada.", "danger")
            return redirect(url_for("aplication.dashboard"))

        # Verificar estudiantes registrados
        lista_est = sp_obtener_estudiantes_por_acudiente(user_id)
        mostrar_modal_estudiante = not bool(lista_est)

        # Instanciar formularios
        form_p1 = FormTicketPaso1()
        form_p2 = FormTicketPaso2()
        form_p3 = FormTicketPaso3()
        form_p4 = FormTicketPaso4()
        form_p5 = FormTicketPaso5()
        form_p6 = FormTicketPaso6()

        # Poblar choices desde la BD
        _form_opciones_ticket(form_p1, form_p2, form_p3, form_p4, lista_est)
        tipos_afectacion = sp_obtener_tipos_afectacion()

        todos_los_forms = [form_p1, form_p2, form_p3, form_p4, form_p5, form_p6]

        # ==============================================================================
        # GET — Renderizar (con o sin datos de sesión previos)

        if request.method == "GET":

            initial_step = 1  # paso por defecto

            if "ticket_form_errors" in session:
                # Recuperar datos y errores almacenados en el POST fallido
                form_data = session.pop("ticket_form_data", {})
                form_errors = session.pop("ticket_form_errors", {})
                initial_step = session.pop("ticket_step_error", 1)

                # Repoblar campos con los valores que el usuario ingresó
                _repoblar_formularios(form_data, todos_los_forms)

                # Inyectar mensajes de error en cada campo
                _inyectar_errores(form_errors, todos_los_forms)

                # Emitir flash si había uno pendiente
                if "flash_message" in session:
                    flash(
                        session.pop("flash_message"),
                        session.pop("flash_category", "danger"),
                    )

            return _render_ticket(
                form_p1, form_p2, form_p3, form_p4, form_p5, form_p6,
                tipos_afectacion,
                mostrar_modal_estudiante=mostrar_modal_estudiante,
                initial_step=initial_step,
            )

        # ==============================================================================
        # POST — Procesar solicitud

        # Validación WTForms
        forms_validos = all(f.validate_on_submit() for f in todos_los_forms)

        if not forms_validos:
            # Recopilar todos los errores de los 6 formularios
            errores_consolidados = {}
            for f in todos_los_forms:
                errores_consolidados.update(f.errors)

            print(f"[FORM ERRORS TICKET] {errores_consolidados}")

            # Detectar en qué paso están los primeros errores
            paso_error = _detectar_paso_error(errores_consolidados)

            # Persistir en sesión para recuperar en el GET
            session["ticket_form_data"] = _recopilar_datos_sesion()
            session["ticket_form_errors"] = errores_consolidados
            session["ticket_step_error"] = paso_error
            session["flash_message"] = "Por favor revise los campos indicados en el formulario."
            session["flash_category"] = "danger"

            return redirect(url_for("aplication.ticket_request"))

        # Segunda validación: SelectFields con valor 0
        form_map = {
            "form_p1": form_p1, "form_p2": form_p2,
            "form_p3": form_p3, "form_p4": form_p4,
        }

        campos_sin_seleccion = [
            campo
            for campo, form_key in _SELECTS_REQUERIDOS_TICKET.items()
            if getattr(form_map[form_key], campo).data == 0
        ]

        if campos_sin_seleccion:
            # Construir errores manuales para los campos sin selección
            errores_selects = {campo: ["Debe seleccionar una opción válida."]
                               for campo in campos_sin_seleccion}
            paso_error = _detectar_paso_error(errores_selects)

            session["ticket_form_data"] = _recopilar_datos_sesion()
            session["ticket_form_errors"] = errores_selects
            session["ticket_step_error"] = paso_error
            session["flash_message"] = "Hay campos de selección sin completar."
            session["flash_category"] = "danger"

            return redirect(url_for("aplication.ticket_request"))

        # Verificar ticket activo para el estudiante
        id_estudiante = form_p1.id_estudiante.data

        if sp_ticket_verificar_activo(id_estudiante, user_id):
            session["ticket_form_data"] = _recopilar_datos_sesion()
            session["ticket_form_errors"] = {}
            session["ticket_step_error"] = 1
            session["flash_message"] = "Este estudiante ya tiene una solicitud activa en proceso."
            session["flash_category"] = "warning"

            return redirect(url_for("aplication.ticket_request"))

        # Crear ticket en BD
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

            # Documentos individuales
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
                    sp_documento_ticket_insertar(id_ticket, 3, datos, cert.filename)

            db.commit()

            # Limpiar cualquier dato de sesión previo del wizard
            for key in ("ticket_form_data", "ticket_form_errors",
                        "ticket_step_error", "flash_message", "flash_category"):
                session.pop(key, None)

            flash(f"Solicitud {id_ticket} creada correctamente. La revisaremos pronto.", "success")
            return redirect(url_for("aplication.ticket_status"))

        except ValueError as ve:
            db.rollback()
            # Error de tamaño de archivo — regresar al paso 5
            session["ticket_form_data"] = _recopilar_datos_sesion()
            session["ticket_form_errors"] = {}
            session["ticket_step_error"] = 5
            session["flash_message"] = str(ve)
            session["flash_category"] = "warning"
            return redirect(url_for("aplication.ticket_request"))

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Creación de ticket fallida: {e}")
            session["ticket_form_data"] = _recopilar_datos_sesion()
            session["ticket_form_errors"] = {}
            session["ticket_step_error"]  = 1
            session["flash_message"] = "Ocurrió un error al crear la solicitud. Intente nuevamente."
            session["flash_category"] = "danger"
            return redirect(url_for("aplication.ticket_request"))