@echo off
cls
set CWD=%CD%


set KLOCWORK_PATH=C:\Klocwork\KLOCWO~1.2CO\bin
set INFRA_ROOT_DIR=C:/Users/Infra
set TOOLS_ROOT_DIR=%INFRA_ROOT_DIR%/tools

set MODULE_NAME=Crypto

set CFG_NAME=Crypto_GoldenTargetTest
set EMBUNIT_TESTSRC=AES_128_TestSuite.c

set MODULE_LAST_TAG=V0.0.0
set MODULE_LASTLAST_TAG=V0.0.0

@rem ===============================================================================================
@rem NO Module Config beliw this line
@rem ===============================================================================================

set METRICSDIR=metrics
set OUTDIR=out
set OUTLASTDIR=outLast
set OUTLASTLASTDIR=outLastLast
set KWDIR=kw

set DELIVERY_ROOT_DIR=%INFRA_ROOT_DIR%/delivery/%MODULE_NAME%
set MODULE_ROOT_DIR=%INFRA_ROOT_DIR%/modules/%MODULE_NAME%
set MODULE_LAST_ROOT_DIR=%INFRA_ROOT_DIR%/modules/%MODULE_NAME%_Last
set MODULE_LASTLAST_ROOT_DIR=%INFRA_ROOT_DIR%/modules/%MODULE_NAME%_LastLast

set EMBUNIT_INCLUDES=-I%TOOLS_ROOT_DIR%/embunit/inc -I%TOOLS_ROOT_DIR%/embunit/inc/internal -I%TOOLS_ROOT_DIR%/embunit/inc/outputters
set MISC_INCLUDES=-I%TOOLS_ROOT_DIR%/RTE_GENERATOR/ssc/inc -I%TOOLS_ROOT_DIR%/COMMON_FILES/unit_test/platform_headers/x86_64
set FAKE_LIBC_PATH=%~dp0\..\tools\PYTHON\Lib\site-packages\pycparser_fake_libc

set KLOCWORK_PROJECT_PATH=%KWDIR%\.kwlp
set KLOCWORK_SETTINGS_PATH=%KWDIR%\.kwps
set KLOCWORK_TRACE_FILE=%KWDIR%\kwwrap.trace
set KLOCWORK_KWINJECT_FILE=%KWDIR%\kwinject.out
set KLOCWORK_KWLIST_XML_FILE=%KWDIR%\kwlist.xml
set KLOCWORK_KWLIST_CSV_FILE=%KWDIR%\kwlist.csv
set SCA_PATH=%TOOLS_ROOT_DIR%\SCA

if exist %METRICSDIR% rmdir %METRICSDIR% /q /s
mkdir %METRICSDIR%

if exist %OUTDIR% rmdir %OUTDIR% /q /s
mkdir %OUTDIR%

if exist %OUTLASTDIR% rmdir %OUTLASTDIR% /q /s
mkdir %OUTLASTDIR%

if exist %OUTLASTLASTDIR% rmdir %OUTLASTLASTDIR% /q /s
mkdir %OUTLASTLASTDIR%

if exist %KWDIR% rmdir %KWDIR% /q /s
mkdir %KWDIR%

if exist "%MODULE_LAST_ROOT_DIR%" rmdir "%MODULE_LAST_ROOT_DIR%" /q /s
mkdir "%MODULE_LAST_ROOT_DIR%"

if exist "%MODULE_LASTLAST_ROOT_DIR%" rmdir "%MODULE_LASTLAST_ROOT_DIR%" /q /s
mkdir "%MODULE_LASTLAST_ROOT_DIR%"

@echo ====================================
@echo Creating Baslines
@echo ====================================
@echo %MODULE_ROOT_DIR%...
cd %MODULE_ROOT_DIR%
git rev-parse HEAD
cd %CWD% 

@echo %MODULE_LAST_ROOT_DIR%...
xcopy /s /i /h /q "%MODULE_ROOT_DIR%" "%MODULE_LAST_ROOT_DIR%"
cd %MODULE_LAST_ROOT_DIR%
git clean -Xdf
git checkout -f -q %MODULE_LAST_TAG%
git rev-parse HEAD
cd %DELIVERY_ROOT_DIR%
git checkout -f -q %MODULE_LAST_TAG%
xcopy /s /i /h /q internal\baseline.mk "%MODULE_LAST_ROOT_DIR%"
cd %CWD%

@echo %MODULE_LASTLAST_ROOT_DIR%...
xcopy /s /i /h /q /y "%MODULE_LAST_ROOT_DIR%" "%MODULE_LASTLAST_ROOT_DIR%"
cd %MODULE_LASTLAST_ROOT_DIR%
git clean -Xdf
git checkout -f -q %MODULE_LASTLAST_TAG%
git rev-parse HEAD
cd %DELIVERY_ROOT_DIR%
git checkout -f -q %MODULE_LASTLAST_TAG%
xcopy /s /i /h /q /y internal\baseline.mk "%MODULE_LASTLAST_ROOT_DIR%"
cd %CWD% 

