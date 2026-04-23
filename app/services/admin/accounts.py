from flask import request, render_template
from app.repositories.admin_repository import (
    sp_admin_historial_acceso_listar, 
    sp_admin_historial_acciones_listar, 
    sp_admin_metricas_accounts, 
    sp_admin_roles_consultar,
    sp_admin_eventos_acceso_consultar,
    sp_admin_eventos_auditoria_consultar,
    sp_admin_navegadores_consultar
)

class Accounts_Service:
    """Lógica de negocio para accounts.html (historial de acceso y auditoría)."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Vista principal
    # ------------------------------------------------------------------
    def listar_historial(self):
        tab = request.args.get("tab", "acceso")  # 'acceso' | 'acciones'
        
        # --- Datos de Metricas ---
        datos_metricas = sp_admin_metricas_accounts()
        
        # --- Datos de Dropdowns ---
        datos_roles = sp_admin_roles_consultar()
        datos_eventos_acceso = sp_admin_eventos_acceso_consultar()
        datos_eventos_auditoria = sp_admin_eventos_auditoria_consultar()
        datos_navegadores = sp_admin_navegadores_consultar()
        
        # --- Filtros tab Historial de Acceso ---
        filtros_acceso = {
            "rol": self._int_or_none(request.args.get("rol")),
            "evento": self._str_or_none(request.args.get("evento")),
            "navegador": self._str_or_none(request.args.get("navegador")),
        }

        # --- Filtros tab Historial de Acciones ---
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
        