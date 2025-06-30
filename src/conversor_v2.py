import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

# ---------------- UTILIDADES ----------------
def normaliza_importe(importe):
    return str((Decimal(importe).quantize(Decimal("0.01")) * 100).to_integral_value()).zfill(10)

def formatea_texto(texto, longitud):
    return texto.upper().strip().ljust(longitud)[:longitud]

# ---------------- CONVERSOR ----------------
def generar_norma43_estandar_80(csv_file, output_file, entidad, oficina, cuenta, nombre_empresa,
                                 campo_fecha, campo_concepto, campo_importe, separador):
    movimientos_por_fecha = defaultdict(list)

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=separador)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:
            fecha = datetime.strptime(row[campo_fecha], "%d/%m/%Y").strftime("%Y%m%d")
            concepto = row[campo_concepto]
            importe = Decimal(row[campo_importe].replace(',', '.'))
            movimientos_por_fecha[fecha].append((concepto, importe))

    fechas = sorted(movimientos_por_fecha.keys())
    fecha_inicio = fechas[0]
    fecha_fin = fechas[-1]
    num_registros = 0
    total_movimientos = 0

    with open(output_file, 'w', encoding='utf-8') as f:
        linea_11 = f"11{entidad}{oficina}{cuenta}{fecha_inicio[-4:]}{fecha_inicio}{fecha_fin}2000000002000009783{formatea_texto(nombre_empresa, 36)}099"
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

            linea_22 = f"22{entidad}{oficina}{cuenta}{fecha}{fecha}0111120000000000{str(nabonos).zfill(4)}{normaliza_importe(abonos)}{str(ncargos).zfill(4)}{normaliza_importe(cargos)}ORDEN PAGO RECIB "
            f.write(linea_22[:80] + "\n")
            num_registros += 1

            for concepto, importe in grupo:
                total_movimientos += 1
                # ✅ Usar concepto en línea 23
                linea_23 = f"23{'01'}{formatea_texto(concepto, 60)}"
                f.write(linea_23[:80] + "\n")
                linea_24 = f"24{formatea_texto(concepto, 160)}"
                f.write(linea_24[:80] + "\n")
                num_registros += 2

            linea_33 = f"33{entidad}{oficina}{cuenta}{'0'*24}{str(nabonos).zfill(4)}{normaliza_importe(abonos)}{str(ncargos).zfill(4)}{normaliza_importe(cargos)}978"
            f.write(linea_33[:80] + "\n")
            num_registros += 1

        linea_88 = f"88{'9'*20}{str(num_registros).zfill(6)}"
        f.write(linea_88[:80] + "\n")

# ---------------- CONFIGURACIÓN AVANZADA ----------------
class ConfigApp:
    def __init__(self, master, defaults):
        self.master = tk.Toplevel(master)
        self.master.title("Configuración avanzada")
        self.defaults = defaults

        self.sep_var = tk.StringVar(value=defaults['sep'])
        self.headers = []

        self.build_ui()

    def build_ui(self):
        tk.Label(self.master, text="Separador CSV:").grid(row=0, column=0, sticky='e')
        ttk.Combobox(self.master, textvariable=self.sep_var, values=[',', ';', '\t', '|'], width=5).grid(row=0, column=1, sticky='w')

        tk.Button(self.master, text="Cargar columnas", command=self.cargar_columnas).grid(row=0, column=2, padx=10)

        self.combo_fecha = ttk.Combobox(self.master, state='readonly')
        self.combo_concepto = ttk.Combobox(self.master, state='readonly')
        self.combo_importe = ttk.Combobox(self.master, state='readonly')

        tk.Label(self.master, text="Columna FECHA OPERACION:").grid(row=1, column=0, sticky='e')
        self.combo_fecha.grid(row=1, column=1, columnspan=2, sticky='we')

        tk.Label(self.master, text="Columna CONCEPTO:").grid(row=2, column=0, sticky='e')
        self.combo_concepto.grid(row=2, column=1, columnspan=2, sticky='we')

        tk.Label(self.master, text="Columna IMPORTE:").grid(row=3, column=0, sticky='e')
        self.combo_importe.grid(row=3, column=1, columnspan=2, sticky='we')

        tk.Button(self.master, text="Guardar configuración", command=self.guardar).grid(row=4, column=0, columnspan=3, pady=10)

    def cargar_columnas(self):
        file_path = filedialog.askopenfilename(title="Selecciona archivo CSV", filetypes=[("CSV", "*.csv")])
        if not file_path:
            return
        self.defaults['csv_file'] = file_path
        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self.sep_var.get())
                self.headers = [h.strip() for h in reader.fieldnames]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron leer las columnas:\n{e}")
            return

        for combo in [self.combo_fecha, self.combo_concepto, self.combo_importe]:
            combo['values'] = self.headers
            if self.headers:
                combo.current(0)

    def guardar(self):
        self.defaults['sep'] = self.sep_var.get()
        self.defaults['campo_fecha'] = self.combo_fecha.get()
        self.defaults['campo_concepto'] = self.combo_concepto.get()
        self.defaults['campo_importe'] = self.combo_importe.get()
        self.master.destroy()

# ---------------- VENTANA PRINCIPAL ----------------
def seleccionar_archivo_y_convertir(defaults):
    input_path = filedialog.askopenfilename(title="Selecciona archivo CSV", filetypes=[("CSV files", "*.csv")])
    if not input_path:
        return
    output_path = filedialog.asksaveasfilename(title="Guardar archivo Norma 43", defaultextension=".txt", filetypes=[("TXT", "*.txt")])
    if not output_path:
        return

    try:
        generar_norma43_estandar_80(
            csv_file=input_path,
            output_file=output_path,
            entidad="0128",
            oficina="0532",
            cuenta="0100101463",
            nombre_empresa="Mi Empresa SL",
            campo_fecha=defaults['campo_fecha'],
            campo_concepto=defaults['campo_concepto'],
            campo_importe=defaults['campo_importe'],
            separador=defaults['sep']
        )
        messagebox.showinfo("Éxito", f"Archivo generado correctamente:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al procesar:\n{e}")

# ---------------- LANZADOR ----------------
if __name__ == "__main__":
    defaults = {
        'sep': ';',
        'campo_fecha': 'FECHA OPERACION',
        'campo_concepto': 'CONCEPTO',
        'campo_importe': 'IMPORTE',
        'csv_file': ''
    }

    root = tk.Tk()
    root.title("Conversor CSV ➜ Norma 43")
    root.geometry("400x180")
    root.resizable(False, False)

    tk.Label(root, text="Conversor Norma 43", font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Seleccionar CSV y convertir", command=lambda: seleccionar_archivo_y_convertir(defaults), font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Configuración avanzada...", command=lambda: ConfigApp(root, defaults), font=("Arial", 10)).pack()

    root.mainloop()
