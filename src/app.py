# app.py
import sys
import os

ventanas_abiertas = {
    "config": None,
    "info": None,
    "preview": None,
    "root":None
}

def ruta_recurso(rel_path):
    """Devuelve la ruta absoluta a un recurso."""
    if hasattr(sys, '_MEIPASS'):  # PyInstaller/Nuitka modo empaquetado
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):  # PyInstaller onefile
        base_path = os.path.dirname(sys.executable)
    else:  # Ejecución normal: usar ruta del script
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.abspath(os.path.join(base_path, ".."))  # Subir un nivel si estás en /src
    return os.path.join(base_path, rel_path)

ruta_icono = ruta_recurso(os.path.join("assets", "csv2n43.ico"))