@echo ====================================
@echo Generating Configurations
@echo ====================================
@echo Generate.bat %MODULE_NAME%_Last %EMBUNIT_TESTSRC%
start /w cmd /C Generate.bat %MODULE_NAME%_Last %EMBUNIT_TESTSRC%
@echo Generate.bat %MODULE_NAME%_LastLast  %EMBUNIT_TESTSRC%
start /w cmd /C Generate.bat %MODULE_NAME%_LastLast %EMBUNIT_TESTSRC%
@echo install_and_update_tools
cd %INFRA_ROOT_DIR%
start /w cmd /C %INFRA_ROOT_DIR%/tools/buildsystem/install_and_update_tools.sh
cd %CWD%
@echo Generate.bat %MODULE_NAME% %EMBUNIT_TESTSRC%
start /w cmd /C Generate.bat %MODULE_NAME% %EMBUNIT_TESTSRC%

@echo ====================================
@echo Preprocessing Source Files (%MODULE_ROOT_DIR%/src)
@echo ====================================
set CFG_INCLUDES=-I%MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME% -I%MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%/extra
set MODULE_INCLUDES=-I%MODULE_ROOT_DIR%/inc -I%MODULE_ROOT_DIR%/ext/inc -I%MODULE_ROOT_DIR%/stub -I%MODULE_ROOT_DIR%/unit_test/module_emb/headers
set INCLUDES=%CFG_INCLUDES% %MODULE_INCLUDES% %EMBUNIT_INCLUDES% %MISC_INCLUDES% -I%FAKE_LIBC_PATH%
for /f %%f in ('dir /b "%MODULE_ROOT_DIR%/src"') do echo Preprocessing %%f && gcc.exe -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -E %MODULE_ROOT_DIR%/src\%%f %INCLUDES% > %OUTDIR%\%%f.pp
for /f %%f in ('dir /b "%MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%"') do if "%%~xf"==".c" echo Preprocessing %%f && gcc.exe -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -E %MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%\%%f %INCLUDES% > %OUTDIR%\%%f.pp

@echo ====================================
@echo Preprocessing Source Files (%MODULE_LAST_ROOT_DIR%/src)
@echo ====================================
set CFG_LAST_INCLUDES=-I%MODULE_LAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME% -I%MODULE_LAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%/extra
set MODULE_LAST_INCLUDES=-I%MODULE_LAST_ROOT_DIR%/inc -I%MODULE_ROOT_DIR%/ext/inc -I%MODULE_LAST_ROOT_DIR%/stub -I%MODULE_LAST_ROOT_DIR%/unit_test/module_emb/headers
set INCLUDES_LAST=%CFG_LAST_INCLUDES% %MODULE_LAST_INCLUDES% %EMBUNIT_INCLUDES% %MISC_INCLUDES% -I%FAKE_LIBC_PATH%
for /f %%f in ('dir /b "%MODULE_LAST_ROOT_DIR%/src"') do echo Preprocessing %%f && gcc.exe -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -E %MODULE_LAST_ROOT_DIR%/src\%%f %INCLUDES_LAST% > %OUTLASTDIR%\%%f.pp
for /f %%f in ('dir /b "%MODULE_LAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%"') do if "%%~xf"==".c" echo Preprocessing %%f && gcc.exe -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -E %MODULE_LAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%\%%f %INCLUDES_LAST% > %OUTLASTDIR%\%%f.pp

@echo ====================================
@echo Preprocessing Source Files (%MODULE_LASTLAST_ROOT_DIR%/src)
@echo ====================================
set CFG_LASTLAST_INCLUDES=-I%MODULE_LASTLAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME% -I%MODULE_LASTLAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%/extra
set MODULE_LASTLAST_INCLUDES=-I%MODULE_LASTLAST_ROOT_DIR%/inc -I%MODULE_ROOT_DIR%/ext/inc -I%MODULE_LASTLAST_ROOT_DIR%/stub -I%MODULE_LASTLAST_ROOT_DIR%/unit_test/module_emb/headers
set INCLUDES_LASTLAST=%CFG_LASTLAST_INCLUDES% %MODULE_LASTLAST_INCLUDES% %EMBUNIT_INCLUDES% %MISC_INCLUDES% -I%FAKE_LIBC_PATH%
for /f %%f in ('dir /b "%MODULE_LASTLAST_ROOT_DIR%/src"') do echo Preprocessing %%f && gcc.exe -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -E %MODULE_LASTLAST_ROOT_DIR%/src\%%f %INCLUDES_LASTLAST% > %OUTLASTLASTDIR%\%%f.pp
for /f %%f in ('dir /b "%MODULE_LASTLAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%"') do if "%%~xf"==".c" echo Preprocessing %%f && gcc.exe -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -E %MODULE_LASTLAST_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%\%%f %INCLUDES_LASTLAST% > %OUTLASTLASTDIR%\%%f.pp

