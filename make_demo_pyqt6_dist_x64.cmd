@echo off
setlocal EnableDelayedExpansion

REM Config
set APP_NAME=demo_pyqt6
set ICON=src\demos\%APP_NAME%\resources\app.ico
set DATA_DIR=data

cd /d %~dp0
set DIR=%CD%
set APP_DIR=%CD%\dist\%APP_NAME%\

REM Cleanup dist folder
rd /s /q "dist\%APP_NAME%" 2>nul
del "dist\%APP_NAME%-x64.7z" 2>nul

REM "Compile" winapp contants and functions
cd src
python _compile_const.py
python _compile_dlls.py
ren webview2\winapp\const.py __const.py
ren webview2\winapp\const_c.py const.py
ren webview2\winapp\dlls.py __dlls.py
ren webview2\winapp\dlls_c.py dlls.py
cd ..

echo.
echo ****************************************
echo Running pyinstaller...
echo ****************************************
set PYTHONPATH=src
pyinstaller --noupx -w -n "%APP_NAME%" -i "%ICON%" -D "src\demos\%APP_NAME%\main.py" --hidden-import webview2 --contents-directory %DATA_DIR%

ren src\webview2\winapp\const.py const_c.py
ren src\webview2\winapp\__const.py const.py
ren src\webview2\winapp\dlls.py dlls_c.py
ren src\webview2\winapp\__dlls.py dlls.py

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
del "dist\%APP_NAME%\%DATA_DIR%\_ssl.pyd"

rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt6\uic"
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\translations"

rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\plugins\generic"
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\plugins\iconengines"
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\plugins\imageformats"

del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\MSVCP140.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\MSVCP140_1.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\MSVCP140_2.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\opengl32sw.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\Qt6Network.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\Qt6Pdf.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\Qt6Svg.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\VCRUNTIME140.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\bin\VCRUNTIME140_1.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\plugins\platforms\qminimal.dll"
del "dist\%APP_NAME%\%DATA_DIR%\PyQt6\Qt6\plugins\platforms\qoffscreen.dll"

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
