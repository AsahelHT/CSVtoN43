# info_gui.py
import webbrowser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def mostrar_informacion():
    info_win = ttk.Toplevel()
    info_win.iconbitmap("../media/icon.ico")
    info_win.title("Información de la aplicación")
    info_win.geometry("500x400")
    info_win.resizable(False, False)

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
        "Licencia: GPL-3.0 license\n"
    )

    lbl_autor = ttk.Label(info_win, text=texto_autor, justify="center", wraplength=460)
    lbl_autor.pack(padx=20, pady=10)
