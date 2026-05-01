import mysql.connector
from mysql.connector import Error

from app.settings import Config_DB

Config_DB.validate()

class ConnectionDB:
    def __init__(self):
        ssl_args = {}

        if Config_DB.DB_SSL:
            ssl_args = {
                "ssl_disabled": False, # Fuerza SSL
                "ssl_verify_cert": False, # True si tienes certificado propio
            }

        self.config = {
            "host": Config_DB.DB_HOST,
            "port": Config_DB.DB_PORT,
            "user": Config_DB.DB_USER,
            "password": Config_DB.DB_PASSWORD,
            "database": Config_DB.DB_NAME,
            "connection_timeout": 10, # Timeout de conexión
            **ssl_args,
            
        }
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("[INFO] Conexión a MySQL establecida.")
        except Error as e:
            print(f"[ERROR] No se pudo conectar a MySQL: {e}")
            self.connection = None

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            print("[WARN] Reconectando a MySQL...")            
            self.connect()

    def call_procedure(self, nombre_sp, params=None, commit=False):
        self.ensure_connection()
        if params is None:
            params = ()
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc(nombre_sp, params)
            resultados = []
            for result in cursor.stored_results():
                resultados.extend(result.fetchall())
            if commit:
                self.connection.commit()
            cursor.close()
            return resultados if resultados else None
        except Error as e:
            self.rollback() # Rollback automático ante error            
            print(f"[ERROR] Fallo ejecutando SP '{nombre_sp}': {e}")
            return None

    def registrar_auditoria(self, evento: str, ip_origen: str = "127.0.0.1", tabla: str = None, detalle: str = None):
        """Registra un evento en la tabla audit_log vía procedimiento almacenado"""
        self.call_procedure(
            "sp_registrar_auditoria",
            params=(evento, ip_origen, tabla, detalle),
            commit=True
        )

    def rollback(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.rollback()
        except Error as e:
            print(f"[ERROR] Fallo al hacer rollback: {e}")

    def commit(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.commit()
        except Error as e:
            print(f"[ERROR] Fallo al hacer commit: {e}")

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[INFO] Conexión a MySQL cerrada.")


db = ConnectionDB()