@echo ====================================
@echo Creating Static Call Graphs
@echo ====================================
python CallGraphBuilder.py -o%METRICSDIR%\CallGraph.txt -s%OUTDIR%

@echo ====================================
@echo Calculating Lines of Code
@echo ====================================

@echo .
@rem already done in previous step

@echo ====================================
@echo Creating klocwork project
@echo ====================================
@echo . && %KLOCWORK_PATH%\kwcheck create --settings-dir %KLOCWORK_SETTINGS_PATH% --project-dir %KLOCWORK_PROJECT_PATH%
@echo . && %KLOCWORK_PATH%\kwcheck import %SCA_PATH%\config\analysis_profile.pconf -pd %KLOCWORK_PROJECT_PATH%
@echo . && %KLOCWORK_PATH%\kwcheck import %SCA_PATH%\config\metrics_all_warn.mconf -pd %KLOCWORK_PROJECT_PATH%
@echo . && %KLOCWORK_PATH%\kwcheck import %SCA_PATH%\config\Klocwork-Quality-Standard.tconf -pd %KLOCWORK_PROJECT_PATH%
@echo . && @echo additional_analysis_options=--lef-planner-in-memory > %KLOCWORK_SETTINGS_PATH%\external_config.txt
@echo . && @echo Number of parameters;FUNCTION;NOPARMS;^<0;^>=0 >> %KWDIR%\.kwps\localconfig\user_metrics.mconf
@echo . && @echo Number of accesses to global variables;FUNCTION;NOACCTOGLOB;^<0;^>=0 >> %KWDIR%\.kwps\localconfig\user_metrics.mconf

@echo ====================================
@echo Running klocwork build
@echo ====================================
set REAL_CC=%TOOLS_ROOT_DIR%\MINGW\bin\gcc.exe
set KW_CC=%KLOCWORK_PATH%\kwwrap -p -o %cd%\%KLOCWORK_TRACE_FILE% %REAL_CC%

for /f %%f in ('dir /b "%MODULE_ROOT_DIR%\src"') do echo Compiling %%f && %KW_CC% -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -c %MODULE_ROOT_DIR%\src\%%f %INCLUDES% -o %KWDIR%\%%f.o
for /f %%f in ('dir /b "%MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%"') do if "%%~xf"==".c" echo Compiling %%f && %KW_CC% -nostdinc -DCHAR_BIT=8 -D__STATIC_ANALYSIS__ -DDISABLE_TRACE_LOG -c %MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%\%%f %INCLUDES% -o %KWDIR%\%%f.o

@echo ====================================
@echo Running klocwork analysis
@echo ====================================
%KLOCWORK_PATH%\kwinject --trace-in %cd%\%KLOCWORK_TRACE_FILE% --output %KLOCWORK_KWINJECT_FILE% 
%KLOCWORK_PATH%\kwcheck run --build-spec %KLOCWORK_KWINJECT_FILE% --project-dir %KLOCWORK_PROJECT_PATH% --no-local --no-system
%KLOCWORK_PATH%\kwcheck list -F xml --project-dir %KLOCWORK_PROJECT_PATH% -report %KLOCWORK_KWLIST_XML_FILE%
%KLOCWORK_PATH%\kwcheck list -F scriptable --project-dir %KLOCWORK_PROJECT_PATH% -report %KLOCWORK_KWLIST_CSV_FILE%

@echo ====================================
@echo Collecting Complexity Metrices
@echo ====================================
python ComplexityCalculator.py -o%METRICSDIR%\Complexity.txt -i%KLOCWORK_KWLIST_CSV_FILE% -s%OUTDIR%

@echo ====================================
@echo Collecting Fluctuation Metrices
@echo ====================================
python FluctuationCalculator.py -o%METRICSDIR%\Fluctuation.txt -i%KLOCWORK_KWLIST_CSV_FILE% -s%OUTDIR%

@echo ====================================
@echo Calculating Function Weights
@echo ====================================
python FunctionWeightCalculator.py -g%METRICSDIR%\CallGraph.txt -c%METRICSDIR%\Complexity.txt -f%METRICSDIR%\Fluctuation.txt -o%METRICSDIR%\FunctionWeight.txt 

@echo .
@echo ====================================
@echo Done.

