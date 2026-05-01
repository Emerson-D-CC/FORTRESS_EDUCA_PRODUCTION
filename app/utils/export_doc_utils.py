import csv
import io
from datetime import datetime

# FUNCIONES DE FLASK
from flask import Response
from app.models.report_row import ReporteFila

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class ExportarReporte:
    """Clase para exportar cualquier listado a CSV o PDF"""

    # ------------------------------------------------------------------
    # Cargar datos en la Cola
    # ------------------------------------------------------------------
    @staticmethod
    def cargar_fila(registros: list, mapeador) -> ReporteFila:
        """Encola cada registro aplicando la función mapeador"""
        fila = ReporteFila()
        for r in registros:
            fila.encolar(mapeador(r))
        return fila

    # ------------------------------------------------------------------
    # Exportar CSV
    # ------------------------------------------------------------------
    @staticmethod
    def csv(datos: list, columnas: list, nombre_archivo: str):
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=columnas,
            extrasaction="ignore",
            delimiter=";",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(datos)

        contenido = "\ufeff" + output.getvalue()  # BOM UTF-8 para Excel

        return Response(
            contenido,
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={nombre_archivo}.csv",
                "Content-Type": "text/csv; charset=utf-8-sig",
            },
        )

    # ------------------------------------------------------------------
    # Exportar PDF
    # ------------------------------------------------------------------
    @staticmethod
    def pdf(datos: list, columnas: list, titulo: str, nombre_archivo: str,):

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1.5 * cm, leftMargin=1.5 * cm,
            topMargin=2 * cm, bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        
        st_celda = ParagraphStyle(
            "Celda", 
            parent=styles["Normal"], 
            fontSize=7, 
            leading=8, # Espaciado entre líneas
            alignment=TA_CENTER
        ) 
        st_titulo = ParagraphStyle(
            "Titulo", parent=styles["Heading1"],
            fontSize=15, alignment=TA_CENTER, spaceAfter=4,
        )
        st_subtitulo = ParagraphStyle(
            "SubTitulo", parent=styles["Normal"],
            fontSize=8, alignment=TA_CENTER,
            textColor=colors.HexColor("#6c757d"), spaceAfter=10,
        )

        # Tabla
        tabla_data = [columnas]
        for fila in datos:
            fila_procesada = []
            for col in columnas:
                texto = str(fila.get(col, "—"))     
                fila_procesada.append(Paragraph(texto, st_celda))
            tabla_data.append(fila_procesada)

        ancho_col = (landscape(A4)[0] - 3 * cm) / len(columnas)
        tabla = Table(tabla_data, colWidths=[ancho_col] * len(columnas), repeatRows=1)

        estilo = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#212529")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTNAME", (0, 1), (-1, -1),"Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dee2e6")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]
        for i in range(1, len(tabla_data)):
            bg = colors.HexColor("#f8f9fa") if i % 2 == 0 else colors.white
            estilo.append(("BACKGROUND", (0, i), (-1, i), bg))

        tabla.setStyle(TableStyle(estilo))

        doc.build([
            Paragraph(f"Fortress Educa — {titulo}", st_titulo),
            Paragraph(
                f"Generado el {datetime.now().strftime('%d/%m/%Y %I:%M %p')}"
                f" &nbsp;·&nbsp; Total: {len(datos)} registros",
                st_subtitulo,
            ),
            Spacer(1, 0.3 * cm),
            tabla,
        ])

        buffer.seek(0)
        return Response(
            buffer.getvalue(),
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}.pdf"},
        )


