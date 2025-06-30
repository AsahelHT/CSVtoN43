# CSVtoN43

**CSVtoN43** es una aplicación de escritorio que permite convertir archivos bancarios en formato CSV a **Norma 43 (AEB43)**, el estándar español para el intercambio de extractos bancarios. También permite la conversión inversa: de Norma 43 a CSV.

## 🧩 Funcionalidad principal

- 🗃️ **Carga de archivos CSV** con información de movimientos bancarios.
- ⚙️ **Configuración interactiva de columnas** para adaptar el CSV al formato esperado (asociar campos como fecha, importe, saldo, etc.).
- 💱 **Selección de divisa** con asignación automática del código ISO 4217.
- 🧠 **Asignación automática de campos** al detectar nombres comunes como “fecha”, “importe”, “concepto”, etc.
- 🔄 **Conversión a Norma 43 (AEB43)** siguiendo el estándar oficial, con líneas 11, 22, 23, 33 y 88.
- 📤 **Generación automática de nombre de archivo** al exportar.
- 🔁 **Conversión inversa** de archivos `.txt` Norma 43 a `.csv`.

---

## 🧑‍💻 Requisitos

- Python 3.9 o superior
- Windows (soporte principal)
- Librerías: `tkinter`, `pandas`, `decimal`, `pyinstaller`, `ttkbootstrap`, ... 

Instalación de dependencias (si usas el código fuente):

```bash
pip install -r requirements.txt

