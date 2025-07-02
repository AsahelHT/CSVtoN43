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

def convertir_con_archivo_existente(config, csv_file, lineas_n43):
    if not os.path.isfile(csv_file):
        messagebox.showerror("Archivo no encontrado", f"No se encontró el archivo:\n{csv_file}")
        return

    cuenta_csv = "00000000000000000000"
    fecha_final = datetime.now()

    # OBTENER NOMBRE DE ARCHIVO A PARTIR DE LA CUENTA
    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=config['sep'])
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            movimientos = []

            for row in reader:
                # Leer cuenta
                if config.get('cuenta') in row:
                    cuenta_csv_raw = row[config['cuenta']].replace(' ', '').upper()

                    if cuenta_csv_raw[:2].isalpha():  # Detecta si es IBAN
                        # Quitar los 4 primeros caracteres (p.ej. ES12) => código país + dígito de control
                        cuenta_csv = cuenta_csv_raw[4:]
                    else:
                        # Cuenta nacional (CCC)
                        cuenta_csv = cuenta_csv_raw
                        

                # Leer fecha
                fecha_str = row.get(config['fecha operacion'], '')
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

    nombre_sugerido = f"AEB43_{cuenta_csv}_{fecha_final.strftime('%Y-%m')}"

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
    guardar_norma43(lineas_n43,output_file)
    
    messagebox.showinfo("Conversión completada", f"Archivo guardado en:\n{output_file}")

