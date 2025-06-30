#info_gui.py
import webbrowser
import tkinter as tk

def mostrar_informacion():
    info_win = tk.Toplevel()
    info_win.title("Información de la aplicación")
    info_win.geometry("500x300")

    texto = (
        "N43 Converter es una herramienta para convertir extractos bancarios en formato CSV\n"
        "a archivos compatibles con la Norma 43 del estándar bancario español.\n\n"
        "Puedes configurar fácilmente los campos, seleccionar la divisa y generar\n"
        "archivos en formato AEB43 (Norma53) compatibles con sistemas contables.\n"
    )

    lbl = tk.Label(info_win, text=texto, justify="left", wraplength=450)
    lbl.pack(padx=10, pady=10)

    def abrir_link():
        webbrowser.open("https://github.com/AsahelHT/N43_Converter")

    btn_link = tk.Button(info_win,font=("Arial", 12), text="📎 Ir al repositorio Github", command=abrir_link)
    btn_link.pack(pady=10)

    texto = (
        "Autor: Asahel Hernández Torné\n"
        "Contacto: asahel.dev@gmai.com\n"
        "Licencia: GPL-3.0 license\n"
    )

    lbl = tk.Label(info_win, text=texto, justify="left", wraplength=450)
    lbl.pack(padx=10, pady=10)