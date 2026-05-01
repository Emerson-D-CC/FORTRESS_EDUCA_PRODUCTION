import re

class regex:
    """Clase para validaciones con expresiones regulares"""
    
    # VALIDACIONES DE NOMBRES/APELLIDOS
    @staticmethod
    def formato_nombre_apellido(valor: str) -> bool:
        return bool(re.fullmatch(r"[A-Za-záéíóúÁÉÍÓÚÜüÑñ']{2,50}$", valor.strip()))


    # CORREOS ELECTRÓNICOS
    @staticmethod
    def formato_email(valor: str) -> bool:
        return bool(re.fullmatch(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z]{2,6}){1,2}$", valor.strip()))


    # NÚMEROS TELEFÓNICOS
    @staticmethod
    def formato_telefono_sin_prefijo_celular(valor: str) -> bool:
        return bool(re.fullmatch(r"3\d{9}$", valor.strip()))


    # DOCUMENTO DE IDENTIDAD
    @staticmethod
    def formato_numero_identificacion(valor: str) -> bool:
        return bool(re.fullmatch(r"\d{5,10}$", valor.strip()))


    # DIRECCIONES
    @staticmethod
    def formato_direccion(valor: str) -> bool:
        # Función que valida las direcciones de Bogotá D.C. con varios regex
        return bool(re.fullmatch(
            r"^(?:(Cl|Cll|Calle|Cra|Kr|Kra|Carrera|Av|Avenida|Tv|Transv|Transversal|Dg|Diag|Diagonal))\.?\s*" \
            r"\d{1,3}[A-Za-z]?(?:\s*Bis)?(?:\s*(Norte|Sur|Este|Oeste|N|S|E|O))?" \
            r"\s*#\s*\d{1,3}[A-Za-z]?(?:\s*[A-Za-z0-9]+)?(?:\s*-\s*\d{1,3}[A-Za-z0-9]*)?" \
            r"(?:\s*(?:Mz|Manzana)\s*[A-Za-z0-9]+\s*(?:Casa|Cs|Apartamento|Apto|Bloque|Blq)\s*\d{1,3}[A-Za-z]?)?$", valor.strip(), re.IGNORECASE))


    # CONTRASEÑA
    @staticmethod
    def formato_contraseña(contraseña: str) -> list:
        errores = []

        if not re.search(r"[A-Z]", contraseña):
            errores.append("\nDebe contener mínimo una letra mayúscula.")
        if not re.search(r"[a-z]", contraseña):
            errores.append("\nDebe contener mínimo una letra minúscula.")
        if not re.search(r"\d", contraseña):
            errores.append("\nDebe contener mínimo un número.")
        if not re.search(r"[^\w\s]", contraseña):
            errores.append("\nDebe contener mínimo un carácter especial.")
        if re.search(r"\s", contraseña):
            errores.append("\nNo debe contener espacios en blanco.")
        return errores
    
    
    @staticmethod
    def formato_contraseña_all(contraseña: str) -> bool:
        return bool(re.fullmatch(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^\w\s])[^\s]{10,}$", contraseña.strip()))


    # CODIGO MFA
    @staticmethod
    def codigo_mfa(valor: str) -> bool:
        return bool(re.fullmatch(r"^\d{6}$", valor.strip()))