def guardar_norma43(lineas, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for linea in lineas:
            f.write(linea + '\n')

def generar_norma43_temp(csv_file, config):
    cuenta_csv = ''
    entidad = ''
    oficina = ''
    cuenta = ''

    movimientos = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=config['sep'])
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        # Comprobar que todos los campos necesarios existen en el CSV
        campos_necesarios = [
            config.get('fecha operacion'),
            config.get('fecha valor'),
            config.get('concepto'),
            config.get('importe'),
            config.get('saldo'),
            config.get('cuenta'),
        ]

        # Solo añadir ref1/ref2 si están asignados
        ref1 = config.get('referencia 1')
        ref2 = config.get('referencia 2')
        if ref1 and ref1 != "Sin asignar":
            campos_necesarios.append(ref1)
        if ref2 and ref2 != "Sin asignar":
            campos_necesarios.append(ref2)

        campos_faltantes = [campo for campo in campos_necesarios if campo not in reader.fieldnames]
        if campos_faltantes:
            raise Exception(f"Faltan los siguientes campos en el CSV:\n{', '.join(campos_faltantes)}")

        for row in reader:
            if config.get('cuenta') in row:
                cuenta_csv_raw = row[config['cuenta']].replace(' ', '').upper()

                if cuenta_csv_raw[:2].isalpha():  # Detecta si es IBAN
                    # Quitar los 4 primeros caracteres (p.ej. ES12) => código país + dígito de control
                    cuenta_csv = cuenta_csv_raw[4:]
                    entidad = cuenta_csv[:4]
                    oficina = cuenta_csv[4:8]
                    cuenta = cuenta_csv[10:] # Empieza en 10 para saltarse los 2 numeros de control entre oficina y n cuentas
                else:
                    # Cuenta nacional (CCC)
                    entidad = cuenta_csv_raw[:4]
                    oficina = cuenta_csv_raw[4:8] # Empieza en 10 para saltarse los 2 numeros de control entre oficina y n cuentas
                    cuenta = cuenta_csv_raw[10:]

            try:
                fecha_raw = row[config['fecha operacion']]
                fecha_valor_raw = row[config['fecha valor']]
                concepto = row[config['concepto']]
                ref1 = row.get(config['referencia 1'], '') if config['referencia 1'] != "Sin asignar" else ''
                ref2 = row.get(config['referencia 2'], '') if config['referencia 2'] != "Sin asignar" else ''
                importe_str = row[config['importe']].replace(',', '.')
                saldo_str = row[config['saldo']].replace(',', '.')

                fecha = datetime.strptime(fecha_raw, "%d/%m/%Y")
                fecha_valor = datetime.strptime(fecha_valor_raw, "%d/%m/%Y")
                importe = Decimal(importe_str)
                saldo = Decimal(saldo_str)
            except:
                continue

            movimientos.append({
                'fecha operacion': fecha,
                'fecha valor': fecha_valor,
                'concepto': concepto,
                'ref1': ref1,
                'ref2': ref2,
                'importe': importe,
                'saldo': saldo
            })

    if not movimientos:
        raise Exception("No se encontraron movimientos válidos en el archivo CSV.")

    primer_mov = movimientos[0]
    saldo_inicial = primer_mov['saldo'] - primer_mov['importe']

    saldo_tipo = '2' if saldo_inicial >= 0 else '1'
    importe_saldo = normaliza_importe(abs(saldo_inicial))
    divisa = config.get('divisa_codigo', '978')

    modalidad = '3'
    concepto_comun = '99'
    concepto_propio = '000'
    n_documento = '0000000000'

    abonos = Decimal('0.00')
    cargos = Decimal('0.00')
    nabonos = 0
    ncargos = 0

    fecha_inicio = movimientos[0]['fecha operacion'].strftime("%y%m%d")
    fecha_fin = movimientos[-1]['fecha operacion'].strftime("%y%m%d")

    lineas = []

    # Cabecera 11
    linea_11 = f"11{entidad}{oficina}{cuenta}{fecha_inicio}{fecha_fin}{saldo_tipo}{importe_saldo}{divisa}{modalidad}{formatea_texto(config['nombre_empresa'], 36)}"
    lineas.append(linea_11[:80])
    
    for mov in movimientos:
        fecha = mov['fecha operacion'].strftime("%y%m%d")
        fecha_valor = mov['fecha valor'].strftime("%y%m%d")
        importe = mov['importe']
        concepto = mov['concepto']
        ref1 = mov['ref1']
        ref2 = mov['ref2']

        if importe >= 0:
            importe_tipo = '2'
            abonos += importe
            nabonos += 1
        else:
            importe_tipo = '1'
            cargos += abs(importe)
            ncargos += 1
  
        # Comienza a construir la línea base (sin las referencias todavía)
        base_linea_22 = f"22    {oficina}{fecha}{fecha_valor}{concepto_comun}{concepto_propio}{importe_tipo}{normaliza_importe(abs(importe))}{n_documento}"

        # Calcular cuántos caracteres hay ya en la línea 22
        long_actual = len(base_linea_22)
        espacio_restante = 80 - long_actual

        linea_22 = ""
        lineas_extra = []

        if ref1 or ref2:
            if len(ref1 + ref2) <= espacio_restante:
                # Caben ambas referencias
                refs_combinadas = formatea_texto(ref1 + ref2, espacio_restante)
                linea_22 = base_linea_22 + refs_combinadas
                lineas_extra.append(f"2301{formatea_texto(concepto, 60)}"[:80])
            else:
                # Solo cabe ref1 o parte de ref1 en la línea 22
                ref1_cortada = formatea_texto(ref1, espacio_restante)
                linea_22 = base_linea_22 + ref1_cortada
                if ref2:
                    lineas_extra.append(f"2301{formatea_texto(ref2, 60)}"[:80])
                    lineas_extra.append(f"2302{formatea_texto(concepto, 60)}"[:80])
                else:
                    lineas_extra.append(f"2301{formatea_texto(concepto, 60)}"[:80])
        else:
            # No hay referencias, se rellenan con ceros
            refs_vacias = '0' * espacio_restante
            linea_22 = base_linea_22 + refs_vacias
            lineas_extra.append(f"2301{formatea_texto(concepto, 60)}"[:80])

        # Añadir las líneas finales
        lineas.append(linea_22[:80])
        lineas.extend(lineas_extra)
            
        saldo_final = mov['saldo']
        tipo_saldo_final = '2' if saldo_final >= 0 else '1'

    # Línea 33 - Totales
    linea_33 = f"33{entidad}{oficina}{cuenta}{str(ncargos).zfill(5)}{normaliza_importe(cargos)}{str(nabonos).zfill(5)}{normaliza_importe(abonos)}{tipo_saldo_final}{normaliza_importe(saldo_final)}{divisa}"
    lineas.append(linea_33[:80])
    
    # Línea 88 - Fin de fichero
    total_registros = len(lineas) 
    linea_88 = f"88{'9'*20}{str(total_registros).zfill(6)}"
    lineas.append(linea_88[:80])

    return lineas


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
