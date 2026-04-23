import csv
import io
import math

from flask import Response, render_template, request

from app.repositories.admin_repository import sp_history_contar_auditoria, sp_history_exportar_auditoria, sp_history_listar_auditoria

# Eventos válidos (coinciden con los valores almacenados en BD)
TIPOS_EVENTO = [
    ("Nueva Solicitud", "Nueva Solicitud de Cupo"),
    ("Comentario", "Comentario"),
    ("Cambio Estado", "Cambio de Estado"),
    ("Documento Subido", "Documento Subido"),
    ("Cambio Tecnico", "Cambio de Técnico"),
    ("Cupo Asignado", "Asignación de Cupo"),
    ("Cierre Solicitud", "Cierre de Solicitud"),
]

POR_PAGINA = 15


class History_Service:
    """Servicio para el módulo de historial y auditoría."""

    # Vista principal con filtros y paginación
    def listar_auditoria(self):
        tipo_evento = request.args.get("tipo_evento") or None
        fecha_desde = request.args.get("fecha_desde") or None
        fecha_hasta = request.args.get("fecha_hasta") or None
        pagina = self._parse_pagina(request.args.get("pagina"))

        # Validar que tipo_evento sea un valor permitido
        valores_validos = {v for v, _ in TIPOS_EVENTO}
        if tipo_evento and tipo_evento not in valores_validos:
            tipo_evento = None

        registros = sp_history_listar_auditoria(tipo_evento, fecha_desde, fecha_hasta, pagina, POR_PAGINA)
        total = sp_history_contar_auditoria(tipo_evento, fecha_desde, fecha_hasta)
        total_paginas = max(1, math.ceil(total / POR_PAGINA))

        # Clampear pagina al rango real
        if pagina > total_paginas:
            pagina = total_paginas

        filtros = {
            "tipo_evento": tipo_evento,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        }

        return render_template(
            "admin/history.html",
            registros = registros,
            tipos_evento = TIPOS_EVENTO,
            filtros = filtros,
            pagina_actual = pagina,
            total_paginas = total_paginas,
            total_registros = total,
            por_pagina = POR_PAGINA,
            active_page = "history",
        )

    # Exportar CSV con los mismos filtros activos
    def exportar_csv(self):
        tipo_evento = request.args.get("tipo_evento") or None
        fecha_desde = request.args.get("fecha_desde") or None
        fecha_hasta = request.args.get("fecha_hasta") or None

        registros = sp_history_exportar_auditoria(tipo_evento, fecha_desde, fecha_hasta)

        output = io.StringIO()
        writer = csv.writer(output)

        # Encabezados
        writer.writerow([
            "ID", "Fecha y Hora", "Tipo Evento", "Usuario",
            "Rol", "Ticket", "Detalle", "Visibilidad",
        ])

        for r in registros:
            writer.writerow([
                r["ID_Ticket_Comentario"],
                r["Fecha_Comentario"].strftime("%d/%m/%Y %H:%M") if r["Fecha_Comentario"] else "",
                r["Tipo_Evento"],
                r["Nombre_Completo_Usuario"],
                r["Nombre_Rol"],
                r["FK_ID_Ticket"],
                r["Comentario"],
                "Interno" if r["Es_Interno"] else "Público",
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=auditoria.csv"},
        )

    # Helpers
    @staticmethod
    def _parse_pagina(valor: str | None) -> int:
        try:
            p = int(valor)
            return p if p >= 1 else 1
        except (TypeError, ValueError):
            return 1