# main.py
# build v2
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from config_gui import cargar_config, mostrar_configuracion, CONFIG_FILE
from info_gui import mostrar_informacion
from preview_gui import mostrar_previsualizacion

import os
import sys

from app import ventanas_abiertas

def obtener_ruta_icono():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'media', 'csv2n43.ico')
    return os.path.join(os.path.dirname(__file__), '..', 'media', 'csv2n43.ico')

def hay_campos_sin_asignar(config):
    for clave in config:
        if clave.startswith("campo_") and clave not in ("referencia1", "referencia2"):
            if config[clave] == "Sin asignar":
                return True
    return False

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

    # Estilo o advertencia en el botón de configuración si hay campos sin asignar
    
    btn_config = ttk.Button(top_frame, text="⚙️", width=3, bootstyle="light-outline", command=lambda: mostrar_configuracion(app, config))
    btn_config.pack(side="right")

    # Título
    ttk.Label(app, text="CSV 🔀 Norma 43", font=("Arial", 18, "bold")).pack(pady=(10, 20))

    btn_convertir = ttk.Button(
        app,
        text="EMPEZAR",
        width=30,
        bootstyle="primary",
        command=lambda: mostrar_previsualizacion(app, config)
    )
    btn_convertir.pack(pady=10)


    # Función que comprueba si hay ventanas abiertas y actualiza el estado del botón
    def hay_ventanas_abiertas(root):
        return any(isinstance(w, tk.Toplevel) and w.winfo_exists() for w in root.winfo_children())

    def comprobar_configuracion():
        if not os.path.exists(CONFIG_FILE):
            btn_config.config(text="⚙️❗", bootstyle="danger-outline", width=4)
            btn_convertir.config(state="disabled")
        else:
            # Carga la config actual para saber si hay campos sin asignar
            nueva_config, _ = cargar_config()
            config.update(nueva_config)  # actualiza el dict

            if hay_campos_sin_asignar(config):
                btn_config.config(text="⚙️❗", bootstyle="warning-outline", width=4)
            else:
                btn_config.config(text="⚙️", bootstyle="light-outline", width=3)

            if not hay_ventanas_abiertas(app):
                btn_convertir.config(state="normal")

        # Llama a sí misma cada 1000 ms (1 segundo)
        app.after(1000, comprobar_configuracion)

    if not existe_config:
        comprobar_configuracion()  
        mostrar_configuracion(app, config)

    comprobar_configuracion()  
    app.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()
