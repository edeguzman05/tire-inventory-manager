[Setup]
AppId=TireInventory.GarciaWheelsAndTires
AppName=Tire Inventory
AppVersion=1.0
AppPublisher=Garcia Wheels & Tires

DefaultDirName={localappdata}\Programs\Tire Inventory
DefaultGroupName=Tire Inventory

OutputDir=installer
OutputBaseFilename=TireInventorySetup

Compression=lzma2
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=lowest

UninstallDisplayName=Tire Inventory

[Tasks]
Name: "desktopicon"; \
Description: "Create a desktop shortcut"; \
GroupDescription: "Additional shortcuts:"; \
Flags: unchecked

[Files]
Source: "dist\TireInventory.exe"; \
DestDir: "{app}"; \
Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Tire Inventory"; \
Filename: "{app}\TireInventory.exe"

Name: "{autodesktop}\Tire Inventory"; \
Filename: "{app}\TireInventory.exe"; \
Tasks: desktopicon

[Run]
Filename: "{app}\TireInventory.exe"; \
Description: "Launch Tire Inventory"; \
Flags: nowait postinstall skipifsilent