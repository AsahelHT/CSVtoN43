# conversor.py
import csv
import os
from datetime import datetime
from decimal import Decimal
from tkinter import filedialog, messagebox
from config_gui import guardar_config

def formatea_texto(texto, longitud):
    return texto.upper().strip().ljust(longitud)[:longitud]

def normaliza_importe(importe):
    return str((Decimal(importe).quantize(Decimal("0.01")) * 100).to_integral_value()).zfill(14)

def convertir_con_archivo(config):
    csv_file = filedialog.askopenfilename(title="Selecciona archivo CSV", filetypes=[("CSV", "*.csv")])
    if not csv_file:
        return

    cuenta = "00000000000000000000"
    fecha_final = datetime.now()

    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=config['sep'])
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            movimientos = []

            for row in reader:
                # Leer cuenta
                if 'campo_cuenta' in config and config['campo_cuenta'] in row:
                    cuenta_raw = row[config['campo_cuenta']]
                    cuenta = cuenta_raw.replace(' ', '').zfill(20)

                # Leer fecha
                fecha_str = row.get(config['campo_fecha'], '')
                try:
                    fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
                    movimientos.append(fecha)
                except:
                    continue

            if movimientos:
                fecha_final = max(movimientos)
    except Exception as e:
        messagebox.showerror("Error leyendo CSV", f"No se pudo analizar el archivo CSV:\n{e}")
        return

    nombre_sugerido = f"AEB43_{cuenta}_{fecha_final.strftime('%Y-%m')}"

    output_file = filedialog.asksaveasfilename(
        title="Guardar como Norma43",
        defaultextension=".txt",
        filetypes=[("TXT", "*.txt")],
        initialfile=nombre_sugerido
    )
    if not output_file:
        return

    config['last_csv_path'] = os.path.dirname(csv_file)
    config['last_output_path'] = os.path.dirname(output_file)
    guardar_config(config)

    generar_norma43_estandar_80(csv_file, output_file, config)
    messagebox.showinfo("Conversión completada", f"Archivo guardado en:\n{output_file}")


