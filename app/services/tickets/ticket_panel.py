import io

# FUNCIONES DE FLASK
from flask import render_template, redirect, url_for, flash, session, request, send_file, current_app
from itsdangerous import URLSafeSerializer, BadSignature

from app.repositories.tickets_repository import (
    sp_catalogo_barrios_con_colegios,
    sp_catalogo_colegios_por_barrio,
    sp_ticket_validar_cupo,
    sp_ticket_confirmar_asignacion,
    sp_ticket_obtener_abandonados,
    sp_ticket_rechazar_abandonado,
    sp_ticket_panel_consultar_detalle,
    sp_ticket_panel_comentarios_consultar,
    sp_ticket_panel_comentario_insertar,
    sp_ticket_panel_estado_actualizar,
    sp_ticket_panel_documentos_consultar,
    sp_ticket_panel_documento_descargar,
    sp_ticket_panel_documento_insertar,
    sp_ticket_panel_acudiente_consultar,
    sp_ticket_panel_estudiante_consultar,
    sp_catalogo_estados_ticket,
    sp_catalogo_jornadas,
    sp_tipo_documento_consultar,
    sp_ticket_cupo_asignado_detalle,
    sp_ticket_usuario_confirmar_cupo,
    sp_ticket_usuario_cancelar_cupo,
)

from app.forms.tickets_forms import FormCambiarEstado, FormAgregarComentario, FormConfirmarCupo, FormSubirDocumentoTecnico
from app.utils.database_utils import db

_ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
_MAX_FILE_BYTES     = 5 * 1024 * 1024


