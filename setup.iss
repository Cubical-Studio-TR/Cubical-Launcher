[Setup]
AppName=CL Setup
AppVersion=1.0
AppPublisher=Cubical Studios
DefaultDirName={autopf}\CubiLauncher
DefaultGroupName=CubiLauncher
UninstallDisplayIcon={app}\icon.ico
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Output
OutputBaseFilename=CL_Setup
SetupIconFile="C:\Users\TeknoPC\Desktop\icon.ico"
DisableWelcomePage=no

[Languages]
Name: "turkish"; MessagesFile: "compiler:Default.isl"

[Messages]
turkish.WelcomeLabel1=Minecraft Launcher Kurulumuna Hoş Geldiniz
turkish.WelcomeLabel2=Bu sihirbaz, Cubical Studios tarafından geliştirilen Cubi Launcher yazılımını bilgisayarınıza kuracaktır.
turkish.WizardSelectDir=Kurulum Konumunu Seçin
turkish.SelectDirDesc=Cubi Launcher nereye kurulsun?
turkish.ButtonNext=İleri >
turkish.ButtonInstall=Kur
turkish.ButtonCancel=İptal
turkish.ButtonFinish=Bitir

[Tasks]
Name: "desktopicon"; Description: "Masaüstü simgesi oluştur"; GroupDescription: "Ek simgeler:"; Flags: unchecked

[Files]
Source: "C:\Users\TeknoPC\Desktop\Cubi Launcher (MC).exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\TeknoPC\Desktop\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Cubi Launcher"; Filename: "{app}\Cubi Launcher (MC).exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\Cubi Launcher"; Filename: "{app}\Cubi Launcher (MC).exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\Cubi Launcher (MC).exe"; Description: "Cubi Launcher'ı Başlat"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{CubiLauncher_App_ID}_is1') then
  begin
    if MsgBox('Program zaten yüklü. Dosyaları yenilemek (Reload) ister misiniz?', mbInformation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;