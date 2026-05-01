from app.services.tickets.ticket_panel import Ticket_Panel_Service

class TicketsController:
    """Controlador de funciones para la parte de admin"""

    def __init__(self):
        self.ticket_panel_service = Ticket_Panel_Service()

    # TICKET PANEL
    def ticket_panel_detail(self, id_ticket: str):
        return self.ticket_panel_service.cargar_ticket_panel(id_ticket)

        # TAB COMENTARIOS
    def ticket_add_comentario(self, id_ticket: str):
        return self.ticket_panel_service.agregar_comentario(id_ticket)

        # SIDERBAR
    def ticket_update_estado(self, id_ticket: str):
        return self.ticket_panel_service.actualizar_estado(id_ticket)

        # TAB ASIGNACIÓN DE CUPO
    def ticket_asignar_cupo(self, id_ticket: str):
        return self.ticket_panel_service.asignar_cupo(id_ticket)

    def ticket_filtrar_cupo(self, id_ticket: str):
        return self.ticket_panel_service.filtrar_cupo(id_ticket)

        # TAB DOCUMENTOS
    def ticket_upload_doc(self, id_ticket: str):
        return self.ticket_panel_service.subir_documento(id_ticket)

    def ticket_download_doc(self, id_ticket: str, id_doc: int):
        return self.ticket_panel_service.descargar_documento(id_ticket, id_doc)

        # TAB COMFIRMACIÓN DE CUPO
    def ticket_autorizar_cupo(self, id_ticket: str):
        return self.ticket_panel_service.autorizar_cupo(id_ticket)

    def ticket_cancelar_cupo(self, id_ticket: str):
        return self.ticket_panel_service.cancelar_cupo(id_ticket)