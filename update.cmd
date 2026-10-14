@echo off
rem Pre-launch step: update the mods from GitHub, but never block the game if that fails
rem (GitHub down or rate-limited, no internet): the game then starts with the mods already installed.
rem A first install fetches ~130 files in parallel and a few of them time out, so a failed run is retried
rem (the installer only re-downloads what is still missing, so a retry is quick).
cd /d "%~dp0"
if not defined INST_JAVA set INST_JAVA=java
if not defined PACK_URL set PACK_URL=https://raw.githubusercontent.com/Radu0120/brass-and-bullets/master/pack.toml
set TRIES=0
:again
set /a TRIES+=1
"%INST_JAVA%" -jar packwiz-installer-bootstrap.jar -g -s client %PACK_URL%
if not errorlevel 1 exit /b 0
if %TRIES% GEQ 5 goto giveup
echo [update] attempt %TRIES% failed, retrying in a few seconds
ping -n 6 127.0.0.1 >nul
goto again
:giveup
echo [update] FAILED after %TRIES% attempts: starting with the mods already installed
exit /b 0