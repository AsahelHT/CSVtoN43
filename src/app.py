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
    """Obtiene la ruta correcta al recurso, tanto si está empaquetado como si no"""
    if hasattr(sys, '_MEIPASS'):  # usado por PyInstaller, pero también útil con Nuitka
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

ruta_icono = ruta_recurso(os.path.join("media", "csv2n43.ico"))