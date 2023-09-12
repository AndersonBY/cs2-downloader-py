@REM @Author: Bi Ying
@REM @Date:   2023-09-12 19:18:59
@REM @Last Modified by:   Bi Ying
@REM Modified time: 2023-09-12 19:19:18
@echo off
color 6
echo Starting Counter-Strike: 2...
start "" "game\bin\win64\cs2.exe" -condebug -novid -console -insecure
timeout /t 5 /nobreak
exit