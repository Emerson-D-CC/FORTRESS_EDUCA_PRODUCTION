# FUNCIONES DE FLASK
import datetime

from flask import request, render_template
from app.repositories.admin_repository import (
    sp_admin_historial_acceso_listar, 
    sp_admin_historial_acciones_listar, 
    sp_admin_metricas_accounts, 
    sp_admin_roles_consultar,
    sp_admin_eventos_acceso_consultar,
    sp_admin_eventos_auditoria_consultar,
    sp_admin_navegadores_consultar,
)

# Logica de reportes
from app.utils.export_doc_utils import ExportarReporte


class Accounts_Service:
    """Lógica de negocio para accounts.html (historial de acceso y auditoría)"""

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------
    @staticmethod
    def _int_or_none(value: str):
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _str_or_none(value: str):
        v = (value or "").strip()
        return v if v else None

    # ---------------------------------------------------------------
    # Vista principal
    # ---------------------------------------------------------------
    def listar_historial(self):
        tab = request.args.get("tab", "acceso")  # 'acceso' | 'acciones'
        
        # Datos de Metricas 
        datos_metricas = sp_admin_metricas_accounts()
        
        # Datos de Dropdowns 
        datos_roles = sp_admin_roles_consultar()
        datos_eventos_acceso = sp_admin_eventos_acceso_consultar()
        datos_eventos_auditoria = sp_admin_eventos_auditoria_consultar()
        datos_navegadores = sp_admin_navegadores_consultar()
        
        # Filtros tab Historial de Acceso 
        filtros_acceso = {
            "rol": self._int_or_none(request.args.get("rol")),
            "evento": self._str_or_none(request.args.get("evento")),
            "navegador": self._str_or_none(request.args.get("navegador")),
        }

        # Filtros tab Historial de Acciones 
        filtros_acciones = {
            "rol":self._int_or_none(request.args.get("rol_ac")),
            "evento": self._str_or_none(request.args.get("evento_ac")),
        }

        historial_acceso = sp_admin_historial_acceso_listar(
            filtros_acceso["rol"],
            filtros_acceso["evento"],
            filtros_acceso["navegador"],
        )
        historial_acciones = sp_admin_historial_acciones_listar(
            filtros_acciones["rol"],
            filtros_acciones["evento"],
        )
        
        return render_template(
            "admin/accounts.html",
            active_page="accounts",
            # datos
            historial_acceso=historial_acceso,
            historial_acciones=historial_acciones,
            metricas=datos_metricas,
            # dropdowns
            roles=datos_roles,
            eventos_acceso=datos_eventos_acceso,
            eventos_auditoria=datos_eventos_auditoria,
            navegadores=datos_navegadores,
            # estado filtros
            filtros_acceso=filtros_acceso,
            filtros_acciones=filtros_acciones,
            tab_activo=tab,
        )


    # ---------------------------------------------------------------
    # Exportar Historial de Acceso
    # ---------------------------------------------------------------
    
    def exportar_historial_acceso(self):
        formato = request.args.get("formato", "csv").lower()
        filtros = {
            "rol": self._int_or_none(request.args.get("rol")),
            "evento": self._str_or_none(request.args.get("evento")),
            "navegador": self._str_or_none(request.args.get("navegador")),
        }

        registros = sp_admin_historial_acceso_listar(
            filtros["rol"], filtros["evento"], filtros["navegador"]
        )

        # Mapeador específico de este módulo
        def mapeador(r):
            fecha = r["Fecha_Evento"]
            return {
                "ID": r["ID_Auditoria"],
                "Usuario": r["Nombre_Usuario"],
                "Rol": r["Nombre_Rol"],
                "Evento": r["Evento"],
                "IP": r["IP"],
                "Navegador": r["Navegador"],
                "Fecha": fecha.strftime("%d/%m/%Y %I:%M %p") if fecha else "—",
            }

        fila = ExportarReporte.cargar_fila(registros, mapeador)
        fila.insertion_sort("ID", ascendente=True)
        datos = fila.a_lista_datos()

        COLUMNAS = ["ID", "Usuario", "Rol", "Evento", "IP", "Navegador", "Fecha"]
        
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS, "Historial de Acceso", f"historial_acceso_usuarios_{fecha_actual}")
        return ExportarReporte.csv(datos, COLUMNAS, f"historial_acceso_usuarios_{fecha_actual}")

    # ---------------------------------------------------------------
    # Exportar Historial de Acciones
    # ---------------------------------------------------------------

    def exportar_historial_acciones(self):
        formato = request.args.get("formato", "csv").lower()
        filtros = {
            "rol": self._int_or_none(request.args.get("rol_ac")),
            "evento": self._str_or_none(request.args.get("evento_ac")),
        }

        registros = sp_admin_historial_acciones_listar(
            filtros["rol"], filtros["evento"]
        )

        def mapeador(r):
            fecha = r["Fecha_Evento"]
            return {
                "ID": r["ID_Auditoria"],
                "Evento": r["Evento"],
                "Ejecutor": r["ID_Formateado"],
                "IP": r["IP"],
                "Dato Antiguo": r["Dato_Antiguo"] or "—",
                "Dato Nuevo": r["Dato_Nuevo"]   or "—",
                "Fecha": fecha.strftime("%d/%m/%Y %I:%M %p") if fecha else "—",
            }

        fila = ExportarReporte.cargar_fila(registros, mapeador)
        fila.insertion_sort("ID", ascendente=True)
        datos = fila.a_lista_datos()

        COLUMNAS = ["ID", "Evento", "Ejecutor", "IP", "Dato Antiguo", "Dato Nuevo", "Fecha"]
        
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if formato == "pdf":
            return ExportarReporte.pdf(datos, COLUMNAS, "Historial de Acciones", f"historial_acciones_usuarios_{fecha_actual}")
        return ExportarReporte.csv(datos, COLUMNAS, f"historial_acciones_usuarios_{fecha_actual}")    