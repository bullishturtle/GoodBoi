; GoodBoy.AI Inno Setup Installer Script
; Requires Inno Setup 6.x

#define MyAppName "GoodBoy.AI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GoodBoy.AI Team"
#define MyAppURL "https://goodboy.ai"
#define MyAppExeName "GoodBoy.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Output settings
OutputDir=..\dist
OutputBaseFilename=GoodBoy_Setup_{#MyAppVersion}
; Compression
Compression=lzma2/ultra64
SolidCompression=yes
; Visual settings
SetupIconFile=..\assets\goodboy_icon.ico
WizardStyle=modern
WizardSizePercent=120
; Privileges - per-user install by default
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (built by PyInstaller)
Source: "..\dist\GoodBoy\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Data directory structure
Source: "..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist

; Models directory (empty - user downloads models)
; We create the directory structure

[Dirs]
Name: "{app}\models"; Permissions: users-modify
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\data\memory"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Run after install (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom install logic

var
  ModelPage: TInputOptionWizardPage;
  DownloadModelCheckbox: Boolean;

procedure InitializeWizard;
begin
  // Create custom page for model selection
  ModelPage := CreateInputOptionPage(wpSelectTasks,
    'AI Model Setup', 'Configure your AI model',
    'GoodBoy.AI requires a local AI model to function. You can download one now or add it later.',
    True, False);
  
  ModelPage.Add('Download recommended model after installation (Qwen 2.5 7B, ~5GB)');
  ModelPage.Add('I will add my own GGUF model later');
  
  ModelPage.Values[1] := True; // Default to manual
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = ModelPage.ID then
  begin
    DownloadModelCheckbox := ModelPage.Values[0];
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create default config if it doesn't exist
    if not FileExists(ExpandConstant('{app}\data\GoodBoy_config.json')) then
    begin
      SaveStringToFile(
        ExpandConstant('{app}\data\GoodBoy_config.json'),
        '{' + #13#10 +
        '  "engine": "local",' + #13#10 +
        '  "model_path": "models/",' + #13#10 +
        '  "max_tokens": 512,' + #13#10 +
        '  "temperature": 0.6,' + #13#10 +
        '  "user_name": "Mayor"' + #13#10 +
        '}',
        False
      );
    end;
    
    // Note: Actual model download would require a separate downloader tool
    // as Inno Setup cannot handle large HTTP downloads reliably
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  // Check for minimum disk space (10GB recommended)
  if GetSpaceOnDisk(ExpandConstant('{app}'), True, True) < 10737418240 then
  begin
    Result := 'Warning: Less than 10GB free space. AI models require significant disk space.';
  end;
end;
