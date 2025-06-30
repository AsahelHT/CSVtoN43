# configuracion.py
import os
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