from app.models.report_nodo import ReporteNodo

class ReporteFila:
    """Estructura de datos: Cola (Queue) de registros de log"""

    def __init__(self):
        self.primero = None
        self.ultimo = None
        self._tamanio = 0

    #  Encolar (enqueue) 
    def encolar(self, datos):
        """Agrega un registro al final de la cola"""
        nuevo = ReporteNodo(datos)
        if self.primero is None:
            self.primero = nuevo
            self.ultimo = nuevo
        else:
            self.ultimo.siguiente = nuevo
            self.ultimo = nuevo
        self._tamanio += 1

    #  Desencolar (dequeue)
    def desencolar(self):
        """Elimina y retorna el primer registro de la cola"""
        if self.primero is None:
            return None
        dato = self.primero.datos
        self.primero = self.primero.siguiente
        if self.primero is None:
            self.ultimo = None
        self._tamanio -= 1
        return dato

    #  Utilidades 
    def esta_vacia(self):
        return self.primero is None

    def tamanio(self):
        return self._tamanio

    #  Aux: Cola ↔ Lista de nodos 
    def _a_lista_nodos(self):
        nodos, aux = [], self.primero
        while aux is not None:
            nodos.append(aux)
            aux = aux.siguiente
        return nodos

    def _desde_lista_nodos(self, nodos):
        self.primero = self.ultimo = None
        for nodo in nodos:
            nodo.siguiente = None
            if self.primero is None:
                self.primero = self.ultimo = nodo
            else:
                self.ultimo.siguiente = nodo
                self.ultimo = nodo

    #  Insertion Sort 
    def insertion_sort(self, campo, ascendente):
        """Ordena la cola usando Insertion Sort por el campo indicado"""
        nodos = self._a_lista_nodos()

        for i in range(1, len(nodos)):
            clave     = nodos[i]
            val_clave = clave.datos.get(campo)
            j         = i - 1

            while j >= 0:
                val_j = nodos[j].datos.get(campo)

                # None siempre va al inicio
                if val_j is None:
                    break
                if val_clave is None:
                    j -= 1
                    continue

                mover = (val_j > val_clave) if ascendente else (val_j < val_clave)
                if mover:
                    nodos[j + 1] = nodos[j]
                    j -= 1
                else:
                    break

            nodos[j + 1] = clave

        self._desde_lista_nodos(nodos)

    #  Leer datos sin vaciar la cola 
    def a_lista_datos(self):
        """Retorna todos los datos como lista de dicts (no vacía la cola)"""
        resultado, aux = [], self.primero
        while aux is not None:
            resultado.append(aux.datos)
            aux = aux.siguiente
        return resultado