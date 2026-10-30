@echo off
"%~dp0venv\Scripts\pyinstaller.exe" ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --noconsole ^
  --name VoivoClipNC ^
  --icon "%~dp0image\application.ico" ^
  --version-file "%~dp0version_info.txt" ^
  --add-data "%~dp0image:image" ^
  --specpath "%~dp0build" ^
  "%~dp0application.py"
