@echo off
setlocal EnableDelayedExpansion

REM Config
set APP_NAME=demo_standalone
set ICON=NONE
set DATA_DIR=data

cd /d %~dp0
set DIR=%CD%
set APP_DIR=%CD%\dist\%APP_NAME%\

REM Cleanup dist folder
rd /s /q "dist\%APP_NAME%" 2>nul
del "dist\%APP_NAME%-x64.7z" 2>nul

echo.
echo ****************************************
echo Running pyinstaller...
echo ****************************************
set PYTHONPATH=src
pyinstaller --noupx -w -n "%APP_NAME%" -i %ICON% -r "src\demos\%APP_NAME%\resources.dll" -D "src\demos\%APP_NAME%\main.py" --hidden-import webview2 --contents-directory %DATA_DIR%

echo.
echo ****************************************
echo Copying resources...
echo ****************************************
copy "src\webview2\native\win-amd64\loader.dll" "dist\%APP_NAME%\%DATA_DIR%\"

echo.
echo ****************************************
echo Optimizing dist folder...
echo ****************************************
del "dist\%APP_NAME%\%DATA_DIR%\api-ms-win-*.dll"
del "dist\%APP_NAME%\%DATA_DIR%\ucrtbase.dll"
del "dist\%APP_NAME%\%DATA_DIR%\VCRUNTIME140.dll"

del "dist\%APP_NAME%\%DATA_DIR%\select.pyd
del "dist\%APP_NAME%\%DATA_DIR%\_socket.pyd
del "dist\%APP_NAME%\%DATA_DIR%\_bz2.pyd
del "dist\%APP_NAME%\%DATA_DIR%\_lzma.pyd"

call :create_7z

:done
echo.
echo ****************************************
echo Done.
echo ****************************************
echo.
pause

endlocal
goto :eof


:create_7z
if not exist "C:\Program Files\7-Zip\" (
	echo.
	echo ****************************************
	echo 7z.exe not found at default location, omitting .7z creation...
	echo ****************************************
	exit /B
)
echo.
echo ****************************************
echo Creating .7z archives...
echo ****************************************
cd dist
set PATH=C:\Program Files\7-Zip;%PATH%
7z a "%APP_NAME%-portable-x64.7z" "%APP_NAME%\*"
cd ..
exit /B
