import os
import sys
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Combobox, Entry, Button, Frame, Label, LabelFrame, Treeview, Scrollbar
import pandas as pd
import json
import csv

from csv2n43_utils import ventanas_abiertas, ruta_icono
import csv2n43_utils as utils

ok = False


def al_cerrar(parent, state):
    from json import dumps

    window = state['window']
    config = state['config']
    saved_config = state.get('saved_config', {})

    # Actualizar config actual con lo que hay en la interfaz
    for key, var in state['vars'].items():
        config[key] = var.get()

    # Comparar solo los campos relevantes
    claves_relevantes = list(utils.SUGERENCIAS_COLUMNAS.keys()) + ['sep', 'nombre_empresa', 'divisa_nombre']
    config_actual = {k: config.get(k) for k in claves_relevantes}
    config_guardado = {k: saved_config.get(k) for k in claves_relevantes}

    if dumps(config_actual, sort_keys=True) != dumps(config_guardado, sort_keys=True):
        respuesta = messagebox.askyesno(
            "⚠️ Cambios no guardados ⚠️",
            "Has hecho cambios en la configuración que no se han guardado.\n¿Estás seguro de que quieres salir sin guardar?"
        )
        if not respuesta:
            return
        
    if "config" in ventanas_abiertas:
        ventanas_abiertas["config"] = None

    window.destroy()
    parent.destroy()

def mostrar_configuracion(parent, config, archivo=None) :
    # Evitar duplicados
    if ventanas_abiertas.get("config") and ventanas_abiertas["config"].winfo_exists():
        ventanas_abiertas["config"].focus()
        return
    
    saved_config, _ = utils.cargar_config()
    state = {
        'config': config,
        'saved_config': saved_config,
        'vars': {},
        'df_columnas': [],
        'tree': None,
        'preview_frame': None,
        'window': None,
        'parent': parent
    }

    if archivo != None:
        cambiar_plantilla_csv(state, archivo)

    if not os.path.exists(utils.CONFIG_FILE):
        if not solicitar_csv(state):
            return False
    if utils.configuracion_vacia(state['config']):
        if not solicitar_csv(state):
            return False

    #boton_inicio.config(state="disabled")
    window = ttk.Toplevel(parent)

    window.title("⚙️ Configuración de campos")
    window.geometry("1500x700")
    window.minsize(1500, 700)
    try:
        window.iconbitmap(ruta_icono)
    except Exception as e:
        if utils.show_ico_warn:
            messagebox.showwarning("Archivo no encontrado", "No se encontró la imagen de icono de la aplicación: csv2n43.ico")
            utils.show_ico_warn = False
        
    window.protocol("WM_DELETE_WINDOW", lambda: al_cerrar(window, state))
    
    ventanas_abiertas["config"] = window
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1, uniform="col")
    window.grid_columnconfigure(1, weight=2, uniform="col")

    state['window'] = window

    leer_columnas_csv(state, archivo)
    crear_campos(state)
    crear_preview(state, archivo)



