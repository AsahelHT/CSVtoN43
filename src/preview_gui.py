from tkinter import ttk, TclError
from tkinter import Toplevel, Text, Scrollbar, BOTH, Y, RIGHT, LEFT, END, CENTER, filedialog, messagebox, Frame, Label
from ttkbootstrap import LabelFrame, Treeview, Scrollbar, Button, Style
import pandas as pd
from conversor import generar_norma43_temp 
from config_gui import cargar_config, mostrar_configuracion
from conversor import convertir_con_archivo_existente
from ttkbootstrap.widgets import Treeview
import os
import sys

from app import ventanas_abiertas

import unicodedata

# Colores por campo
colores = {
    'codigo':"#18B01F",
    'cuenta':"#0088ff",
    'fecha operacion': '#ff6b6b',    
    'fecha valor': '#61dafb',     
    'concepto': '#a3e635',  
    'importe': '#facc15',   
    'saldo': "#ff7c01",     
    'referencia1': '#c084fc',      
    'referencia2': '#f472b6',       
    'divisa':"#00ffbb",
    'tipo importe':"#00ff00",
    'contadores':"#ff0000"
}


def normalizar(nombre):
    nombre = nombre.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('utf-8')
    return nombre

def mapear_colores_desde_config(config, colores):
    colores_por_columna = {}

    for campo, nombre_columna in config.items():
        if campo in ['nombre_empresa', 'sep', 'last_csv_path', 'last_csv_file', 'last_output_path']:
            continue

        if nombre_columna == 'Sin asignar' or not nombre_columna.strip():
            continue

        color = colores.get(campo, "#e0e0e0")
        colores_por_columna[normalizar(nombre_columna)] = color  # clave normalizada

    return colores_por_columna

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
        preview_win.geometry("1200x800")
        preview_win.minsize(1200, 800)
        preview_win.iconbitmap(obtener_ruta_icono())
        preview_win.protocol("WM_DELETE_WINDOW", lambda: (preview_win.destroy()))
        # Contenedor principal
        
        ventanas_abiertas["preview"] = preview_win
        
        container = ttk.Frame(preview_win)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        container.grid_rowconfigure(0, weight=1)  # Info
        # --- Botón para mostrar leyenda ---
        btn_leyenda = Button(
            container,
            text="📘 Ver leyenda",
            bootstyle="info-outline",
            command=lambda: mostrar_leyenda_popup(preview_win)
        )
        btn_leyenda.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=(5, 10))

        container.grid_rowconfigure(1, weight=3)  # CSV
        container.grid_rowconfigure(2, weight=1)  # Campo de texto
        container.grid_rowconfigure(3, weight=3)  # Norma43
        container.grid_rowconfigure(4, weight=3)  # Guardar
        container.grid_columnconfigure(0, weight=1)

        # --- Previsualización CSV ---
        frame_csv = LabelFrame(container, text="📄 Previsualización CSV Original (7 primeras líneas)", bootstyle="primary")
        frame_csv.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        _mostrar_tabla_csv(frame_csv, archivo, config)
        
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
    except TclError:
        return   


