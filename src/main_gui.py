import tkinter as tk
from config_gui import cargar_config, mostrar_configuracion
from info_gui import mostrar_informacion
from conversor import convertir_con_archivo

def iniciar_aplicacion():
    config, existe_config = cargar_config()
    
    root = tk.Tk()
    root.title("CSVtoN43")
    root.geometry("500x250")

    # ─────────────────────────────────────────
    # Frame superior para botones alineados a la derecha
    top_frame = tk.Frame(root)
    top_frame.pack(side="top", anchor="ne", fill="x", padx=10, pady=10)

    btn_config = tk.Button(top_frame, text="⚙️", font=("Arial", 12), command=lambda: mostrar_configuracion(root, config))
    btn_config.pack(side="right", padx=5)

    # ─────────────────────────────────────────
    # Título centrado
    tk.Label(root, text="Conversor CSV a Norma 43", font=("Arial", 18)).pack(pady=0)

    # Botón principal grande
    tk.Button(
        root, 
        text="CSV → Norma43", 
        font=("Arial", 14), 
        width=20, 
        height=2,
        command=lambda: convertir_con_archivo(config)
    ).pack(pady=30)

    btn_info = tk.Button(root, text="ℹ️ Info", font=("Arial", 12), command=mostrar_informacion)
    btn_info.pack(pady=5)

    # Mostrar configuración al inicio si no existe
    if not existe_config:
        mostrar_configuracion(root, config)

    root.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()
