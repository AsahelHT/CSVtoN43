# main.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config_gui import cargar_config, mostrar_configuracion
from info_gui import mostrar_informacion
from preview_gui import mostrar_previsualizacion

import os
import sys

def obtener_ruta_icono():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'media', 'ico.ico')
    return os.path.join(os.path.dirname(__file__), '..', 'media', 'ico.ico')

def iniciar_aplicacion():
    config, existe_config = cargar_config()
    app = ttk.Window(title="CSVtoN43", themename="darkly")
    app.geometry("500x250")
    app.iconbitmap(obtener_ruta_icono())
    app.resizable(False, False)

    # Frame superior para botones info y configuración
    top_frame = ttk.Frame(app)
    top_frame.pack(anchor="ne", pady=10, padx=10)

    btn_info = ttk.Button(top_frame, text="ℹ️", width=1, bootstyle="info-outline", command= mostrar_informacion)
    btn_info.pack(side="left", padx=5)

    btn_config = ttk.Button(top_frame, text="⚙️", width=3, bootstyle="light-outline", command=lambda: mostrar_configuracion(app, config))
    btn_config.pack(side="right")

    # Título
    ttk.Label(app, text="CSV 🔀 Norma 43", font=("Arial", 18, "bold")).pack(pady=(10, 20))

    # Botón principal grande
    btn_convertir = ttk.Button(
        app,
        text="EMPEZAR",
        width=30,
        bootstyle="primary",
        command=lambda: mostrar_previsualizacion(app, config, btn_convertir)
    )
    btn_convertir.pack(pady=10)

    if not existe_config:
        mostrar_configuracion(app, config)

    app.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()
