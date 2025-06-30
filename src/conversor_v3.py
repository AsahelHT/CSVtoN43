# Script con ventana principal y configuración avanzada persistente
# Añadiré:
# - Entradas en la configuración para entidad, oficina, cuenta y nombre de empresa
# - Persistencia en un archivo config.json
# - Recordar rutas de entrada y salida

import os
import json
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

CONFIG_FILE = 'config.json'

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'sep': ';',
        'campo_fecha': 'FECHA OPERACION',
        'campo_concepto': 'CONCEPTO',
        'campo_importe': 'IMPORTE',
        'entidad': '0128',
        'oficina': '0532',
        'cuenta': '0100101463',
        'nombre_empresa': 'Mi Empresa SL',
        'last_csv_path': '',
        'last_output_path': ''
    }

def guardar_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def normaliza_importe(importe):
    return str((Decimal(importe).quantize(Decimal("0.01")) * 100).to_integral_value()).zfill(10)

def formatea_texto(texto, longitud):
    return texto.upper().strip().ljust(longitud)[:longitud]

def generar_norma43_estandar_80(csv_file, output_file, config):
    movimientos_por_fecha = defaultdict(list)
    
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=config['sep'])
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:
            fecha = datetime.strptime(row[config['campo_fecha']], "%d/%m/%Y").strftime("%Y%m%d")
            concepto = row[config['campo_concepto']]
            importe = Decimal(row[config['campo_importe']].replace(',', '.'))
            movimientos_por_fecha[fecha].append((concepto, importe))

    fechas = sorted(movimientos_por_fecha.keys())
    fecha_inicio = fechas[0]
    fecha_fin = fechas[-1]
    num_registros = 0
    total_movimientos = 0

    with open(output_file, 'w', encoding='utf-8') as f:
        linea_11 = f"11{config['entidad']}{config['oficina']}{config['cuenta']}{fecha_inicio[-4:]}{fecha_inicio}{fecha_fin}2000000002000009783{formatea_texto(config['nombre_empresa'], 36)}099"
        f.write(linea_11[:80] + "\n")
        num_registros += 1

        for fecha in fechas:
            grupo = movimientos_por_fecha[fecha]
            cargos = abonos = Decimal('0.00')
            ncargos = nabonos = 0

            for _, importe in grupo:
                if importe < 0:
                    ncargos += 1
                    cargos += abs(importe)
                else:
                    nabonos += 1
                    abonos += importe

            linea_22 = f"22{config['entidad']}{config['oficina']}{config['cuenta']}{fecha}{fecha}0111120000000000{str(nabonos).zfill(4)}{normaliza_importe(abonos)}{str(ncargos).zfill(4)}{normaliza_importe(cargos)}ORDEN PAGO RECIB "
            f.write(linea_22[:80] + "\n")
            num_registros += 1

            for concepto, importe in grupo:
                total_movimientos += 1
                linea_23 = f"23{'01'}{formatea_texto(concepto, 60)}"
                f.write(linea_23[:80] + "\n")
                linea_24 = f"24{formatea_texto(concepto, 160)}"
                f.write(linea_24[:80] + "\n")
                num_registros += 2

            linea_33 = f"33{config['entidad']}{config['oficina']}{config['cuenta']}{'0'*24}{str(nabonos).zfill(4)}{normaliza_importe(abonos)}{str(ncargos).zfill(4)}{normaliza_importe(cargos)}978"
            f.write(linea_33[:80] + "\n")
            num_registros += 1

        linea_88 = f"88{'9'*20}{str(num_registros).zfill(6)}"
        f.write(linea_88[:80] + "\n")

