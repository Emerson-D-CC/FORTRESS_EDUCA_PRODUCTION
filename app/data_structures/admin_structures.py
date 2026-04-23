from typing import Any, List, Dict

class Nodo:
    def __init__(self, data: Dict[str, Any]):
        self.data = data  # Diccionario con datos del usuario (e.g., {'id': 1, 'nombre': 'Juan'})
        self.siguiente = None

class Cola:
    def __init__(self):
        self.primero = None
        self.ultimo = None

    def encolar(self, data: Dict[str, Any]):
        nuevo = Nodo(data)
        if self.primero is None:
            self.primero = nuevo
            self.ultimo = nuevo
        else:
            self.ultimo.siguiente = nuevo
            self.ultimo = nuevo

    def desencolar(self) -> Dict[str, Any] | None:
        if self.primero is None:
            return None
        data = self.primero.data
        self.primero = self.primero.siguiente
        return data

    def ver_primero(self) -> Dict[str, Any] | None:
        return self.primero.data if self.primero else None

    def ver_todos(self) -> List[Dict[str, Any]]:
        items = []
        aux = self.primero
        while aux:
            items.append(aux.data)
            aux = aux.siguiente
        return items

    def esta_vacia(self) -> bool:
        return self.primero is None