def mostrar_leyenda_popup(parent):
    if hasattr(parent, "_leyenda_popup") and parent._leyenda_popup and parent._leyenda_popup.winfo_exists():
        parent._leyenda_popup.focus()
        return

    popup = Toplevel(parent)
    popup.title("🎨 Leyenda de colores Norma 43")
    popup.geometry("250x475")
    popup.resizable(False, False)
    popup.transient(parent)
    popup.grab_set()

    parent._leyenda_popup = popup

    text = Text(
        popup,
        font=("Courier", 11),  # monoespaciada
        bg="white",
        fg="black",
        height=25,
        wrap="none"
    )
    text.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(popup, command=text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    text.config(yscrollcommand=scrollbar.set)

    for i, (campo, color) in enumerate(colores.items(), start=1):
        # Línea con texto y espacios coloreables
        linea = f"{campo:<15}  {' '*5}\n\n"  # línea con doble salto para separar visualmente
        text.insert(END, linea)

        # La línea visible está en la posición 2*i - 1 (1, 3, 5, ...) por el salto adicional
        linea_visible = (i * 2) - 1

        # Aplicar color del fondo a los 5 espacios finales de la línea con texto
        tag_name = f"color_{i}"
        text.tag_add(tag_name, f"{linea_visible}.17", f"{linea_visible}.22")  # 15 + 2 separación + 5 espacios
        text.tag_config(tag_name, background=color)

    text.config(state="disabled")

    
def _mostrar_tabla_csv(frame, archivo, config):
    try:
        df = pd.read_csv(archivo, sep=config['sep'], nrows=7)
        # Eliminar "ES" al inicio de la columna de cuenta si existe
        if 'cuenta' in df.columns:
            def limpiar_iban(valor):
                valor = str(valor).replace(" ", "")
                if valor.upper().startswith("ES") and len(valor) >= 24:
                    return valor[4:]  # elimina 'ES' + 2 dígitos
                return valor

            df['cuenta'] = df['cuenta'].apply(limpiar_iban)

    except Exception as e:
        messagebox.showerror("Error CSV", str(e))
        return

    columnas = list(df.columns)
    colores_por_columna = mapear_colores_desde_config(config, colores)

    for i, col in enumerate(columnas):
        col_norm = normalizar(col)  # normaliza el nombre del CSV
        color = colores_por_columna.get(col_norm, "#e0e0e0")

        subframe = Frame(frame)
        subframe.pack(side=LEFT, fill=BOTH, expand=True)

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
            if i < len(muestra) - 1:
                text.insert("end", linea + "\n")
            else:
                text.insert("end", linea)

            if linea.startswith("22"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('cuenta',     f"{i+1}.6",  f"{i+1}.10")
                text.tag_add('fecha operacion',     f"{i+1}.10",  f"{i+1}.16")
                text.tag_add('fecha valor',     f"{i+1}.16", f"{i+1}.22")
                text.tag_add('tipo importe', f"{i+1}.27", f"{i+1}.28")
                text.tag_add('importe',   f"{i+1}.28", f"{i+1}.42")
                text.tag_add('concepto',  f"{i+1}.52", f"{i+1}.80")

            elif linea.startswith("23"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('contadores', f"{i+1}.2", f"{i+1}.4")
                text.tag_add('referencia1', f"{i+1}.4", f"{i+1}.64")

            elif linea.startswith("11"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('cuenta', f"{i+1}.2", f"{i+1}.22")
                text.tag_add('fecha operacion', f"{i+1}.22", f"{i+1}.28")
                text.tag_add('fecha valor', f"{i+1}.28", f"{i+1}.34")
                text.tag_add('tipo importe', f"{i+1}.34", f"{i+1}.35")
                text.tag_add('saldo', f"{i+1}.35", f"{i+1}.49")
                text.tag_add('divisa', f"{i+1}.49", f"{i+1}.52")

            elif linea.startswith("33"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('cuenta', f"{i+1}.2", f"{i+1}.22")
                text.tag_add('contadores', f"{i+1}.22", f"{i+1}.27")
                text.tag_add('importe',   f"{i+1}.27", f"{i+1}.41")
                text.tag_add('contadores', f"{i+1}.41", f"{i+1}.46")
                text.tag_add('importe',   f"{i+1}.46", f"{i+1}.60")
                text.tag_add('tipo importe', f"{i+1}.60", f"{i+1}.61")
                text.tag_add('saldo', f"{i+1}.61", f"{i+1}.75")
                text.tag_add('divisa', f"{i+1}.75", f"{i+1}.78")

            elif linea.startswith("88"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('contadores', f"{i+1}.22", f"{i+1}.28")


        text.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Error Norma 43", str(e))
        if parent:
            parent.destroy()
            parent.after(100, lambda: mostrar_configuracion(parent.master, config))