class Ticket_Panel_Service:

    def __init__(self):
        self._allowed_extensions = _ALLOWED_EXTENSIONS
        self._max_file_bytes = _MAX_FILE_BYTES

    # ----------------------------------------------------------
    # Helpers privados
    # ----------------------------------------------------------

    def _cargar_formularios(self, id_ticket: str) -> dict:
        """Instancia los formularios del panel (sin dropdowns de cupo)"""
        form_estado = FormCambiarEstado()
        estados = sp_catalogo_estados_ticket()
        form_estado.estado.choices = [(0, "-- Seleccione --")] + [
            (e["ID_Estado_Ticket"], e["Nombre_Estado"]) for e in estados
        ]

        form_comentario = FormAgregarComentario()
        form_confirmar = FormConfirmarCupo()

        form_doc = FormSubirDocumentoTecnico()
        tipos_doc = sp_tipo_documento_consultar()
        form_doc.tipo_documento.choices = [(0, "-- Seleccione --")] + [
            (t["ID_Tipo_Doc"], t["Nombre_Tipo_Doc"]) for t in tipos_doc
        ]

        return {
            "form_estado": form_estado,
            "form_comentario": form_comentario,
            "form_confirmar": form_confirmar,   # ← reemplaza form_asignacion
            "form_doc": form_doc,
        }
        
    # ----------------------------------------------------------
    # SIDERBAR DE DATOS DEL TIKET
    # ----------------------------------------------------------

    def _cargar_contexto_ticket(self, id_ticket: str) -> dict | None:
        ticket = sp_ticket_panel_consultar_detalle(id_ticket)
        if not ticket:
            return None
        comentarios = sp_ticket_panel_comentarios_consultar(id_ticket)
        documentos = sp_ticket_panel_documentos_consultar(id_ticket)
        acudiente = sp_ticket_panel_acudiente_consultar(id_ticket)
        estudiante = sp_ticket_panel_estudiante_consultar(id_ticket)
        cupo_asignado = sp_ticket_cupo_asignado_detalle(id_ticket)
        
        return {
            "ticket": ticket,
            "comentarios": comentarios,
            "documentos": documentos,
            "acudiente": acudiente,
            "estudiante": estudiante,
            "cupo_asignado": cupo_asignado,
        }
        
    def _contexto_tecnico(self) -> dict:
        nombre = session.get("nombre_usuario", "Técnico")
        partes = nombre.strip().split()
        iniciales = "".join(p[0].upper() for p in partes[:2]) if partes else "T"
        return {"nombre_usuario": nombre, "iniciales": iniciales}

    def _procesar_tickets_abandonados(self) -> None:
        """Llama a los SPs de detección y cierre de tickets abandonados. Se ejecuta en cada carga del panel para mantener estados actualizados"""
        try:
            abandonados = sp_ticket_obtener_abandonados()
            for t in abandonados:
                sp_ticket_rechazar_abandonado(
                    id_ticket = t["ID_Ticket"],
                    id_responsable = t["ID_Responsable"],
                )
            if abandonados:
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"[ERROR - abandonados] {e}")

    # ----------------------------------------------------------
    # Helpers de Firma de URL
    # ---------------------------------------------------------

    def _firmar_filtros(self, barrio_id: int, colegio_id: int = 0, jornada_id: int = 0) -> str:
        s = URLSafeSerializer(current_app.config["SECRET_KEY"], salt="cupo-filtros")
        return s.dumps({"b": barrio_id, "c": colegio_id, "j": jornada_id})

    def _leer_filtros(self, token: str) -> tuple[int, int, int]:
        """Devuelve (barrio_id, colegio_id, jornada_id) o (0,0,0) si el token es inválido"""
        if not token:
            return 0, 0, 0
        s = URLSafeSerializer(current_app.config["SECRET_KEY"], salt="cupo-filtros")
        try:
            data = s.loads(token)
            return int(data.get("b", 0)), int(data.get("c", 0)), int(data.get("j", 0))
        except (BadSignature, Exception):
            return 0, 0, 0

    # ----------------------------------------------------------
    # TAB DE ASIGNAR CUPO
    # ----------------------------------------------------------

    # Método de filtrado 
    def filtrar_cupo(self, id_ticket: str):
        """
        Recibe los valores del formulario de filtro (paso 1 o paso 2),
        los firma y redirige al panel con el token opaco.
        """
        barrio_id  = request.form.get("barrio_id",  type=int, default=0)
        colegio_id = request.form.get("colegio_id", type=int, default=0)
        jornada_id = request.form.get("jornada_id", type=int, default=0)

        token = self._firmar_filtros(barrio_id, colegio_id, jornada_id)
        return redirect(
            url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket, t=token, tab="asignacion")
        )

    def cargar_ticket_panel(self, id_ticket: str):
        """Renderiza el panel del ticket"""
        
        # Revisar tickets abandonados en cada visita al panel
        self._procesar_tickets_abandonados()

        ctx = self._cargar_contexto_ticket(id_ticket)
        if not ctx:
            flash("El ticket no existe o no está disponible.", "danger")
            return redirect(url_for("ticket_ad.cases"))

        forms = self._cargar_formularios(id_ticket)
        forms["form_estado"].estado.data = ctx["ticket"]["ID_Estado_Ticket"]

        # Decodificar el token firmado en lugar de leer IDs en texto plano
        token = request.args.get("t", "")
        barrio_id, colegio_id, jornada_id = self._leer_filtros(token)

        barrios_con_colegios = sp_catalogo_barrios_con_colegios()
        colegios_barrio = []
        jornadas = []
        cupo_info = None

        if barrio_id:
            colegios_barrio = sp_catalogo_colegios_por_barrio(barrio_id)
            jornadas = sp_catalogo_jornadas()

        if barrio_id and colegio_id and jornada_id:
            cupo_info = sp_ticket_validar_cupo(id_ticket, colegio_id, jornada_id)
        
        return render_template(
            "tickets/ticket_panel.html", 
            **ctx,
            **forms,
            tecnico = self._contexto_tecnico(),
            barrios_con_colegios = barrios_con_colegios,
            barrio_id = barrio_id,
            colegios_barrio = colegios_barrio,
            colegio_id = colegio_id,
            jornada_id = jornada_id,
            jornadas = jornadas,
            cupo_info = cupo_info,
            token_filtro = token,            
        )

    # ----------------------------------------------------------
    # Confirmación de cupo (POST)
    # ----------------------------------------------------------

    def asignar_cupo(self, id_ticket: str):
        """Valida CSRF y confirma la asignación del cupo"""
        form = FormConfirmarCupo()

        # 1. Validar solo el token CSRF
        if not form.validate_on_submit():
            flash("Solicitud inválida. Vuelva a intentarlo.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

        # 2. Leer id_cupo directamente del request (evita conflictos de WTForms)
        id_cupo = request.form.get("id_cupo", type=int)
        
        print(id_cupo)
        if not id_cupo:
            flash("No se recibió un cupo válido. Intente nuevamente.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

        try:
            sp_ticket_confirmar_asignacion(
                id_ticket = id_ticket,
                id_cupo = id_cupo,
                id_tecnico = session["user_id"],
            )
            db.commit()
            flash(
                "Cupo asignado correctamente. Se ha notificado al usuario "
                "y el ticket queda en espera de su confirmación.",
                "success",
            )
        except Exception as e:
            db.rollback()
            print(f"[ERROR - cupo] {e}")
            flash("No se pudo asignar el cupo. Intente nuevamente.", "danger")

        return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))


    #  autorizar cupo 
    def autorizar_cupo(self, id_ticket: str):
        form = FormConfirmarCupo()
        if not form.validate_on_submit():
            flash("Solicitud inválida.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))
        try:
            sp_ticket_usuario_confirmar_cupo(
                id_ticket  = id_ticket,
                id_tecnico = session["user_id"],
            )
            db.commit()
            flash("Cupo confirmado. El ticket ha sido marcado como Solucionado.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - autorizar cupo] {e}")
            flash("No se pudo confirmar el cupo. Intente nuevamente.", "danger")
        return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

    #  cancelar cupo 
    def cancelar_cupo(self, id_ticket: str):
        form = FormConfirmarCupo()
        if not form.validate_on_submit():
            flash("Solicitud inválida.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))
        try:
            sp_ticket_usuario_cancelar_cupo(
                id_ticket  = id_ticket,
                id_tecnico = session["user_id"],
            )
            db.commit()
            flash("Cupo cancelado. El ticket vuelve a Asignación de Cupo.", "warning")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - cancelar cupo] {e}")
            flash("No se pudo cancelar el cupo. Intente nuevamente.", "danger")
        return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))


    # ----------------------------------------------------------
    # TAB COMENTARIOS
    # ----------------------------------------------------------

    def agregar_comentario(self, id_ticket: str):
        form = FormAgregarComentario()
        if not form.validate_on_submit():
            flash("Por favor revise el comentario antes de enviarlo.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))
        try:
            sp_ticket_panel_comentario_insertar(
                id_ticket = id_ticket,
                tipo_evento = "Comentario",
                id_usuario = session["user_id"],
                comentario = form.comentario.data.strip(),
                es_interno = form.es_interno.data,
            )
            db.commit()
            flash("Comentario agregado correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - comentario] {e}")
            flash("Ocurrió un error al guardar el comentario.", "danger")
        return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

    def actualizar_estado(self, id_ticket: str):
        form_estado = FormCambiarEstado()
        estados = sp_catalogo_estados_ticket()
        form_estado.estado.choices = [(0, "-- Seleccione --")] + [
            (e["ID_Estado_Ticket"], e["Nombre_Estado"]) for e in estados
        ]
        if not form_estado.validate_on_submit():
            flash("Por favor revise los campos antes de guardar.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))
        fecha_cierre = form_estado.fecha_cierre.data or None
        try:
            sp_ticket_panel_estado_actualizar(
                id_ticket = id_ticket,
                id_estado_nuevo = form_estado.estado.data,
                fecha_cierre = fecha_cierre,
                resolucion = form_estado.resolucion.data.strip(),
                id_tecnico = session["user_id"],
            )
            db.commit()
            flash("Estado del ticket actualizado correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - estado] {e}")
            flash("No se pudo actualizar el estado.", "danger")
        return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

    # ----------------------------------------------------------
    # TAB DOCUMENTOS
    # ----------------------------------------------------------

    def subir_documento(self, id_ticket: str):
        form_doc = FormSubirDocumentoTecnico()
        tipos_doc = sp_tipo_documento_consultar()
        form_doc.tipo_documento.choices = [(0, "-- Seleccione --")] + [
            (t["ID_Tipo_Doc"], t["Nombre_Tipo_Doc"]) for t in tipos_doc
        ]
        if not form_doc.validate_on_submit():
            flash("Por favor revise el formulario de documentos.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

        archivo_field = form_doc.archivo.data
        nombre_original = archivo_field.filename
        extension = nombre_original.rsplit(".", 1)[-1].lower()

        if extension not in self._allowed_extensions:
            flash("Tipo de archivo no permitido. Solo PDF, JPG o PNG.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

        contenido = archivo_field.read()
        if len(contenido) > self._max_file_bytes:
            flash("El archivo supera el límite de 5 MB.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

        try:
            sp_ticket_panel_documento_insertar(
                id_ticket = id_ticket,
                id_tipo_doc = form_doc.tipo_documento.data,
                archivo = contenido,
                nombre_original = nombre_original,
            )
            sp_ticket_panel_comentario_insertar(
                id_ticket  = id_ticket,
                tipo_evento = "Documento Subido",
                id_usuario = session["user_id"],
                comentario = f"[Documento Subido] {nombre_original}",
                es_interno = True,
            )
            db.commit()
            flash("Documento subido correctamente.", "success")
        except Exception as e:
            db.rollback()
            print(f"[ERROR - documento upload] {e}")
            flash("Ocurrió un error al subir el documento.", "danger")

        return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))

    def descargar_documento(self, id_ticket: str, id_doc: int):
        doc = sp_ticket_panel_documento_descargar(id_doc)
        if not doc:
            flash("Documento no encontrado.", "danger")
            return redirect(url_for("ticket_ad.ticket_panel_detail", id_ticket=id_ticket))
        return send_file(
            io.BytesIO(doc["Archivo"]),
            download_name=doc["Nombre_Original"],
            as_attachment=True,
        )