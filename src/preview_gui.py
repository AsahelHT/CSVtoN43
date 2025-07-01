import tkinter as tk
from tkinter import Toplevel, filedialog, messagebox
from ttkbootstrap import LabelFrame, Treeview, Scrollbar, Button
import pandas as pd
from conversor import generar_norma43_temp 
from config_gui import cargar_config, mostrar_configuracion
from conversor import convertir_con_archivo_existente
import os
import sys



def obtener_ruta_icono():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'media', 'ico.ico')
    return os.path.join(os.path.dirname(__file__), '..', 'media', 'ico.ico')

def mostrar_previsualizacion(parent, config, boton_inicio):
    boton_inicio.config(state="disabled")
    config, existe_config = cargar_config()


    if not existe_config:
        ok = mostrar_configuracion(parent, config)
        if not ok:
            boton_inicio.config(state="normal")
            return

    

    def on_convertir():
        convertir_con_archivo_existente(config, archivo)
        preview_win.destroy()
        boton_inicio.config(state="normal")


    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo CSV",
        filetypes=[("CSV files", "*.csv")]
    )

    if not archivo:
        boton_inicio.config(state="normal")
        return

    preview_win = Toplevel()
    preview_win.title("🔍 Previsualización de la conversión")
    preview_win.geometry("1000x800")
    preview_win.iconbitmap(obtener_ruta_icono())
    preview_win.protocol("WM_DELETE_WINDOW", lambda: (preview_win.destroy(), boton_inicio.config(state="normal")))
    # Contenedor principal
    
    container = tk.Frame(preview_win)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    container.grid_rowconfigure(0, weight=1)  # Info
    container.grid_rowconfigure(1, weight=3)  # CSV
    container.grid_rowconfigure(2, weight=1)  # Campo de texto
    container.grid_rowconfigure(3, weight=3)  # Norma43
    container.grid_rowconfigure(4, weight=3)  # Guardar
    container.grid_columnconfigure(0, weight=1)

    # --- Boton info ---
    
    #btn_leyenda = Button(
    #    container,
    #    text="📘 Ver leyenda",
    #    bootstyle="info-outline",
    #    command=lambda: mostrar_leyenda_popup(preview_win)
    #)
    #btn_leyenda.grid(row=0, column=0, columnspan=2, pady=(5, 10))


    # --- Previsualización CSV ---
    frame_csv = LabelFrame(container, text="📄 Previsualización CSV Original (7 primeras líneas)", bootstyle="primary")
    frame_csv.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    _mostrar_tabla_csv(frame_csv, archivo)

    # --- Indicador de conversión con emoji ---
    arrow_frame = tk.Frame(container)
    arrow_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
    arrow_frame.grid_rowconfigure(0, weight=1)
    arrow_frame.grid_columnconfigure(0, weight=1)

    emoji_label = tk.Label(
        arrow_frame,
        text="🔀",
        font=("Arial", 64),  # Tamaño grande
        anchor="center"
    )
    emoji_label.grid(row=0, column=0, sticky="nsew")        
    # --- Previsualización Norma43 ---
    frame_n43 = LabelFrame(container, text="📃 Previsualización Norma 43 (5 primeras y 2 últimas líneas)", bootstyle="light")
    frame_n43.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
    _mostrar_tabla_norma43(frame_n43, archivo, config)

    # --- Boton de guardar ---
    arrow_frame = tk.Frame(container)
    arrow_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)
    arrow_frame.grid_rowconfigure(0, weight=1)
    arrow_frame.grid_columnconfigure(0, weight=1)

    boton_guardar = Button(
        arrow_frame,
        text="CONVERTIR",
        bootstyle="success",
        width=5,
        style="TButton",
        command=lambda: on_convertir()
    )
    boton_guardar.grid(row=0, column=0, sticky="nsew")

def _mostrar_tabla_csv(frame, archivo):
    tree = Treeview(frame, show="headings")
    tree.pack(fill="both", expand=True, side="left")

    scrollbar = Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    try:
        df = pd.read_csv(archivo, sep=";", nrows=7)
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
    except Exception as e:
        messagebox.showerror("Error CSV", str(e))

def _mostrar_tabla_norma43(frame, archivo_csv, config):
    tree = Treeview(frame)
    tree.pack(fill="both", expand=True, side="left")

    scrollbar = Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    try:
        lineas = generar_norma43_temp(archivo_csv, config)  # Debes retornar una lista de líneas
        if not lineas:
            raise ValueError("No se generó contenido.")

        muestra = lineas[:5] + ["..."] + lineas[-2:]

        tree["columns"] = ["contenido"]
        tree.column("contenido", anchor="w", width=800)

        for linea in muestra:
            tree.insert("", "end", values=[linea.strip()])

    except Exception as e:
        messagebox.showerror("Error Norma 43", str(e))

import tkinter as tk
from ttkbootstrap import LabelFrame, Label

def mostrar_leyenda_popup(parent=None):
    leyenda_win = tk.Toplevel(parent)
    leyenda_win.title("📘 Leyenda de correspondencia CSV → Norma43")
    leyenda_win.geometry("600x400")
    leyenda_win.resizable(True, True)

    # Opcional: icono
    try:
        from preview_gui import obtener_ruta_icono
        leyenda_win.iconbitmap(obtener_ruta_icono())
    except:
        pass

    frame = LabelFrame(leyenda_win, text="Relación de campos", bootstyle="info")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    campos = [
        ("fecha", "Campo de fecha de operación del CSV → Línea 22 (posición 6-11)"),
        ("valor", "Campo de fecha valor del CSV → Línea 22 (posición 12-17)"),
        ("concepto", "Concepto del movimiento → Línea 22 (posición 40-99)"),
        ("importe", "Importe del movimiento → Línea 22 (posición 33-44)"),
        ("saldo", "Saldo inicial/final → Línea 11 y Línea 33"),
        ("referencia 1", "Referencia extendida → Línea 2301"),
        ("referencia 2", "Segunda referencia → Línea 2302"),
        ("cuenta", "Número de cuenta del cliente → Línea 11 y Línea 33"),
    ]

    for campo, descripcion in campos:
        Label(frame, text=f"{campo.title()}:", bootstyle="secondary", anchor="w").pack(fill="x", padx=5, pady=(8, 0))
        Label(frame, text=descripcion, anchor="w", wraplength=550, justify="left").pack(fill="x", padx=10)


