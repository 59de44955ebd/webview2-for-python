@echo off
setlocal EnableDelayedExpansion

REM Config
set APP_NAME=demo_pyqt5
set ICON=src\demos\%APP_NAME%\resources\app.ico
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
pyinstaller --noupx -w -n "%APP_NAME%" -i "%ICON%" -D "src\demos\%APP_NAME%\main.py" --hidden-import webview2 --contents-directory %DATA_DIR%

echo.
echo ****************************************
echo Copying resources...
echo ****************************************
copy "src\webview2\native\win-amd64\loader.dll" "dist\%APP_NAME%\%DATA_DIR%\"
copy "src\demos\%APP_NAME%\main.rcc" "dist\%APP_NAME%\%DATA_DIR%\"
copy "src\demos\%APP_NAME%\main.ui" "dist\%APP_NAME%\%DATA_DIR%\"

echo.
echo ****************************************
echo Optimizing dist folder...
echo ****************************************
del "dist\%APP_NAME%\%DATA_DIR%\api-ms-win-*.dll"
del "dist\%APP_NAME%\%DATA_DIR%\ucrtbase.dll"
del "dist\%APP_NAME%\%DATA_DIR%\VCRUNTIME140.dll"
del "dist\%APP_NAME%\%DATA_DIR%\VCRUNTIME140_1.dll"

del "dist\%APP_NAME%\%DATA_DIR%\unicodedata.pyd"
del "dist\%APP_NAME%\%DATA_DIR%\libssl-3.dll"
del "dist\%APP_NAME%\%DATA_DIR%\_bz2.pyd"
del "dist\%APP_NAME%\%DATA_DIR%\_lzma.pyd"
del "dist\%APP_NAME%\%DATA_DIR%\libcrypto-3.dll"
del "dist\%APP_NAME%\%DATA_DIR%\_socket.pyd"
del "dist\%APP_NAME%\%DATA_DIR%\_ssl.pyd"

rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt5\uic"
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\translations"

rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\plugins\generic"
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\plugins\iconengines"
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\plugins\imageformats"
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\plugins\platformthemes"

del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\plugins\platforms\qminimal.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\plugins\platforms\qoffscreen.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\plugins\platforms\qwebgl.dll"

del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\d3dcompiler_47.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\libEGL.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\libGLESv2.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\opengl32sw.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\Qt5DBus.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\Qt5Network.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\Qt5Qml.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\Qt5QmlModels.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\Qt5Quick.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\Qt5Svg.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\Qt5WebSockets.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\VCRUNTIME140.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\VCRUNTIME140_1.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\MSVCP140.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt5\Qt5\bin\MSVCP140_1.dll"

::call :create_7z

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
7z a "%APP_NAME%-x64.7z" "%APP_NAME%\*"
cd ..
exit /B
