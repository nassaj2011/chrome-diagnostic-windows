#define MyAppName "Chrome Diagnostic"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Chrome Diagnostic contributors"
#define MyAppExeName "ChromeDiagnostic.exe"

[Setup]
AppId={{C98A5D6A-2EAD-45C0-963F-5E0F26F718F1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Chrome Diagnostic
DefaultGroupName=Chrome Diagnostic
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=Chrome-Diagnostic-Setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyAppName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupLogging=yes
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\ChromeDiagnostic.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Chrome Diagnostic"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Chrome Diagnostic"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Chrome Diagnostic"; Flags: nowait postinstall skipifsilent
