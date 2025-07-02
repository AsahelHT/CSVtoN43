[Setup]
AppName=CSVtoN43
AppVersion=1.0
DefaultDirName={pf}\CSVtoN43
DefaultGroupName=CSVtoN43
OutputDir=.\instalador
OutputBaseFilename=CSVtoN43_Instalador
Compression=lzma
SolidCompression=yes
DisableDirPage=no
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=media\csv2n43.ico

[Files]
; Copiar los archivos generados por pyinstaller
Source: "src\dist\CSVtoN43\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
; Incluir el icono en el directorio de instalación (opcional, si lo necesitas dentro)
Source: "media\csv2n43.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CSVtoN43"; Filename: "{app}\CSVtoN43.exe"; IconFilename: "{app}\csv2n43.ico"
Name: "{group}\Desinstalar CSVtoN43"; Filename: "{uninstallexe}"
Name: "{commondesktop}\CSVtoN43"; Filename: "{app}\CSVtoN43.exe"; IconFilename: "{app}\csv2n43.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un icono en el escritorio"; GroupDescription: "Opciones adicionales:"; Flags: unchecked

[Run]
Filename: "{app}\CSVtoN43.exe"; Description: "Ejecutar CSVtoN43"; Flags: nowait postinstall skipifsilent
