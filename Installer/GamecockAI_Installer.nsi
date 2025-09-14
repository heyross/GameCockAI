; GamecockAI Installer Script
; NSIS (Nullsoft Scriptable Install System) script for creating a Windows installer

;--------------------------------
; Include Modern UI

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

;--------------------------------
; General Definitions

!define APP_NAME "GamecockAI"
!define APP_VERSION "1.0.0"
!define PUBLISHER "Your Company"
!define WEBSITE "https://yourwebsite.com"
!define INSTALL_DIR "$PROGRAMFILES64\\${APP_NAME}"
!define UNINSTALLER "$INSTDIR\\uninstall.exe"

; Name of the installer
Name "${APP_NAME} ${APP_VERSION}"

; The file to write
OutFile "${APP_NAME}_Setup_${APP_VERSION}.exe"

; Request application privileges for Windows Vista and higher
RequestExecutionLevel admin

; Best compression
SetCompressor /SOLID lzma

; Installer icon
!define MUI_ICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-uninstall.ico"

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\\Contrib\\Graphics\\Wizard\win.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "${NSISDIR}\\Contrib\\Graphics\\Wizard\win.bmp"

;--------------------------------
; Pages

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  
  ; Add files
  File /r "..\\*.*"
  
  ; Create uninstaller
  WriteUninstaller "${UNINSTALLER}"
  
  ; Create start menu shortcuts
  CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\launcher.bat" "" "$INSTDIR\\launcher.bat" 0
  CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk" "${UNINSTALLER}" "" "${UNINSTALLER}" 0
  
  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\launcher.bat" "" "$INSTDIR\\launcher.bat" 0
  
  ; Write uninstall information to the registry
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString" "${UNINSTALLER}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "URLInfoAbout" "${WEBSITE}"
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "NoRepair" 1
  
  ; Set Python path in environment
  EnVar::SetHKCU
  EnVar::AddValue "Path" "$INSTDIR"
  
  ; Install Python if not present
  IfFileExists "$SYSDIR\\python.exe" python_found
    MessageBox MB_YESNO|MB_ICONQUESTION "Python is required but not found. Install Python 3.7 or higher now?" IDNO python_install_cancel
      ExecShell "open" "https://www.python.org/downloads/"
      Abort "Python installation is required. Please install Python and run the installer again."
    python_install_cancel:
      Abort "Python installation is required to continue."
  python_found:
  
  ; Install required Python packages
  nsExec::ExecToLog 'python -m pip install --upgrade pip'
  nsExec::ExecToLog 'python -m pip install -r "$INSTDIR\\requirements.txt"'
  
SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"
  ; Remove files and directories
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk"
  RMDir "$SMPROGRAMS\\${APP_NAME}"
  Delete "$DESKTOP\\${APP_NAME}.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"
  
  ; Remove from PATH
  EnVar::SetHKCU
  EnVar::DeleteValue "Path" "$INSTDIR"
  
SectionEnd

;--------------------------------
; Functions

Function .onInit
  ${If} ${RunningX64}
    ; 64-bit code
    SetRegView 64
  ${Else}
    ; 32-bit code
    SetRegView 32
  ${EndIf}
  
  ; Check if already installed
  ReadRegStr $R0 HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString"
  StrCmp $R0 "" done
    
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${APP_NAME} is already installed. $\\n\\nClick `OK` to remove the previous version or `Cancel` to cancel this upgrade." \
    IDOK uninst
  Abort
  
  ;Run the uninstaller
  uninst:
    ClearErrors
    ExecWait '$R0 _?=$INSTDIR' ;Do not copy the uninstaller to a temp file
    
    IfErrors no_remove_uninstaller
    ; You can either use Delete /REBOOTOK in the uninstaller or add some sort
    ; of polling in the uninstaller to wait for the uninstaller to finish
    Sleep 1000
    
  no_remove_uninstaller:
  done:
FunctionEnd
