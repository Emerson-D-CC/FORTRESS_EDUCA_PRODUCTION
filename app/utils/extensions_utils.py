from flask_mail import Mail
from flask import session

# Instancia global
mail = Mail()


def register_context_processors(app):
    """Registra los context processors globales de la aplicación."""

    @app.context_processor
    def inject_user_header():
        """Disponibiliza {{ user.nombre_acudiente }} y {{ user.iniciales }} en cualquier template que use el header del dashboard."""
        return {
            "user": {
                "nombre_acudiente": session.get("nombre_acudiente", ""),
                "iniciales": session.get("iniciales", ""),
                "nombre_admin": session.get("nombre_admin", ""),
                "iniciales_admin": session.get("iniciales_admin", "")
            }
        }
