# gui.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json

CONFIG_FILE = 'config.json'

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
        
        self.configuracion = config
        self.df_columnas = []


        if not os.path.exists("config.json"):
            self._solicitar_csv()

        if self._configuracion_vacia():
            self._solicitar_csv()

        self.title("Configuración")
        self.geometry("900x600")

        self.vars = {}
        self._leer_columnas_csv()
        self._crear_campos()
        self._crear_preview()

    def _configuracion_vacia(self):
        campos_requeridos = [
            'campo_fecha', 'campo_valor', 'campo_concepto', 'campo_ref1',
            'campo_importe', 'campo_cuenta', 'campo_saldo', 'campo_ref2'
        ]
        return not all(k in self.configuracion for k in campos_requeridos)

    def _solicitar_csv(self):
        messagebox.showinfo("Carga inicial", "No se ha encontrado una configuración previa para procesar la información. \nSelecciona un archivo CSV para empezar a utilizar como plantilla.")
        archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])
        if archivo:
            carpeta = os.path.dirname(archivo)
            self.configuracion['last_csv_path'] = carpeta
            self.configuracion['sep'] = self.configuracion.get('sep', ';')
            for clave in [
                'campo_fecha', 'campo_valor', 'campo_concepto', 'campo_ref1',
                'campo_importe', 'campo_cuenta', 'campo_saldo', 'campo_ref2'
            ]:
                self.configuracion[clave] = "Sin asignar"
            guardar_config(self.configuracion)
        else:
            self.destroy()

    def _leer_columnas_csv(self):
        try:
            path = self.configuracion.get("last_csv_path", "")
            if not path:
                return
            archivos = [f for f in os.listdir(path) if f.endswith(".csv")]
            if not archivos:
                return
            full_path = os.path.join(path, archivos[0])
            df = pd.read_csv(full_path, sep=self.configuracion.get("sep", ";"), nrows=1)
            self.df_columnas = df.columns.tolist()

            self._asignar_campos_automaticamente()
        except:
            self.df_columnas = []
            
    def _asignar_campos_automaticamente(self):
        columnas_csv_original = self.df_columnas  # Conservamos nombres originales
        columnas_csv = [col.strip().lower() for col in columnas_csv_original]

        for clave, sugeridos in SUGERENCIAS_COLUMNAS.items():
            for sugerido in sugeridos:
                sugerido_lower = sugerido.lower()
                if sugerido_lower in columnas_csv:
                    indice = columnas_csv.index(sugerido_lower)
                    self.configuracion[clave] = columnas_csv_original[indice]  # Usamos el nombre original
                    break

    def _crear_campos(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        campos_texto = [
            ('Separador', 'sep'),
            ('Nombre Empresa', 'nombre_empresa'),
        ]

        campos_combo = [
            ('Fecha Operación', 'campo_fecha'),
            ('Fecha Valor', 'campo_valor'),
            ('Concepto', 'campo_concepto'),
            ('Importe', 'campo_importe'),
            ('Cuenta', 'campo_cuenta'),
            ('Saldo', 'campo_saldo'),
            ('Referencia 1', 'campo_ref1'),
            ('Referencia 2', 'campo_ref2'),
        ]

        for i, (label, key) in enumerate(campos_texto):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky='e')
            var = tk.StringVar(value=self.configuracion.get(key, ''))
            self.vars[key] = var
            tk.Entry(frame, textvariable=var, width=30).grid(row=i, column=1, sticky='w')

        offset = len(campos_texto)
        for i, (label, key) in enumerate(campos_combo):
            tk.Label(frame, text=label).grid(row=i+offset, column=0, sticky='e')
            var = tk.StringVar(value=self.configuracion.get(key, ''))
            self.vars[key] = var
            combo = ttk.Combobox(frame, textvariable=var, values=self.df_columnas, width=28)
            combo.grid(row=i+offset, column=1, sticky='w')

        row_total = offset + len(campos_combo)
        # Campo para la divisa
        tk.Label(frame, text="Divisa").grid(row=row_total, column=0, sticky='e')
        var_divisa = tk.StringVar(value=self.configuracion.get('divisa_nombre', 'Euro (EUR)'))
        self.vars['divisa_nombre'] = var_divisa
        combo_divisa = ttk.Combobox(frame, textvariable=var_divisa, values=list(DIVISAS.keys()), width=28)
        combo_divisa.grid(row=row_total, column=1, sticky='w')
        
        row_total += 1
        tk.Button(frame, text="Guardar", command=self._guardar).grid(row=row_total, column=0, columnspan=2, pady=10)
       
    def _crear_preview(self):
        self.preview_frame = tk.LabelFrame(self, text="Vista previa del CSV")
        self.preview_frame.pack(pady=5, fill="both", expand=True)

        self.tree = ttk.Treeview(self.preview_frame, show='headings')
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self._cargar_preview_csv()


    def _cargar_preview_csv(self):
        try:
            path = self.configuracion.get("last_csv_path", "")
            if not path:
                return
            archivos = [f for f in os.listdir(path) if f.endswith(".csv")]
            if not archivos:
                return
            full_path = os.path.join(path, archivos[0])
            df = pd.read_csv(full_path, sep=self.configuracion.get("sep", ";"))
            
            self.preview_frame.config(text=f"Vista previa del CSV: {os.path.basename(full_path)}")

            # Limpiar columnas y filas anteriores si las hay
            for col in self.tree["columns"]:
                self.tree.heading(col, text="")
            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = list(df.columns)

            for col in df.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, anchor='center')

            for _, row in df.head(10).iterrows():
                self.tree.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("Error al cargar CSV", f"No se pudo cargar la vista previa del CSV.\n{e}")

        except Exception as e:
            messagebox.showerror("Error generando preview", str(e))

    def _guardar(self):
        for k, var in self.vars.items():
            self.configuracion[k] = var.get()

        nombre_divisa = self.configuracion.get('divisa_nombre', 'Euro (EUR)')
        self.configuracion['divisa_codigo'] = DIVISAS.get(nombre_divisa, '978')

        guardar_config(self.configuracion)
        self.destroy()


def mostrar_configuracion(parent, config):
    ConfiguracionVentana(parent, config)
