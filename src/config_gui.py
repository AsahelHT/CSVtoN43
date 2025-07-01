import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Combobox, Entry, Button, Frame, Label, LabelFrame, Treeview, Scrollbar
import pandas as pd
import json
import csv

from app import ventanas_abiertas

ok = False

BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath((os.path.dirname(__file__))))

def obtener_ruta_icono():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'media', 'csv2n43.ico')
    return os.path.join(os.path.dirname(__file__), '..', 'media', 'csv2n43.ico')

CONFIG_FILE = os.path.join(BASE_DIR, 'CSVtoN43_CFG.json')

def cargar_config():
    existe = os.path.exists(CONFIG_FILE)
    if existe:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f), True
    return {
        'sep': '',
        'fecha operacion': 'Sin asignar',
        'fecha valor': 'Sin asignar',
        'concepto': 'Sin asignar',
        'importe': 'Sin asignar',
        'cuenta': 'Sin asignar',
        'saldo': 'Sin asignar',
        'referencia 1': 'Sin asignar',
        'referencia 2': 'Sin asignar',
        'nombre_empresa': '',
        'last_csv_path': '',
        'last_csv_file': '',
        'last_output_path': ''
    }, False

def guardar_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

DIVISAS = {
    'Euro (EUR)': '978',
    'Dólar estadounidense (USD)': '840',
    'Libra esterlina (GBP)': '826',
    'Yen japonés (JPY)': '392',
    'Yuan chino (CNY)': '156',
}

SUGERENCIAS_COLUMNAS = {
    'fecha operacion': ['fecha operación', 'operacion', 'fecha operacion'],
    'fecha valor': ['fecha valor', 'valor'],
    'concepto': ['concepto', 'descripcion', 'descripción'],
    'importe': ['importe', 'cantidad'],
    'cuenta': ['cuenta', 'número cuenta'],
    'saldo': ['saldo'],
    'referencia 1': ['referencia1', 'ref1', 'referencia 1'],
    'referencia 2': ['referencia2', 'ref2', 'referencia 2']
}

def hay_campos_sin_asignar(config):
    for clave in config:
        if clave not in ("referencia 1", "referencia 2"):
            if config[clave] == "Sin asignar":
                return True
    return False

def mostrar_configuracion(parent, config) :
    # Evitar duplicados
    if ventanas_abiertas.get("config") and ventanas_abiertas["config"].winfo_exists():
        ventanas_abiertas["config"].focus()
        return
    
    state = {
        'config': config,
        'vars': {},
        'df_columnas': [],
        'tree': None,
        'preview_frame': None,
        'window': None,
        'parent': parent
    }

    if not os.path.exists(CONFIG_FILE):
        if not solicitar_csv(state):
            return False
    if configuracion_vacia(state['config']):
        if not solicitar_csv(state):
            return False

    #boton_inicio.config(state="disabled")
    window = tk.Toplevel(parent)

    window.title("⚙️ Configuración de campos")
    window.geometry("1500x700")
    window.minsize(1500, 700)
    window.iconbitmap(obtener_ruta_icono())
    window.protocol("WM_DELETE_WINDOW", lambda: (window.destroy()))
    
    ventanas_abiertas["config"] = window
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1, uniform="col")
    window.grid_columnconfigure(1, weight=2, uniform="col")

    state['window'] = window

    leer_columnas_csv(state)
    crear_campos(state)
    crear_preview(state)

def configuracion_vacia(config):
    return not all(k in config for k in SUGERENCIAS_COLUMNAS)

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
            for clave in SUGERENCIAS_COLUMNAS:
                state['config'][clave] = "Sin asignar"
            guardar_config(state['config'])
            return True
        else:
            return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo CSV:\n{e}")
        return False

def leer_columnas_csv(state):
    config = state['config']
    full_path = config.get("last_csv_file", "")
    if not full_path or not os.path.isfile(full_path):
        state['df_columnas'] = []
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

