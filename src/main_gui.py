# main.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config_gui import cargar_config, mostrar_configuracion
from info_gui import mostrar_informacion
from conversor import convertir_con_archivo

def iniciar_aplicacion():
    config, existe_config = cargar_config()
    app = ttk.Window(title="CSVtoN43", themename="darkly")
    app.geometry("500x250")
    app.iconbitmap("../media/icon.ico")
    app.resizable(False, False)

    # Frame superior para botones info y configuración
    top_frame = ttk.Frame(app)
    top_frame.pack(anchor="ne", pady=10, padx=10)

    btn_info = ttk.Button(top_frame, text="ℹ️", width=1, bootstyle="info-outline", command=mostrar_informacion)
    btn_info.pack(side="left", padx=5)

    btn_config = ttk.Button(top_frame, text="⚙️", width=3, bootstyle="light-outline", command=lambda: mostrar_configuracion(app, config))
    btn_config.pack(side="right")

    # Título
    ttk.Label(app, text="CSV 🔀 Norma 43", font=("Arial", 18, "bold")).pack(pady=(10, 20))

    # Botón principal grande
    btn_convertir = ttk.Button(
        app,
        text="Convertir",
        width=30,
        bootstyle="primary",
        command=lambda: convertir_con_archivo(config)
    )
    btn_convertir.pack(pady=10)

    if not existe_config:
        mostrar_configuracion(app, config)

    app.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()
