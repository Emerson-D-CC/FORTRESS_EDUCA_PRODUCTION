from mysql.connector import Error, pooling
from contextlib import contextmanager

from app.settings import Config_DB

Config_DB.validate()


class ConnectionDB:
    def __init__(self):
        ssl_args = {}
        if Config_DB.DB_SSL:
            ssl_args = {
                "ssl_disabled": False,
                "ssl_verify_cert": False,
            }

        pool_config = {
            "host": Config_DB.DB_HOST,
            "port": Config_DB.DB_PORT,
            "user": Config_DB.DB_USER,
            "password": Config_DB.DB_PASSWORD,
            "database": Config_DB.DB_NAME,
            "connection_timeout": 10,
            **ssl_args,
        }

        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name = "fortress_pool",
                pool_size = 30, # ajusta según tu carga esperada
                pool_reset_session = True, # limpia variables de sesión al devolver
                **pool_config,
            )
            print("[INFO] Pool de conexiones MySQL inicializado.")
        except Error as e:
            print(f"[ERROR] No se pudo inicializar el pool: {e}")
            self._pool = None

    # ------------------------------------------------------------------
    # INTERNAL: obtiene una conexión del pool
    # ------------------------------------------------------------------
    def _get_connection(self):
        if self._pool is None:
            raise Error("Pool de conexiones no disponible.")
        return self._pool.get_connection()

    # ------------------------------------------------------------------
    # CONTEXT MANAGER: transacciones explícitas multi-paso
    # Uso:
    #   with db.transaction() as conn:
    #       db.call_procedure("sp_x", conn=conn)
    #       db.call_procedure("sp_y", conn=conn)
    #       db.commit(conn)          # commit manual si no se usa auto-commit
    # ------------------------------------------------------------------
    @contextmanager
    def transaction(self):
        """Provee una conexión dedicada para transacciones que involucran múltiples procedimientos"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
            print("[INFO] Transacción confirmada (commit).")
        except Exception as e:
            conn.rollback()
            print(f"[WARN] Transacción revertida (rollback): {e}")
            raise
        finally:
            conn.close()  # devuelve la conexión al pool

    # ------------------------------------------------------------------
    # OPERACIÓN SIMPLE: obtiene, usa y libera la conexión en una sola llamada
    # ------------------------------------------------------------------
    def call_procedure(self, nombre_sp, params=None, commit=False, conn=None):
        """Ejecuta un stored procedure"""
        if params is None:
            params = ()

        external_conn = conn is not None
        if not external_conn:
            conn = self._get_connection()

        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.callproc(nombre_sp, params)

            resultados = []
            for result in cursor.stored_results():
                resultados.extend(result.fetchall())

            cursor.close()

            if commit and not external_conn:
                conn.commit()

            return resultados if resultados else None

        except Error as e:
            if not external_conn:
                # rollback solo si manejamos la conexión aquí
                self.rollback(conn)
            print(f"[ERROR] Fallo ejecutando SP '{nombre_sp}': {e}")
            return None

        finally:
            if not external_conn:
                conn.close()  # siempre devuelve al pool

    # ------------------------------------------------------------------
    # AUDITORÍA
    # ------------------------------------------------------------------
    def registrar_auditoria(self, evento: str, ip_origen: str = "127.0.0.1", tabla: str = None, detalle: str = None):
        self.call_procedure(
            "sp_registrar_auditoria",
            params=(evento, ip_origen, tabla, detalle),
            commit=True,
        )

    # ------------------------------------------------------------------
    # COMMIT / ROLLBACK — conservados tal como los tenías
    # ------------------------------------------------------------------
    def commit(self, conn=None):
        """Confirma la transacción. Recibe la conexión obtenida desde `transaction()`"""
        try:
            if conn and conn.is_connected():
                conn.commit()
                print("[INFO] Commit ejecutado.")
        except Error as e:
            print(f"[ERROR] Fallo al hacer commit: {e}")

    def rollback(self, conn=None):
        """Revierte la transacción. Recibe la conexión obtenida desde `transaction()`"""
        try:
            if conn and conn.is_connected():
                conn.rollback()
                print("[WARN] Rollback ejecutado.")
        except Error as e:
            print(f"[ERROR] Fallo al hacer rollback: {e}")


    # ------------------------------------------------------------------
    # CIERRE (el pool gestiona el ciclo de vida de las conexiones)
    # ------------------------------------------------------------------
    def close(self):
        print("[INFO] El pool gestiona el ciclo de vida automáticamente.")

db = ConnectionDB()