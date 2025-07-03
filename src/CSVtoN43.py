# main.py
# build v2
import os
import sys

import csv2n43_utils as utils

import ttkbootstrap as ttk
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import *
from config_gui import mostrar_configuracion
from info_gui import mostrar_informacion
from preview_gui import mostrar_previsualizacion



if "NUITKA_LAUNCH_TOKEN" in os.environ:
   messagebox.showerror("Error", "Ya existe otra instancia de esta aplicación")
   sys.exit(1)

os.environ["NUITKA_LAUNCH_TOKEN"] = "1"

from csv2n43_utils import ventanas_abiertas, ruta_icono
import csv2n43_utils

def obtener_ruta_icono():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'assets', 'csv2n43.ico')
    return os.path.join(os.path.dirname(__file__), '..', 'assets', 'csv2n43.ico')

def hay_campos_sin_asignar(config):
    for clave in config:
        if config[clave] == "Sin asignar":
            if clave not in ("referencia 1", "referencia 2"):
                return 1
            else:
                return 2
    return 0

def iniciar_aplicacion():
    def actualizar_estado_boton_tema():
        if hay_ventanas_abiertas(app) or tema_en_cooldown["estado"]:
            btn_tema.config(state="disabled")
            app.after(1000, lambda: finalizar_cooldown())
        else:
            btn_tema.config(state="normal")

    def finalizar_cooldown():
        tema_en_cooldown["estado"] = False
        actualizar_estado_boton_tema()

    def cambiar_tema(app):
        nuevo_tema = "flatly" if tema_actual["nombre"] == "darkly" else "darkly"
        
        config['tema'] = nuevo_tema
        utils.guardar_config(config)
        
        # Reiniciar la aplicación
        if "NUITKA_LAUNCH_TOKEN" in os.environ:
            del os.environ["NUITKA_LAUNCH_TOKEN"]

        app.destroy()
        python = sys.executable
        os.execl(python, python, *sys.argv)


    config, existe_config = utils.cargar_config()

    tema_actual = {"nombre": config.get("tema", "darkly")} 
    tema_en_cooldown = {"estado": False} 

    app = ttk.Window(title="CSVtoN43", themename=tema_actual["nombre"])
    app.withdraw()
    try:
        app.iconbitmap(ruta_icono)
    except Exception as e:
        if csv2n43_utils.show_ico_warn:
            messagebox.showwarning("Archivo no encontrado", "No se encontró la imagen de icono de la aplicación: csv2n43.ico")
            csv2n43_utils.show_ico_warn = False 
        
    app.deiconify()

    app.geometry("500x250")
    app.resizable(False, False)
    ventanas_abiertas["root"] = app
    # Frame superior para botones info y configuración
    top_frame = ttk.Frame(app)
    top_frame.pack(anchor="ne", pady=10, padx=10)

    btn_info = ttk.Button(top_frame, text="ℹ️", width=1, bootstyle="info-outline", command=mostrar_informacion)
    btn_info.pack(side="left", padx=5)

    # Estilo o advertencia en el botón de configuración si hay campos sin asignar
    
    btn_config = ttk.Button(top_frame, text="⚙️", width=3, bootstyle="secondary-outline", command=lambda: mostrar_configuracion(app, config))
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

        # Frame inferior para el botón de tema
    bottom_frame = ttk.Frame(app)
    bottom_frame.pack(side="bottom", fill="x", pady=5, padx=10)

    btn_tema = ttk.Button(bottom_frame,text="🌞" if config['tema'] == "darkly" else "🌙", width=3, bootstyle="secondary-outline", command=lambda:cambiar_tema(app))
    btn_tema.pack(side="left")


    # Función que comprueba si hay ventanas abiertas y actualiza el estado del botón
    def hay_ventanas_abiertas(root):
        return any(isinstance(w, tk.Toplevel) and w.winfo_exists() for w in root.winfo_children())

    def comprobar_configuracion():
        if not os.path.exists(utils.CONFIG_FILE):
            btn_config.config(text="⚙️❗", bootstyle="danger-outline", width=4)
            btn_convertir.config(state="disabled")
        else:
            # Carga la config actual para saber si hay campos sin asignar
            nueva_config, _ = utils.cargar_config()
            config.update(nueva_config)  # actualiza el dict

            if hay_campos_sin_asignar(config) == 2:
                btn_config.config(text="⚙️❗", bootstyle="warning-outline", width=4)
                if not hay_ventanas_abiertas(app):
                    btn_convertir.config(state="normal")
                else:
                  btn_convertir.config(state="disabled")

            elif hay_campos_sin_asignar(config) == 1:
                btn_config.config(text="⚙️❗", bootstyle="danger-outline", width=4)
                btn_convertir.config(state="disabled")

            else:
                btn_config.config(text="⚙️", bootstyle="secondary-outline", width=3)
                if not hay_ventanas_abiertas(app):
                    btn_convertir.config(state="normal")
                else:
                    btn_convertir.config(state="disabled")

        actualizar_estado_boton_tema()

        # Llama a sí misma cada 1000 ms (1 segundo)
        app.after(500, comprobar_configuracion)

    if not existe_config:
        comprobar_configuracion()  
        mostrar_configuracion(app, config, None)

    comprobar_configuracion()  
    app.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()
