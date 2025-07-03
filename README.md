
# CSVtoN43

**CSVtoN43** es una aplicación de escritorio desarrollada en Python que permite convertir archivos bancarios en formato CSV a **Norma 43 (AEB43)**, el estándar español para el intercambio de extractos bancarios entre empresas y entidades financieras.

---

## 🧩 Funcionalidad principal

- 🗃️ **Carga de archivos CSV** con información de movimientos bancarios.
- ⚙️ **Configuración interactiva de columnas** para adaptar el CSV al formato esperado (asociar campos como fecha operación, concepto, importe, saldo, etc.).
- 💱 **Selección de divisa** con asignación automática del código ISO 4217.
- 🧠 **Asignación automática de campos** al detectar nombres comunes como “fecha”, “importe”, “concepto”, etc.
- 🎨 **Previsualización interactiva** del resultado con **colores identificativos** que muestran claramente la relación entre campos del CSV y el archivo generado en Norma 43.
- 🔄 **Conversión a Norma 43 (AEB43)** siguiendo el estándar oficial de forma precisa y validada.
- 📤 **Generación automática del nombre del archivo** exportado, evitando sobrescrituras y errores.
- 💾 **Soporte para múltiples tipos de CSV**, incluyendo distintos separadores, codificaciones y estructuras.
- 🧪 **Etapa de validación** para detectar errores en los datos antes de la exportación.
- 🌙 **Cambio de tema**: entre tema oscuro o tema claro para mejor visualización.

---

## 📁 Estructura del proyecto

```text
CSVtoN43/
├── src/           
│   ├── assets/                     # Recursos gráficos como iconos, logotipos, etc.
│   │   └── csv2n43.ico             # Icono de la aplicación para PyInstaller.                 
│   ├── CSVtoN43_CFG.json           # Configuración base utilizada si no hay ajustes previos del usuario.
│   ├── converter.py                # Lógica de conversión de datos desde CSV a Norma 43.
│   ├── CSVtoN43.py                 # Interfaz principal de la aplicación con tkinter y ttkbootstrap.
│   ├── preview_gui.py              # Ventana de previsualización con coloreado y comparación de datos.
│   ├── config_gui.py               # Ventana de configuración de columnas y campos del CSV.
│   ├── app.py                      # Funciones auxiliares para manejo de fechas, nombres, formatos, etc.
│   └── requirements.txt            # Librerías necesarias para ejecutar el proyecto.
└──README.md                        # Este archivo.
```

## 📖 Manual de usuario

### 1. Cargar un archivo CSV
Al iniciar la aplicación, pulsa **“EMPEZAR”** y selecciona tu fichero de movimientos bancarios. 
Puede accerderse a la ventana de configuración mediante el botón **⚙️** y a la información de la app mediante el botón **ℹ️**.

- Interfaz principal
  ![pantalla principal](images/main_wd.png)

### 2. Configurar campos
La primera vez, se abrirá automáticamente la **ventana de configuración**, donde deberás seleccionar un fichero CSV como plantilla.
De este fichero CSV se realizará automáticamente:
- Asignar cada columna del CSV a su campo correspondiente (fecha, importe, concepto…).
- Confirmar el tipo de separador (coma, punto y coma, etc.) si no se detecta automáticamente.

💡 *Si el CSV incluye nombres estándar como `fecha`, `importe`, `concepto`, se asignarán automáticamente.*

En esta ventana también puede modificarse la plantilla usada, abriendo el editor que el sistema tenga establecido por defecto para ficheros .csv, o cambiar la plantilla por otro fichero deseado.

- Vista de configuración de campos  
  ![configuración](images/cfg_wd.png)


### 3. Previsualizar conversión
Antes de guardar, podrás ver una **previsualización** que:
- Muestra las 7 primeras líneas del CSV original.
- Presenta las 5 primeras y 2 últimas líneas del fichero generado en Norma 43.
- Colorea los campos para facilitar la correspondencia entre ambos formatos.
- Para convertir. Pulsa **“CONVERTIR”**.

- Ejemplo de previsualización con colores  
  ![previsualización](images/prev_wd.png)

### 4. Exportar a Norma 43
Pulsa **“Guardar archivo Norma 43”** para generar el fichero compatible. El nombre se generará automáticamente y se te ofrecerá una ubicación para guardarlo.

---

## 🧑‍💻 Requisitos

- Python 3.10.8
- Sistema operativo: Windows
- Dependencias:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Compilación con Nuitka o Pyinstaller (opcional)

Si quieres generar un ejecutable `.exe` para Windows:

```bash
pyinstaller --noconsole --noconfirm --onedir --windowed --icon=../assets/csv2n43.ico --name=CSVtoN43 main_gui.py --collect-all ttkbootstrap --hidden-import=ttkbootstrap --noupx --add-data "assets/csv2n43.ico;assets"

```
```bash
python -m nuitka --standalone --enable-plugin=tk-inter --enable-plugin=tk-inter --include-package-data=numpy --include-package-data=ttkbootstrap --include-data-file=assets/csv2n43.ico=assets/csv2n43.ico --include-data-file=dist_README.md=dist_README.md  --windows-console-mode=disable --windows-icon-from-ico=assets/csv2n43.ico CSVtoN43.py                

---

## 📌 Estado del desarrollo

- ✅ Funcionalidad básica estable.
- ⚙️ Mejora continua en la usabilidad y validación.
- 🧪 Pruebas con CSV de diferentes entidades bancarias.

---



