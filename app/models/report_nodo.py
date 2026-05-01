# Nodo genérico para almacenar un registro de log como diccionario

class ReporteNodo:
    def __init__(self, datos):
        self.datos = datos   # dict con los campos del registro
        self.siguiente = None    # puntero al siguiente nodo