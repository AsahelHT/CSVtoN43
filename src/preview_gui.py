import os
import sys
import pandas as pd

from tkinter import ttk, TclError
from tkinter import Toplevel, Text, Scrollbar, BOTH, Y, RIGHT, LEFT, END, filedialog, messagebox, Frame, Label
from ttkbootstrap import LabelFrame, Treeview, Scrollbar, Button, Style

from converter import generar_norma43_temp 
from config_gui import mostrar_configuracion
from converter import convertir_con_archivo_existente
from ttkbootstrap.widgets import Treeview

from datetime import datetime
from decimal import Decimal

from csv2n43_utils import ventanas_abiertas, ruta_icono, show_ico_warn

import csv2n43_utils as utils


def mostrar_previsualizacion(parent, config):
    def on_convertir(lineas_n43):
        convertir_con_archivo_existente(config, archivo, lineas_n43)
        preview_win.destroy()

    # Evitar duplicados
    if ventanas_abiertas.get("preview") and ventanas_abiertas["preview"].winfo_exists():
        ventanas_abiertas["preview"].focus()
        return
    
    #boton_inicio.config(state="disabled")
    config, existe_config = utils.cargar_config()

    if not existe_config:
        messagebox.showerror("No existe configuración guardada", "Porfavor, guarde una configuración.")
        if parent:
            parent.after(100, lambda: mostrar_configuracion(parent, config, None))
        return
        
    if utils.hay_campos_sin_asignar(config):
        messagebox.showerror("Existen campos obligatorios sin asignar", "Porfavor, revise la configuración.")
        if parent:
            parent.after(100, lambda: mostrar_configuracion(parent, config, None))
        return

    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo CSV",
        filetypes=[("CSV files", "*.csv")]
    )

    if not archivo:
        return

    ok, mensaje = utils.validar_estructura_csv(config, archivo)
    if not ok:
        respuesta = messagebox.askyesno(
            "Archivo incompatible",
            f"{mensaje}\n\n¿Deseas abrir la configuración para adaptarla al nuevo CSV?"
        )
        if respuesta:  # Sí → abrir configuración
            if parent:
                parent.after(100, lambda: mostrar_configuracion(parent, config, archivo))
        return

    # Verifica si el contenedor principal sigue existiendo
    if not parent.winfo_exists():
        return
    
    preview_win = Toplevel()
    if not preview_win.winfo_exists():
        return
    preview_win.withdraw()
    try:
        preview_win.iconbitmap(ruta_icono)
    except Exception as e:
        if utils.show_ico_warn:
            messagebox.showwarning("Archivo no encontrado", "No se encontró la imagen de icono de la aplicación: csv2n43.ico")
            utils.show_ico_warn = False
    preview_win.deiconify()
    preview_win.title("🔍 Previsualización de la conversión")
    preview_win.geometry("1200x800")
    preview_win.minsize(1200, 800)

    
        

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
    frame_n43 = LabelFrame(container, text="📃 Previsualización Norma 43 (5 primeras y 2 últimas líneas)", bootstyle="primary")
    frame_n43.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
    
    lineas_n43 = generar_norma43_temp(archivo, config)
    _mostrar_tabla_norma43(frame_n43, lineas_n43, parent=preview_win)
    
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
        command=lambda: on_convertir(lineas_n43)
    )
    boton_guardar.grid(row=0, column=0, sticky="nsew")
      


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

    for i, (campo, color) in enumerate(utils.colores.items(), start=1):
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
                if valor[:2].isalpha() and len(valor) > 20:
                    return valor[4:]  # elimina 'ES' + 2 dígitos
                return valor

            df['cuenta'] = df['cuenta'].apply(limpiar_iban)

    except Exception as e:
        messagebox.showerror("Error previsualización CSV", str(e))
        return

    columnas = list(df.columns)
    colores_por_columna = utils.mapear_colores_desde_config(config, utils.colores)

    for i, col in enumerate(columnas):
        col_norm = utils.normalizar(col)  # normaliza el nombre del CSV
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

def _mostrar_tabla_norma43(frame, lineas, parent=None):
    import tkinter as tk
    text = tk.Text(
        frame,
        wrap="none",
        font=("Courier", 10),
        height=8,
        relief="flat",
        borderwidth=0,
        highlightthickness=0
    )
    text.pack(fill=BOTH, expand=True, side=LEFT)
    
    text.configure(
        bg="#2c2f33",         
        fg="white",           
        insertbackground="white"
    )
   
    # Colores legibles en tema oscuro

    for campo, color in utils.colores.items():
        text.tag_config(campo, foreground=color)

    try:
        
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
                text.tag_add('referencia 1',  f"{i+1}.52", f"{i+1}.80")

            elif linea.startswith("23"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('contadores', f"{i+1}.2", f"{i+1}.4")
                if linea.startswith("2301") and i > 0:
                    linea_anterior = muestra[i - 1].strip()
                    referencia1_anterior = linea_anterior[52:80]
                    # Comprobar si la referencia 1 anterior termina en "0", la linea ref1 es concepto
                    if referencia1_anterior.rstrip().endswith("0"):
                        text.tag_add('concepto', f"{i+1}.4", f"{i+1}.64")
                    else:
                        if i < len(muestra) - 1:
                            linea_siguiente = muestra[i + 1].strip()
                            if linea_siguiente.startswith("2302"):
                                text.tag_add('referencia 2', f"{i+1}.4", f"{i+1}.64")
                            else:
                                text.tag_add('concepto', f"{i+1}.4", f"{i+1}.64")
                elif linea.startswith("2301"):
                    text.tag_add('concepto', f"{i+1}.4", f"{i+1}.64")

            

            elif linea.startswith("11"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('cuenta', f"{i+1}.2", f"{i+1}.20")
                text.tag_add('fecha operacion', f"{i+1}.20", f"{i+1}.26")
                text.tag_add('fecha valor', f"{i+1}.26", f"{i+1}.32")
                text.tag_add('tipo importe', f"{i+1}.32", f"{i+1}.33")
                text.tag_add('saldo', f"{i+1}.33", f"{i+1}.47")
                text.tag_add('divisa', f"{i+1}.47", f"{i+1}.50")

            elif linea.startswith("33"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('cuenta', f"{i+1}.2", f"{i+1}.20")
                text.tag_add('contadores', f"{i+1}.20", f"{i+1}.25")
                text.tag_add('importe',   f"{i+1}.25", f"{i+1}.39")
                text.tag_add('contadores', f"{i+1}.39", f"{i+1}.44")
                text.tag_add('importe',   f"{i+1}.44", f"{i+1}.58")
                text.tag_add('tipo importe', f"{i+1}.58", f"{i+1}.59")
                text.tag_add('saldo', f"{i+1}.59", f"{i+1}.73")
                text.tag_add('divisa', f"{i+1}.73", f"{i+1}.76")

            elif linea.startswith("88"):
                text.tag_add('codigo',     f"{i+1}.0",  f"{i+1}.2")
                text.tag_add('contadores', f"{i+1}.22", f"{i+1}.28")


        text.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Error previsualización Norma43", str(e))
        

