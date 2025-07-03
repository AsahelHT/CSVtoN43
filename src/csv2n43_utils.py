# csv2n43_utils.py
import sys
import os
import json
import unicodedata
import csv
import pandas as pd

from datetime import datetime
from decimal import Decimal

BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath((os.path.dirname(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, 'CSVtoN43_CFG.json')

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

ventanas_abiertas = {
    "config": None,
    "info": None,
    "preview": None,
    "root":None
}

colores = {
    'codigo':"#18B01F",
    'cuenta':"#0088ff",
    'fecha operacion': '#ff6b6b',    
    'fecha valor': '#61dafb',     
    'concepto': '#a3e635',  
    'importe': '#facc15',   
    'saldo': "#ff7c01",     
    'referencia 1': '#c084fc',      
    'referencia 2': '#c084fc',       
    'divisa':"#00ffbb",
    'tipo importe':"#00ff00",
    'contadores':"#ff0000"
}

def ruta_recurso(rel_path):
    """Devuelve la ruta absoluta a un recurso empaquetado o en desarrollo."""
    if hasattr(sys, "_MEIPASS"):  # PyInstaller
        base_path = sys._MEIPASS
    elif getattr(sys, "frozen", False):  # Nuitka standalone
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)

def guardar_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def formatea_texto(texto, longitud):
    return texto.upper().strip().ljust(longitud)[:longitud]

def normaliza_importe(importe):
    return str((Decimal(importe).quantize(Decimal("0.01")) * 100).to_integral_value()).zfill(14)

def normalizar(nombre):
    nombre = nombre.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('utf-8')
    return nombre

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
        'last_output_path': '',
        'tema':'darkly'
    }, False

def hay_campos_sin_asignar(config):
    for clave in config:
        if clave not in ("referencia 1", "referencia 2"):
            if config[clave] == "Sin asignar":
                return True
    return False

def configuracion_vacia(config):
    return not all(k in config for k in SUGERENCIAS_COLUMNAS)

def validar_estructura_csv(config, archivo):
    sep_config = config.get("sep", ";")
    columnas_esperadas = [
        config.get(k) for k in SUGERENCIAS_COLUMNAS if config.get(k) != "Sin asignar"
    ]

    if not archivo or not os.path.isfile(archivo):
        return False, "No se ha encontrado el archivo CSV configurado."

    try:
        # Leer primeras líneas del CSV
        with open(archivo, "r", encoding="utf-8") as f:
            sample = f.read(2048)
            try:
                sep_detectado = csv.Sniffer().sniff(sample).delimiter
            except:
                sep_detectado = ';' if ';' in sample else ','

        if sep_detectado != sep_config:
            return False, f"El separador detectado ('{sep_detectado}') no coincide con el configurado ('{sep_config}')."

        df = pd.read_csv(archivo, sep=sep_detectado, nrows=1)
        columnas_csv = [col.strip().lower() for col in df.columns]
        columnas_requeridas = [col.lower().strip() for col in columnas_esperadas]

        for columna in columnas_requeridas:
            if columna not in columnas_csv:
                return False, f"Falta la columna '{columna}' en el archivo CSV."

        return True, "El archivo coincide con la configuración."
    except Exception as e:
        return False, f"Error al comprobar el archivo CSV:\n{e}"
    
def mapear_colores_desde_config(config, colores):
    colores_por_columna = {}

    for campo, nombre_columna in config.items():
        if campo in ['nombre_empresa', 'sep', 'last_csv_path', 'last_csv_file', 'last_output_path']:
            continue

        if nombre_columna == 'Sin asignar' or not nombre_columna.strip():
            continue

        color = colores.get(campo, "#e0e0e0")
        colores_por_columna[normalizar(nombre_columna)] = color  # clave normalizada

    return colores_por_columna
    
ruta_icono = ruta_recurso(os.path.join("assets", "csv2n43.ico"))
show_ico_warn = True