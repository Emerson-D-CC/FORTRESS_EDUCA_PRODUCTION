from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.settings import Config_Security

# Parámetros de configuración para el proceso de hashing
ph = PasswordHasher(
    time_cost=3,# Número de iteraciones
    memory_cost=65536, # 64 MB de RAM por hash
    parallelism=4, # Hilos paralelos
    hash_len=32, # Longitud del hash en bytes
    salt_len=16 # Salt generado automáticamente por Argon2
)


def _aplicar_pepper(password: str) -> str:
    """Combina la contraseña con el pepper antes de hashear"""
    pepper = Config_Security.PEPPER
    if isinstance(pepper, bytes):
        pepper = pepper.decode("utf-8")
    return password + pepper


def hashear_contraseña(password: str) -> str:
    """Genera el hash Argon2id de una contraseña"""
    # El salt se genera y embebe automáticamente en el hash resultante.
    return ph.hash(_aplicar_pepper(password))


def verificar_contraseña(password: str, hash_almacenado: str) -> bool:
    """Verifica una contraseña contra su hash almacenado"""
    try:
        return ph.verify(hash_almacenado, _aplicar_pepper(password))
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def hash_necesita_rehash(hash_almacenado: str) -> bool:
    """Detecta si un hash fue generado con parámetros anteriores"""
    return ph.check_needs_rehash(hash_almacenado)