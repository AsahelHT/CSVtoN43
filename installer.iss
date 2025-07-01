[Setup]
AppName=CSVtoN43
AppVersion=1.0
DefaultDirName={pf}\CSVtoN43
DefaultGroupName=CSVtoN43
OutputDir=installer
OutputBaseFilename=CSVtoN43_Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "src\dist\CSVtoN43.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "media\*"; DestDir: "{app}\media"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CSVtoN43"; Filename: "{app}\CSVtoN43.exe"; WorkingDir: "{app}"
Name: "{userdesktop}\CSVtoN43"; Filename: "{app}\CSVtoN43.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Tareas adicionales:"

[Run]
Filename: "{app}\CSVtoN43.exe"; Description: "Ejecutar CSVtoN43 ahora"; Flags: postinstall skipifsilent