def asignar_campos_automaticamente(config, columnas):
    columnas_csv = [col.strip().lower() for col in columnas]
    for clave, sugeridos in SUGERENCIAS_COLUMNAS.items():
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

    for i, (key, _) in enumerate(SUGERENCIAS_COLUMNAS.items()):
        label_text = key

        es_sin_asignar = config.get(key) == "Sin asignar"
        label_style = {
            "font": ("Arial", 10, "bold"),
            "foreground": "#ffc107" if es_sin_asignar else "white"
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
                print(var.get())
                state["advertencia_label"] = mostrar_advertencia_final(window)

        etiquetas[key] = label
        combos[key] = combo

        def bind_trace(var, key, label_ref, combo_ref):
            def callback(*_):
                valor = var.get()
                if valor != "Sin asignar":
                    label_ref.config(foreground="white", font=("Arial", 10, "bold"))
                    combo_ref.configure(style="primary.TCombobox")
                else:
                    label_ref.config(foreground="#ffc107", font=("Arial", 10, "bold"))
                    combo_ref.configure(style="Warning.TCombobox")

                # Verificar si todos están asignados
                if not hay_campos_sin_asignar(config) or (all(vars_[k].get() != "Sin asignar" for k in SUGERENCIAS_COLUMNAS if k not in ("referencia 1", "referencia 2"))):
                    if state.get("advertencia_label"):
                        state["advertencia_label"].destroy()
                        state["advertencia_label"] = None
                else:
                    if not state.get("advertencia_label"):
                        state["advertencia_label"] = mostrar_advertencia_final(window)

            var.trace_add("write", callback)

        # Aquí llamamos a la función pasándole las variables correctas
        bind_trace(var, key, label, combo)
        
    row_total = offset + len(SUGERENCIAS_COLUMNAS)
    Label(frame_total, text="Divisa").grid(row=row_total, column=0, sticky='e', padx=(0, 10), pady=5)
    var_divisa = tk.StringVar(value=config.get('divisa_nombre', 'Euro (EUR)'))
    vars_['divisa_nombre'] = var_divisa
    Combobox(frame_total, textvariable=var_divisa, values=list(DIVISAS.keys()), width=33, bootstyle="success")\
        .grid(row=row_total, column=1, sticky='ew', padx=5, pady=5)

    Button(frame_total, text="📝 Editar archivo CSV", bootstyle="secondary",
           command=lambda: abrir_csv_en_explorador(state))\
        .grid(row=row_total + 1, column=0, columnspan=2, pady=(0, 6), sticky='ew', padx=5)

    Button(frame_total, text="🔄 Cambiar plantilla CSV", bootstyle="warning",
           command=lambda: cambiar_plantilla_csv(state))\
        .grid(row=row_total + 2, column=0, columnspan=2, pady=(0, 24), sticky='ew', padx=5)

    Button(frame_total, text="💾 Guardar configuración", bootstyle="info",
           command=lambda: guardar_configuracion(state))\
        .grid(row=row_total + 3, column=0, columnspan=2, pady=12, sticky='ew', padx=5)


def crear_preview(state):
    frame = LabelFrame(state['window'], text="Vista previa de la plantilla CSV", bootstyle="light")
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
    cargar_preview_csv(state)

def cargar_preview_csv(state):
    config = state['config']
    full_path = config.get("last_csv_file", "")
    if not full_path or not os.path.isfile(full_path):
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
    for campo in SUGERENCIAS_COLUMNAS:
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
    config['divisa_codigo'] = DIVISAS.get(nombre_divisa, '978')

    guardar_config(config)
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

def cambiar_plantilla_csv(state):
    try:
        archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])
        if archivo:
            carpeta = os.path.dirname(archivo)
            state['config']['last_csv_path'] = carpeta
            state['config']['last_csv_file'] = archivo
            with open(archivo, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                state['config']['sep'] = csv.Sniffer().sniff(sample).delimiter
            for clave in SUGERENCIAS_COLUMNAS:
                state['config'][clave] = "Sin asignar"
            guardar_config(state['config'])
            state['window'].destroy()
            state['window'].after(100, lambda: mostrar_configuracion(state['parent'], state['config']))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo CSV:\n{e}")


def mostrar_advertencia_final(parent):
    advertencia = Label(
        parent,
        text="⚠️ Algunos campos obligatorios están sin asignar. Revísalos antes de continuar.",
        style="Advertencia.TLabel",
        anchor="center",
        padding=10,
        justify="center",
        wraplength=900
    )
    advertencia.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
    return advertencia
