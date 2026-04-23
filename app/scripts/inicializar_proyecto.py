import os

def crear_estructura():
    # Definimos la estructura basada en nuestro acuerdo
    directorios = [
        'database/pruebas',
        'app/blueprints/pagina',
        'app/blueprints/auth',
        'app/blueprints/aplicacion',
        'app/blueprints/admin',
        'app/controllers',
        'app/models',
        'app/services',
        'app/repositories',
        'app/data_structures',
        'app/utils',
        'app/static/css',
        'app/static/js',
        'app/static/img',
        'app/templates/includes',
        'app/templates/pagina',
        'app/templates/auth',
        'app/templates/aplicacion/tickets',
        'app/templates/aplicacion/usuarios',
        'app/templates/aplicacion/reportes',
        'docs'
    ]

    # Archivos iniciales vacíos para que Flask reconozca los paquetes
    archivos = [
        'run.py',
        'requirements.txt',
        'app/__init__.py',
        'app/config.py',
        'app/blueprints/pagina/__init__.py',
        'app/blueprints/auth/__init__.py',
        'app/blueprints/aplicacion/__init__.py',
        'app/blueprints/admin/__init__.py',
        'app/utils/db.py'
    ]

    print("--- Iniciando creación de estructura APT ---")

    for carpeta in directorios:
        os.makedirs(carpeta, exist_ok=True)
        # Crear un __init__.py en cada carpeta de lógica para que sea un módulo
        if 'app/' in carpeta and 'static' not in carpeta and 'templates' not in carpeta:
            with open(os.path.join(carpeta, '__init__.py'), 'a'):
                pass
        print(f"Directorio creado: {carpeta}")

    for archivo in archivos:
        if not os.path.exists(archivo):
            with open(archivo, 'w') as f:
                pass
            print(f"Archivo creado: {archivo}")

    print("--- ¡Estructura lista para la batalla, colega! ---")

if __name__ == "__main__":
    crear_estructura()