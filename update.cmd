@echo off
rem Pre-launch step: update the mods from GitHub, but never block the game if that fails
rem (GitHub down or rate-limited, no internet): the game then starts with the mods already installed.
cd /d "%~dp0"
if not defined INST_JAVA set INST_JAVA=java
if not defined PACK_URL set PACK_URL=https://raw.githubusercontent.com/Radu0120/brass-and-bullets/master/pack.toml
"%INST_JAVA%" -jar packwiz-installer-bootstrap.jar -g -s client %PACK_URL%
if errorlevel 1 echo [update] FAILED with code %errorlevel%: starting with the mods already installed
exit /b 0
