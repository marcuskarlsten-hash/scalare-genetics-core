[Setup]
AppName=Scalare Genetics Core
AppVersion=0.14.1
DefaultDirName={localappdata}\Programs\ScalareGenetics
DefaultGroupName=Scalare Genetics
PrivilegesRequired=lowest
OutputBaseFilename=ScalareGeneticsSetup
Compression=lzma2
SolidCompression=yes
[Files]
Source: "dist\ScalareGenetics\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\Scalare Genetics"; Filename: "{app}\ScalareGenetics.exe"
Name: "{userdesktop}\Scalare Genetics"; Filename: "{app}\ScalareGenetics.exe"