def solicitar_csv(state):
    respuesta = messagebox.askokcancel("Cargar plantilla CSV", "No se ha encontrado una configuración previa.\nSelecciona un archivo CSV para utilizar como plantilla.")
    if not respuesta:
        return False
    try:
        archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])
        if archivo:
            carpeta = os.path.dirname(archivo)
            state['config']['last_csv_path'] = carpeta
            state['config']['last_csv_file'] = archivo
            with open(archivo, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                sep_detectado = csv.Sniffer().sniff(sample).delimiter
                state['config']['sep'] = sep_detectado
            for clave in utils.SUGERENCIAS_COLUMNAS:
                state['config'][clave] = "Sin asignar"
            utils.guardar_config(state['config'])
            return True
        else:
            return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo CSV:\n{e}")
        return False

def leer_columnas_csv(state, archivo=None):
    config = state['config']
    full_path = config.get("last_csv_file", "")

    if archivo != None:
        full_path = archivo
        state['config']['last_csv_file'] = archivo

    if not full_path or not os.path.isfile(full_path):
        state['df_columnas'] = []
        messagebox.showwarning("Archivo no encontrado", "No se encontró el archivo deseado")
        return
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            sample = f.read(2048)
            sep_detectado = csv.Sniffer().sniff(sample).delimiter
            config['sep'] = sep_detectado
        df = pd.read_csv(full_path, sep=sep_detectado, nrows=1)
        columnas = df.columns.tolist()
        state['df_columnas'] = columnas
        asignar_campos_automaticamente(config, columnas)
    except:
        state['df_columnas'] = []
        messagebox.showerror("Error al cargar CSV", f"No se pudo cargar la vista previa del CSV.\n")

def asignar_campos_automaticamente(config, columnas):
    columnas_csv = [col.strip().lower() for col in columnas]
    for clave, sugeridos in utils.SUGERENCIAS_COLUMNAS.items():
        for sugerido in sugeridos:
            if sugerido.lower() in columnas_csv:
                idx = columnas_csv.index(sugerido.lower())
                config[clave] = columnas[idx]
                break

def crear_campos(state):
    window = state['window']
    config = state['config']
    vars_ = state['vars']

    style = Style()
    style.configure("Warning.TCombobox", fieldbackground="#fff3cd", foreground="#856404")
    style.configure("Advertencia.TLabel", background="#fff3cd", foreground="#856404", font=("Arial", 10, "bold"))

    frame_total = Frame(window)
    frame_total.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
    frame_total.grid_columnconfigure(0, weight=0)
    frame_total.grid_columnconfigure(1, weight=1)

    campos_texto = [('Separador', 'sep'), ('Nombre Empresa', 'nombre_empresa')]

    for i, (label, key) in enumerate(campos_texto):
        Label(frame_total, text=label).grid(row=i, column=0, sticky='e', padx=(0, 10), pady=5)
        var = tk.StringVar(value=config.get(key, ''))
        vars_[key] = var
        Entry(frame_total, textvariable=var, width=10 if key == 'sep' else 35,
              state='readonly' if key == 'sep' else 'normal').grid(row=i, column=1, sticky='ew', padx=5, pady=5)

    offset = len(campos_texto)
    etiquetas = {}
    combos = {}

    for i, (key, _) in enumerate(utils.SUGERENCIAS_COLUMNAS.items()):
        label_text = key

        es_sin_asignar = config.get(key) == "Sin asignar"
        label_style = {
            "font": ("Arial", 10, "bold"),
            "foreground": "#ffc107" if es_sin_asignar else ("white" if "dark" in config['tema'] else "black")
        }

        label = Label(frame_total, text=label_text, **label_style)
        label.grid(row=i + offset, column=0, sticky='e', padx=(0, 10), pady=3)

        var = tk.StringVar(value=config.get(key, ''))
        vars_[key] = var

        combo = Combobox(frame_total, textvariable=var, values=state['df_columnas'], width=33, bootstyle="primary")
        combo.grid(row=i + offset, column=1, sticky='ew', padx=5, pady=3)

        if es_sin_asignar:
            combo.configure(style="Warning.TCombobox")
            if not state.get("advertencia_label") and key not in ("referencia 1", "referencia 2"):
                state["advertencia_label"] = mostrar_advertencia_final(window)

        etiquetas[key] = label
        combos[key] = combo

        def bind_trace(var, key, label_ref, combo_ref):
            def callback(*_):
                valor = var.get()
                if valor != "Sin asignar":
                    label_ref.config(foreground="white" if "dark" in config['tema'] else "black", font=("Arial", 10, "bold"))
                    combo_ref.configure(style="primary.TCombobox")
                else:
                    label_ref.config(foreground="#ffc107", font=("Arial", 10, "bold"))
                    combo_ref.configure(style="Warning.TCombobox")

                # Verificar si todos están asignados
                if not utils.hay_campos_sin_asignar(config) or (all(vars_[k].get() != "Sin asignar" for k in utils.SUGERENCIAS_COLUMNAS if k not in ("referencia 1", "referencia 2"))):
                    if state.get("advertencia_label"):
                        state["advertencia_label"].destroy()
                        state["advertencia_label"] = None
                else:
                    if not state.get("advertencia_label"):
                        state["advertencia_label"] = mostrar_advertencia_final(window)

            var.trace_add("write", callback)

        # Aquí llamamos a la función pasándole las variables correctas
        bind_trace(var, key, label, combo)
        
    row_total = offset + len(utils.SUGERENCIAS_COLUMNAS)
    Label(frame_total, text="Divisa").grid(row=row_total, column=0, sticky='e', padx=(0, 10), pady=5)
    var_divisa = tk.StringVar(value=config.get('divisa_nombre', 'Euro (EUR)'))
    vars_['divisa_nombre'] = var_divisa
    Combobox(frame_total, textvariable=var_divisa, values=list(utils.DIVISAS.keys()), width=33, bootstyle="success")\
        .grid(row=row_total, column=1, sticky='ew', padx=5, pady=5)

    Button(frame_total, text="📝 Editar archivo CSV", bootstyle="secondary",
           command=lambda: abrir_csv_en_explorador(state))\
        .grid(row=row_total + 1, column=0, columnspan=2, pady=(0, 6), sticky='ew', padx=5)

    Button(frame_total, text="🔄 Cambiar plantilla CSV", bootstyle="warning",
           command=lambda: cambiar_plantilla_csv(state, None))\
        .grid(row=row_total + 2, column=0, columnspan=2, pady=(0, 24), sticky='ew', padx=5)

    Button(frame_total, text="💾 Guardar configuración", bootstyle="info",
       command=lambda: guardar_configuracion(state), padding=(0, 10))\
    .grid(row=row_total + 3, column=0, columnspan=2, pady=12, sticky='ew', padx=5)

def crear_preview(state, archivo=None):
    frame = LabelFrame(state['window'], text="Vista previa de la plantilla CSV", bootstyle="secondary")
    frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=10)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    tree = Treeview(frame, show='headings')
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar = Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")

    state['tree'] = tree
    state['preview_frame'] = frame
    cargar_preview_csv(state, archivo)

