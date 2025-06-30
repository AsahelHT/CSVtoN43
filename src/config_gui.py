import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Combobox, Entry, Button, Frame, Label, LabelFrame, Treeview, Scrollbar
import pandas as pd
import json
import csv

import os
import sys

BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
ICON_PATH = os.path.join(BASE_DIR, 'media', 'icon.ico')

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

def cargar_config():
    existe = os.path.exists(CONFIG_FILE)
    if existe:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f), True
    return {
        'sep': ';',
        'campo_fecha': 'Sin asignar',
        'campo_valor': 'Sin asignar',
        'campo_concepto': 'Sin asignar',
        'campo_importe': 'Sin asignar',
        'campo_cuenta': 'Sin asignar',
        'campo_saldo': 'Sin asignar',
        'campo_ref1': 'Sin asignar',
        'campo_ref2': 'Sin asignar',
        'nombre_empresa': '',
        'last_csv_path': '',
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
    'campo_fecha': ['fecha operación', 'fecha', 'fecha operacion'],
    'campo_valor': ['fecha valor'],
    'campo_concepto': ['concepto'],
    'campo_importe': ['importe', 'cantidad'],
    'campo_cuenta': ['cuenta', 'número cuenta'],
    'campo_saldo': ['saldo'],
    'campo_ref1': ['referencia 1', 'ref1'],
    'campo_ref2': ['referencia 2', 'ref2']
}

class ConfiguracionVentana(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.iconbitmap(ICON_PATH)
        self.configuracion = config
        self.df_columnas = []

        self.title("⚙️ Configuración de campos")
        self.geometry("1500x650")
        self.minsize(950, 500)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=2, uniform="col")

        if not os.path.exists(CONFIG_FILE):
            self._solicitar_csv()
        if self._configuracion_vacia():
            self._solicitar_csv()

        self.vars = {}
        self._leer_columnas_csv()
        self._crear_campos()
        self._crear_preview()

    def _configuracion_vacia(self):
        return not all(k in self.configuracion for k in SUGERENCIAS_COLUMNAS)

    def _solicitar_csv(self):
        messagebox.showinfo("Carga inicial", "No se ha encontrado una configuración previa.\nSelecciona un archivo CSV para usarlo como plantilla.")
        archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])
        if archivo:
            carpeta = os.path.dirname(archivo)
            self.configuracion['last_csv_path'] = carpeta
            self.configuracion['sep'] = self.configuracion.get('sep', ';')
            for clave in SUGERENCIAS_COLUMNAS:
                self.configuracion[clave] = "Sin asignar"
            guardar_config(self.configuracion)
        else:
            self.destroy()

    def _leer_columnas_csv(self):
        try:
            path = self.configuracion.get("last_csv_path", "")
            archivos = [f for f in os.listdir(path) if f.endswith(".csv")]
            full_path = os.path.join(path, archivos[0])

            with open(full_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                sep_detectado = dialect.delimiter
                self.configuracion['sep'] = sep_detectado

            df = pd.read_csv(full_path, sep=sep_detectado, nrows=1)

            self.df_columnas = df.columns.tolist()
            self._asignar_campos_automaticamente()
        except:
            self.df_columnas = []

    def _asignar_campos_automaticamente(self):
        columnas_csv = [col.strip().lower() for col in self.df_columnas]
        for clave, sugeridos in SUGERENCIAS_COLUMNAS.items():
            for sugerido in sugeridos:
                if sugerido.lower() in columnas_csv:
                    idx = columnas_csv.index(sugerido.lower())
                    self.configuracion[clave] = self.df_columnas[idx]
                    break

    def _crear_campos(self):
        frame = Frame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        campos_texto = [
            ('Separador', 'sep'),
            ('Nombre Empresa', 'nombre_empresa'),
        ]

        campos_combo = list(SUGERENCIAS_COLUMNAS.items())

        for i, (label, key) in enumerate(campos_texto):
            Label(frame, text=label, anchor='e').grid(row=i, column=0, sticky='e', padx=(0,10), pady=5)
            var = tk.StringVar(value=self.configuracion.get(key, ''))
            self.vars[key] = var
            if key == 'sep':
                Entry(frame, textvariable=var, width=10, state='readonly').grid(row=i, column=1, sticky='w', padx=5, pady=5)
            else:
                Entry(frame, textvariable=var, width=35).grid(row=i, column=1, sticky='ew', padx=5, pady=5)


        offset = len(campos_texto)
        for i, (key, _) in enumerate(campos_combo):
            label_text = key.replace("campo_", "").replace("_", " ").title()
            Label(frame, text=label_text, anchor='e').grid(row=i+offset, column=0, sticky='e', padx=(0,10), pady=3)
            var = tk.StringVar(value=self.configuracion.get(key, ''))
            self.vars[key] = var
            combo = Combobox(frame, textvariable=var, values=self.df_columnas, width=33, bootstyle="primary")
            combo.grid(row=i+offset, column=1, sticky='ew', padx=5, pady=3)

        row_total = offset + len(campos_combo)
        Label(frame, text="Divisa", anchor='e').grid(row=row_total, column=0, sticky='e', padx=(0,10), pady=5)
        var_divisa = tk.StringVar(value=self.configuracion.get('divisa_nombre', 'Euro (EUR)'))
        self.vars['divisa_nombre'] = var_divisa
        combo_divisa = Combobox(frame, textvariable=var_divisa, values=list(DIVISAS.keys()), width=33, bootstyle="success")
        combo_divisa.grid(row=row_total, column=1, sticky='ew', padx=5, pady=5)

        Button(
            frame,
            text="💾 Guardar configuración",
            command=self._guardar,
            bootstyle="info"
        ).grid(row=row_total + 1, column=0, columnspan=2, pady=12, sticky='ew', padx=5)

    def _crear_preview(self):
        self.preview_frame = LabelFrame(self, text="Vista previa de la plantilla CSV", bootstyle="light")
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=10)

        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)

        self.tree = Treeview(self.preview_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(self.preview_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._cargar_preview_csv()

    def _cargar_preview_csv(self):
        try:
            path = self.configuracion.get("last_csv_path", "")
            archivos = [f for f in os.listdir(path) if f.endswith(".csv")]
            full_path = os.path.join(path, archivos[0])
            df = pd.read_csv(full_path, sep=self.configuracion.get("sep", ";"))

            self.preview_frame.config(text=f"Vista previa de la plantilla CSV: {os.path.basename(full_path)}")

            self.tree["columns"] = list(df.columns)
            for col in df.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor="center")

            for _, row in df.head(10).iterrows():
                self.tree.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("Error al cargar CSV", f"No se pudo cargar la vista previa del CSV.\n{e}")

    def _guardar(self):
        for k, var in self.vars.items():
            self.configuracion[k] = var.get()

        nombre_divisa = self.configuracion.get('divisa_nombre', 'Euro (EUR)')
        self.configuracion['divisa_codigo'] = DIVISAS.get(nombre_divisa, '978')

        guardar_config(self.configuracion)
        self.destroy()

def mostrar_configuracion(parent, config):
    ConfiguracionVentana(parent, config)