def generar_norma43_estandar_80(csv_file, output_file, config):

    cuenta_csv = ''
    entidad = ''
    oficina = ''
    cuenta = ''

    movimientos = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=config['sep'])
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:
            if 'campo_cuenta' in config and config['campo_cuenta'] in row:
                cuenta_csv = row[config['campo_cuenta']].replace(' ', '').zfill(20)
                entidad = cuenta_csv[:4]
                oficina = cuenta_csv[4:8]
                cuenta = cuenta_csv[8:]

            fecha_raw = row[config['campo_fecha']]
            valor_raw = row[config['campo_valor']]
            concepto = row[config['campo_concepto']]
            ref1 = row[config['campo_ref1']]
            ref2 = row[config['campo_ref2']]
            importe_str = row[config['campo_importe']].replace(',', '.')
            saldo_str = row[config['campo_saldo']].replace(',', '.')

            try:
                fecha = datetime.strptime(fecha_raw, "%d/%m/%Y")
                valor = datetime.strptime(valor_raw, "%d/%m/%Y")
                importe = Decimal(importe_str)
                saldo = Decimal(saldo_str)
            except:
                continue

            movimientos.append({
                'fecha': fecha,
                'valor': valor,
                'concepto': concepto,
                'importe': importe,
                'saldo': saldo
            })

    movimientos.sort(key=lambda m: m['fecha'])

    if not movimientos:
        raise Exception("No se encontraron movimientos válidos.")

    primer_mov = movimientos[0]
    saldo_inicial = primer_mov['saldo'] - primer_mov['importe']

    saldo_tipo = '2' if saldo_inicial >= 0 else '1'
    importe_saldo = normaliza_importe(abs(saldo_inicial))
    divisa = config.get('divisa_codigo', '978')

    modalidad = '3'
    concepto_comun = ''
    concepto_propio = '000'
    n_documento = '0000000000'

    abonos = Decimal('0.00')
    cargos = Decimal('0.00')
    nabonos = 0
    ncargos = 0

    fecha_inicio = movimientos[0]['fecha'].strftime("%y%m%d")
    fecha_fin = movimientos[-1]['fecha'].strftime("%y%m%d")

    with open(output_file, 'w', encoding='utf-8') as f:
        linea_11 = f"11{entidad}{oficina}{cuenta}{fecha_inicio}{fecha_fin}{saldo_tipo}{importe_saldo}{divisa}{modalidad}{formatea_texto(config['nombre_empresa'], 36)}"
        f.write(linea_11[:80] + "\n")
        num_registros = 1

        for mov in movimientos:
            fecha = mov['fecha'].strftime("%y%m%d")
            valor = mov['valor'].strftime("%y%m%d")
            importe = mov['importe']
            concepto = mov['concepto']


            if importe >= 0:
                importe_tipo = '2'
                abonos += importe 
                nabonos += 1
            else:
                importe_tipo = '1' 
                cargos += abs(importe)
                ncargos += 1

            linea_22 = f"22    {oficina}{fecha}{valor}{concepto_comun}{concepto_propio}{importe_tipo}{normaliza_importe(abs(importe))}{n_documento}{formatea_texto(concepto, 60)}"
            f.write(linea_22[:80] + "\n")
            num_registros += 1

            if ref1:
                f.write(f"2301{formatea_texto(ref1, 60)}"[:80] + "\n")
            else:
                f.write(f"2301{formatea_texto(concepto, 60)}"[:80] + "\n")

            num_registros += 1

            if ref2:
                f.write(f"2302{formatea_texto(ref2, 60)}"[:80] + "\n")
                num_registros += 1

            saldo_final = mov['saldo']
            tipo_saldo_final = '2' if saldo_final >= 0 else '1'

        linea_33 = f"33{entidad}{oficina}{cuenta}{str(ncargos).zfill(5)}{normaliza_importe(cargos)}{str(nabonos).zfill(5)}{normaliza_importe(abonos)}{tipo_saldo_final}{normaliza_importe(saldo_final)}{divisa}"
        f.write(linea_33[:80] + "\n")

        num_registros += 1
        linea_88 = f"88{'9'*20}{str(num_registros).zfill(6)}"
        f.write(linea_88[:80] + "\n")

def interfaz_convertir_n43_a_csv():
    input_file = filedialog.askopenfilename(title="Selecciona archivo Norma43", filetypes=[("TXT", "*.txt")])
    if not input_file:
        return

    output_file = filedialog.asksaveasfilename(title="Guardar como CSV", defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if not output_file:
        return

    try:
        convertir_n43_a_csv(input_file, output_file)
        messagebox.showinfo("Conversión completada", f"Archivo CSV guardado en:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def convertir_n43_a_csv(input_file, output_file):
    movimientos = []
    cuenta = ""
    fecha_operacion = ""
    fecha_valor = ""
    concepto = ""
    importe = Decimal('0.00')

    with open(input_file, 'r', encoding='utf-8') as f:
        for linea in f:
            if linea.startswith("22"):
                cuenta = linea[2:20]
                fecha_operacion = linea[20:28]
                fecha_valor = linea[28:36]
                num_abonos = int(linea[52:56])
                imp_abonos = Decimal(linea[56:66]) / 100
                num_cargos = int(linea[66:70])
                imp_cargos = Decimal(linea[70:80]) / 100
                importe = imp_abonos - imp_cargos
            elif linea.startswith("23"):
                concepto = linea[4:64].strip()
            elif linea.startswith("24"):
                movimientos.append({
                    'CUENTA': cuenta,
                    'FECHA OPERACION': datetime.strptime(fecha_operacion, "%Y%m%d").strftime("%d/%m/%Y"),
                    'FECHA VALOR': datetime.strptime(fecha_valor, "%Y%m%d").strftime("%d/%m/%Y"),
                    'CONCEPTO': concepto,
                    'IMPORTE': f"{importe:.2f}".replace('.', ',')
                })

    fieldnames = ['CUENTA', 'FECHA OPERACION', 'FECHA VALOR', 'CONCEPTO', 'IMPORTE']
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for m in movimientos:
            writer.writerow(m)
