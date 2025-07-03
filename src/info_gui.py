# info_gui.py
import webbrowser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import os
from tkinter import filedialog, messagebox

from csv2n43_utils import ventanas_abiertas, ruta_icono
import csv2n43_utils as utils

def mostrar_informacion():
    # Evitar duplicados
    if ventanas_abiertas.get("info") and ventanas_abiertas["info"].winfo_exists():
        ventanas_abiertas["info"].focus()
        return

    info_win = ttk.Toplevel()
    info_win.withdraw()
    try:
        info_win.iconbitmap(ruta_icono)
    except Exception as e:
        if utils.show_ico_warn:
            messagebox.showwarning("Archivo no encontrado", "No se encontró la imagen de icono de la aplicación: csv2n43.ico")
            utils.show_ico_warn = False

    info_win.deiconify()
    info_win.title("Información de la aplicación")
    info_win.geometry("500x400")
    info_win.resizable(False, False)

    ventanas_abiertas["info"] = info_win

    texto_intro = (
        "CSVtoN43 es una herramienta para convertir extractos bancarios en formato CSV a archivos compatibles con la Norma 43 del estándar bancario español.\n"
        "\nPueden configurarse los campos a utilizar, seleccionar el tipo de divisa y generar archivos en formato AEB43 (Norma43) compatibles con sistemas contables."
    )

    lbl_intro = ttk.Label(info_win, text=texto_intro, justify="center", wraplength=460)
    lbl_intro.pack(padx=20, pady=(20, 10))

    def abrir_link():
        webbrowser.open("https://github.com/AsahelHT/CSVtoN43")

    btn_link = ttk.Button(
        info_win,
        text="📎 Ir al repositorio GitHub",
        bootstyle="info-outline",
        command=abrir_link
    )
    btn_link.pack(pady=10)

    texto_autor = (
        "Autor: Asahel Hernández Torné\n"
        "Contacto: asahel.dev@gmail.com\n"
        "\n"
        "Versión: Build v3-030725\n"
        "Python: 3.10.8\n"
        "Licencia: GPL-3.0 license\n"
    )

    lbl_autor = ttk.Label(info_win, text=texto_autor, justify="center", wraplength=460)
    lbl_autor.pack(padx=20, pady=10)