def cargar_preview_csv(state, archivo=None):
    config = state['config']
    full_path = config.get("last_csv_file", "")

    if archivo != None:
        full_path = archivo
        state['config']['last_csv_file'] = archivo
    if not full_path or not os.path.isfile(full_path):
        messagebox.showwarning("Archivo no encontrado", "No se encontró el archivo deseado")
        return
    try:
        df = pd.read_csv(full_path, sep=config.get("sep", ";"))
        state['preview_frame'].config(text=f"Vista previa de la plantilla CSV: {os.path.basename(full_path)}")

        tree = state['tree']
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        for _, row in df.head(10).iterrows():
            tree.insert("", "end", values=list(row))
    except Exception as e:
        messagebox.showerror("Error al cargar CSV", f"No se pudo cargar la vista previa del CSV.\n{e}")

def guardar_configuracion(state):
    config = state['config']
    campos_sin_asignar = []

    for k, var in state['vars'].items():
        config[k] = var.get()

    # Detectar campos obligatorios sin asignar
    for campo in utils.SUGERENCIAS_COLUMNAS:
        if campo in ('referencia 1', 'referencia 2'):
            continue  # No obligatorios
        if config.get(campo) == "Sin asignar":
            campos_sin_asignar.append(campo)

    if campos_sin_asignar:
        campos_str = "\n - " + "\n - ".join(campos_sin_asignar)
        respuesta = messagebox.askokcancel(
            "⚠️ Advertencia: campos sin asignar ⚠️",
            f"Los siguientes campos obligatorios no han sido asignados:{campos_str}\n\n"
            "¿Deseas guardar la configuración igualmente y salir?"
        )
        if not respuesta:
            return  # Cancelar: el usuario quiere seguir editando

    # Guardar divisa
    nombre_divisa = config.get('divisa_nombre', 'Euro (EUR)')
    config['divisa_codigo'] = utils.DIVISAS.get(nombre_divisa, '978')

    utils.guardar_config(config)
    if "config" in ventanas_abiertas:
        ventanas_abiertas["config"] = None
    state['window'].destroy()

def abrir_csv_en_explorador(state):
    full_path = state['config'].get("last_csv_file", "")
    if not full_path or not os.path.isfile(full_path):
        messagebox.showwarning("Archivo no encontrado", "No se encontró el archivo CSV guardado como plantilla.")
        return
    try:
        os.startfile(full_path)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo CSV:\n{e}")

def cambiar_plantilla_csv(state, archivo=None):
    try:
        if ventanas_abiertas.get("config") is not None:
            window = ventanas_abiertas["config"]
        else:
            window = ventanas_abiertas["root"]
            
        if archivo == None:
            archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])

        window.focus()
        if archivo:
            carpeta = os.path.dirname(archivo)
            state['config']['last_csv_path'] = carpeta
            state['config']['last_csv_file'] = archivo
            with open(archivo, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                state['config']['sep'] = csv.Sniffer().sniff(sample).delimiter
            for clave in utils.SUGERENCIAS_COLUMNAS:
                state['config'][clave] = "Sin asignar"

            utils.guardar_config(state['config'])
            if "config" in ventanas_abiertas:
                ventanas_abiertas["config"] = None 
                if state['window']:
                    state['window'].destroy()

            state['parent'].after(100, lambda: mostrar_configuracion(state['parent'], state['config'], None))
    except Exception as e:
        messagebox.showerror("Error abriendo archivo", f"No se pudo abrir el archivo CSV:\n{e}")


def mostrar_advertencia_final(parent):
    advertencia = Label(
        parent,
        text="⚠️ Algunos campos obligatorios están sin asignar. Revísalos antes de continuar. ⚠️",
        style="Advertencia.TLabel",
        anchor="center",
        padding=10,
        justify="center",
        wraplength=900
    )
    advertencia.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
    return advertencia
