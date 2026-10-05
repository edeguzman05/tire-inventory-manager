[Setup]
AppId={{A53FB4C8-2170-46A3-923B-FAE8EC56B239}
AppName=Tire Inventory
AppVersion=1.0
DefaultDirName={localappdata}\Programs\Tire Inventory
DefaultGroupName=Tire Inventory

OutputDir=installer
OutputBaseFilename=TireInventorySetup

Compression=lzma2
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=lowest

UninstallDisplayName=Tire Inventory


[Files]
Source: "dist\TireInventory.exe"; \
DestDir: "{app}"; \
Flags: ignoreversion


[Icons]
Name: "{autoprograms}\Tire Inventory"; \
Filename: "{app}\TireInventory.exe"

Name: "{autodesktop}\Tire Inventory"; \
Filename: "{app}\TireInventory.exe"


[Run]
Filename: "{app}\TireInventory.exe"; \
Description: "Launch Tire Inventory"; \
Flags: nowait postinstall skipifsilent