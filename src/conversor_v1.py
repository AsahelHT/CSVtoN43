import csv
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox

def normaliza_importe(importe):
    return str((Decimal(importe).quantize(Decimal("0.01")) * 100).to_integral_value()).zfill(10)

def formatea_texto(texto, longitud):
    return texto.upper().strip().ljust(longitud)[:longitud]

def generar_norma43_estandar_80(csv_file, output_file, entidad, oficina, cuenta, nombre_empresa):
    movimientos_por_fecha = defaultdict(list)

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:
            fecha = datetime.strptime(row['FECHA OPERACION'], "%d/%m/%Y").strftime("%Y%m%d")
            concepto = row['CONCEPTO']
            importe = Decimal(row['IMPORTE'].replace(',', '.'))
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
                linea_23 = f"23{'01'}{formatea_texto(f'LIQ. OP. N {total_movimientos:08d}', 60)}"
                f.write(linea_23[:80] + "\n")
                linea_24 = f"24{formatea_texto(concepto, 160)}"
                f.write(linea_24[:80] + "\n")
                num_registros += 2

            linea_33 = f"33{entidad}{oficina}{cuenta}{'0'*24}{str(nabonos).zfill(4)}{normaliza_importe(abonos)}{str(ncargos).zfill(4)}{normaliza_importe(cargos)}978"
            f.write(linea_33[:80] + "\n")
            num_registros += 1

        linea_88 = f"88{'9'*20}{str(num_registros).zfill(6)}"
        f.write(linea_88[:80] + "\n")

def seleccionar_archivos_y_convertir():
    input_path = filedialog.askopenfilename(
        title="Selecciona archivo CSV de entrada",
        filetypes=[("CSV files", "*.csv")]
    )
    if not input_path:
        return

    output_path = filedialog.asksaveasfilename(
        title="Guardar archivo Norma 43 como...",
        defaultextension=".txt",
        filetypes=[("TXT files", "*.txt")]
    )
    if not output_path:
        return

    # Aquí defines los datos fijos del cliente o empresa
    entidad = "0128"
    oficina = "0532"
    cuenta = "0100101463"
    nombre_empresa = "Mi Empresa SL"

    try:
        generar_norma43_estandar_80(input_path, output_path, entidad, oficina, cuenta, nombre_empresa)
        messagebox.showinfo("Conversión completada", f"Archivo generado correctamente:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo completar la conversión:\n{e}")

# Interfaz con Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Conversor CSV a Norma 43")
    root.geometry("400x150")
    root.resizable(False, False)

    label = tk.Label(root, text="Conversor Norma 43 - CSV ➜ TXT", font=("Arial", 14))
    label.pack(pady=20)

    boton = tk.Button(root, text="Seleccionar CSV y convertir", command=seleccionar_archivos_y_convertir, font=("Arial", 12))
    boton.pack(pady=10)

    root.mainloop()