class ConfigApp:
    def __init__(self, master, config):
        self.master = tk.Toplevel(master)
        self.master.title("Configuración avanzada")
        self.config = config
        self.build_ui()

    def build_ui(self):
        row = 0
        fields = [
            ("Separador CSV:", 'sep'),
            ("Entidad:", 'entidad'),
            ("Oficina:", 'oficina'),
            ("Cuenta:", 'cuenta'),
            ("Nombre empresa:", 'nombre_empresa')
        ]
        for label, key in fields:
            tk.Label(self.master, text=label).grid(row=row, column=0, sticky='e')
            entry = tk.Entry(self.master)
            entry.insert(0, self.config.get(key, ''))
            entry.grid(row=row, column=1, columnspan=2, sticky='we')
            setattr(self, f"entry_{key}", entry)
            row += 1

        tk.Button(self.master, text="Seleccionar CSV y cargar columnas", command=self.cargar_columnas).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        self.combo_fecha = ttk.Combobox(self.master, state='readonly')
        self.combo_concepto = ttk.Combobox(self.master, state='readonly')
        self.combo_importe = ttk.Combobox(self.master, state='readonly')

        tk.Label(self.master, text="Columna Fecha:").grid(row=row, column=0, sticky='e')
        self.combo_fecha.grid(row=row, column=1, columnspan=2, sticky='we')
        row += 1
        tk.Label(self.master, text="Columna Concepto:").grid(row=row, column=0, sticky='e')
        self.combo_concepto.grid(row=row, column=1, columnspan=2, sticky='we')
        row += 1
        tk.Label(self.master, text="Columna Importe:").grid(row=row, column=0, sticky='e')
        self.combo_importe.grid(row=row, column=1, columnspan=2, sticky='we')
        row += 1

        tk.Button(self.master, text="Guardar configuración", command=self.guardar).grid(row=row, column=0, columnspan=3, pady=10)

    def cargar_columnas(self):
        file_path = filedialog.askopenfilename(title="Selecciona archivo CSV", filetypes=[("CSV", "*.csv")])
        if not file_path:
            return
        self.config['csv_file'] = file_path
        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self.entry_sep.get())
                headers = [h.strip() for h in reader.fieldnames]
                for combo in [self.combo_fecha, self.combo_concepto, self.combo_importe]:
                    combo['values'] = headers
                    if headers:
                        combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron leer las columnas:\n{e}")

    def guardar(self):
        self.config['sep'] = self.entry_sep.get()
        self.config['entidad'] = self.entry_entidad.get()
        self.config['oficina'] = self.entry_oficina.get()
        self.config['cuenta'] = self.entry_cuenta.get()
        self.config['nombre_empresa'] = self.entry_nombre_empresa.get()
        self.config['campo_fecha'] = self.combo_fecha.get()
        self.config['campo_concepto'] = self.combo_concepto.get()
        self.config['campo_importe'] = self.combo_importe.get()
        guardar_config(self.config)
        self.master.destroy()

def convertir_con_archivo(config):
    input_path = filedialog.askopenfilename(title="Selecciona archivo CSV", filetypes=[("CSV", "*.csv")], initialdir=config.get('last_csv_path', ''))
    if not input_path:
        return
    config['last_csv_path'] = os.path.dirname(input_path)

    output_path = filedialog.asksaveasfilename(title="Guardar archivo Norma 43", defaultextension=".txt", filetypes=[("TXT", "*.txt")], initialdir=config.get('last_output_path', ''))
    if not output_path:
        return
    config['last_output_path'] = os.path.dirname(output_path)

    try:
        generar_norma43_estandar_80(input_path, output_path, config)
        guardar_config(config)
        messagebox.showinfo("Éxito", f"Archivo generado correctamente:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al procesar:\n{e}")

if __name__ == "__main__":
    config = cargar_config()

    root = tk.Tk()
    root.title("Conversor CSV ➞ Norma 43")
    root.geometry("420x200")

    tk.Label(root, text="Conversor Norma 43", font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Seleccionar CSV y convertir", font=("Arial", 12), command=lambda: convertir_con_archivo(config)).pack(pady=10)
    tk.Button(root, text="Configuración avanzada...", command=lambda: ConfigApp(root, config)).pack(pady=5)

    root.mainloop()
