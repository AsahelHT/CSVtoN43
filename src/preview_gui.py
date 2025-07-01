from tkinter import ttk
from tkinter import Toplevel, filedialog, messagebox, LEFT, BOTH, Frame
from ttkbootstrap import LabelFrame, Treeview, Scrollbar, Button, Style
import pandas as pd
from conversor import generar_norma43_temp 
from config_gui import cargar_config, mostrar_configuracion
from conversor import convertir_con_archivo_existente
from ttkbootstrap.widgets import Treeview
import os
import sys

from app import ventanas_abiertas

# Colores por campo
colores = {
    'campo_fecha': '#ff6b6b',     # rojo claro
    'campo_valor': '#61dafb',     # azul claro
    'campo_concepto': '#a3e635',  # verde lima
    'campo_importe': '#facc15',   # amarillo dorado
    'campo_saldo': '#d4d4d8',     # gris claro
    'campo_ref1': '#c084fc',      # púrpura claro
    'campo_ref2': '#f472b6'       # rosa pastel
}

def generar_mapa_columnas_desde_csv(columnas_csv, colores):
    mapa_columnas = {}
    for col in columnas_csv:
        col_normalizada = col.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
        for clave_color in colores.keys():
            if clave_color.startswith("campo_"):
                campo = clave_color.replace("campo_", "")
                if campo in col_normalizada:
                    mapa_columnas[col] = clave_color
                    break
        else:
            mapa_columnas[col] = None  # No se encontró mapeo
    return mapa_columnas

def obtener_ruta_icono():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'media', 'csv2n43.ico')
    return os.path.join(os.path.dirname(__file__), '..', 'media', 'csv2n43.ico')

def mostrar_previsualizacion(parent, config):

    try:
        # Evitar duplicados
        if ventanas_abiertas.get("preview") and ventanas_abiertas["preview"].winfo_exists():
            ventanas_abiertas["preview"].focus()
            return
        
        #boton_inicio.config(state="disabled")
        config, existe_config = cargar_config()

        if not existe_config:
            ok = mostrar_configuracion(parent, config)
            if not ok:
                return

        def on_convertir():
            convertir_con_archivo_existente(config, archivo)
            preview_win.destroy()


        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv")]
        )

        if not archivo:
            return

        # Verifica si el contenedor principal sigue existiendo
        if not parent.winfo_exists():
            return
        
        preview_win = Toplevel()
        if not preview_win.winfo_exists():
            return
        preview_win.title("🔍 Previsualización de la conversión")
        preview_win.geometry("1000x900")
        preview_win.minsize(1000, 900)
        preview_win.iconbitmap(obtener_ruta_icono())
        preview_win.protocol("WM_DELETE_WINDOW", lambda: (preview_win.destroy()))
        # Contenedor principal

        
        ventanas_abiertas["preview"] = preview_win
        
        container = ttk.Frame(preview_win)
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
        arrow_frame = ttk.Frame(container)
        arrow_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        arrow_frame.grid_rowconfigure(0, weight=1)
        arrow_frame.grid_columnconfigure(0, weight=1)

        emoji_label = ttk.Label(
            arrow_frame,
            text="🔀",
            font=("Arial", 64),  # Tamaño grande
            anchor="center"
        )
        emoji_label.grid(row=0, column=0, sticky="nsew")        
        # --- Previsualización Norma43 ---
        frame_n43 = LabelFrame(container, text="📃 Previsualización Norma 43 (5 primeras y 2 últimas líneas)", bootstyle="light")
        frame_n43.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        
        _mostrar_tabla_norma43(frame_n43, archivo, config,  parent=preview_win)
        
        # --- Boton de guardar ---
        arrow_frame = ttk.Frame(container)
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
    except ttk.TclError:
        return
    


def _mostrar_tabla_csv(frame, archivo):
    try:
        df = pd.read_csv(archivo, sep=";", nrows=7)
    except Exception as e:
        messagebox.showerror("Error CSV", str(e))
        return

    columnas = list(df.columns)
    mapa_columnas = generar_mapa_columnas_desde_csv(columnas, colores)

    for i, col in enumerate(columnas):
        subframe = Frame(frame)
        subframe.pack(side=LEFT, fill=BOTH, expand=True)

        clave_logica = mapa_columnas.get(col)
        color = colores.get(clave_logica, "#e0e0e0")

        style = Style()
        style_name = f"Custom{i}.Treeview"
        style.configure(f"{style_name}.Heading",
                        background=color,
                        foreground="black",
                        font=("Segoe UI", 10, "bold"))
        style.configure(style_name, rowheight=25)

        tree = Treeview(subframe, columns=(col,), show="headings", style=style_name)
        tree.pack(side=LEFT, fill=BOTH, expand=True)

        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

        for valor in df[col]:
            tree.insert("", "end", values=(valor,))

from tkinter import Text, Scrollbar, messagebox
from tkinter import RIGHT, LEFT, Y, BOTH
from datetime import datetime
from decimal import Decimal

def _mostrar_tabla_norma43(frame, archivo_csv, config, parent=None):
    text = Text(
        frame,
        wrap="none",
        font=("Courier", 10),
        bg="#2c2f33",
        fg="white",
        insertbackground="white",
        height=8  # Número de líneas visibles
    )
    text.pack(fill=BOTH, expand=True, side=LEFT)
    
   
    # Colores legibles en tema oscuro

    for campo, color in colores.items():
        text.tag_config(campo, foreground=color)

    try:
        lineas = generar_norma43_temp(archivo_csv, config)
        if not lineas:
            raise ValueError("No se generó contenido.")

        muestra = lineas[:5] + ["..."] + lineas[-2:]

        for i, linea in enumerate(muestra):
            linea = linea.strip()
            pos_ini = f"{i + 1}.0"
            text.insert("end", linea + "\n")

            if linea.startswith("22"):
                text.tag_add('campo_fecha',  f"{i+1}.8",  f"{i+1}.14")
                text.tag_add('campo_valor',  f"{i+1}.14", f"{i+1}.20")
                text.tag_add('campo_importe',f"{i+1}.31", f"{i+1}.45")
                text.tag_add('campo_concepto',f"{i+1}.55", f"{i+1}.80")

            elif linea.startswith("2301"):
                text.tag_add('campo_ref1', f"{i+1}.4", f"{i+1}.64")

            elif linea.startswith("2302"):
                text.tag_add('campo_ref2', f"{i+1}.4", f"{i+1}.64")

        text.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Error Norma 43", str(e))
        if parent:
            parent.destroy()
            parent.after(100, lambda: mostrar_configuracion(parent.master, config))

