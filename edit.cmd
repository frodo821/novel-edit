@echo off
python -uc "print('@echo off')" > temp.cmd
echo "%PROGRAMFILES%\VSCode\Code.exe" %~dp0 >> temp.cmd
python -uc "print('exit')" >> temp.cmd
start /B temp.cmd
ping localhost -n 1 > nul
del temp.cmd
exit