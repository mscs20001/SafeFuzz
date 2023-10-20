@echo off
cls
set CWD=%CD%

set BULL_BIN_PATH="C:\Program Files (x86)\BullseyeCoverage\bin"
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
set BULLDIR=bull
set TESTDIR=test
set TESTHARNESSDIR=testHarness

set MODULE_ROOT_DIR=%INFRA_ROOT_DIR%/modules/%MODULE_NAME%

set EMBUNIT_INCLUDES=-I%TOOLS_ROOT_DIR%/embunit/inc -I%TOOLS_ROOT_DIR%/embunit/inc/internal -I%TOOLS_ROOT_DIR%/embunit/inc/outputters
set MISC_INCLUDES=-I%TOOLS_ROOT_DIR%/RTE_GENERATOR/ssc/inc -I%TOOLS_ROOT_DIR%/COMMON_FILES/unit_test/platform_headers/x86_64

set COVFILE=%BULLDIR%\test.cov

if exist %METRICSDIR% rmdir %METRICSDIR% /q /s
mkdir %METRICSDIR%

if exist %BULLDIR% rmdir %BULLDIR% /q /s
mkdir %BULLDIR%

if exist %OUTDIR% rmdir %OUTDIR% /q /s
mkdir %OUTDIR%

@echo ====================================
@echo Generating Configurations
@echo ====================================
@echo install_and_update_tools
cd %INFRA_ROOT_DIR%
start /w cmd /C %INFRA_ROOT_DIR%/tools/buildsystem/install_and_update_tools.sh
cd %CWD%
@echo Generate.bat %MODULE_NAME% %EMBUNIT_TESTSRC%
start /w cmd /C Generate.bat %MODULE_NAME% %EMBUNIT_TESTSRC%

@echo ====================================
@echo Compiling Source Files (%MODULE_ROOT_DIR%/src)
@echo ====================================
%BULL_BIN_PATH%\cov01.exe --on
set CFG_INCLUDES=-I%MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME% -I%MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%/extra
set MODULE_INCLUDES=-I%MODULE_ROOT_DIR%/inc -I%MODULE_ROOT_DIR%/ext/inc -I%MODULE_ROOT_DIR%/stub -I%MODULE_ROOT_DIR%/unit_test/module_emb/headers
set INCLUDES=%CFG_INCLUDES% %MODULE_INCLUDES% %EMBUNIT_INCLUDES% %MISC_INCLUDES% -I%TESTHARNESSDIR%/inc
for /f %%f in ('dir /b "%MODULE_ROOT_DIR%/src"') do echo Compiling %%f && %BULL_BIN_PATH%\covc.exe -i --file %COVFILE% gcc.exe -g -finstrument-functions -c %MODULE_ROOT_DIR%/src\%%f %INCLUDES% -o %OUTDIR%\%%f.o
for /f %%f in ('dir /b "%MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%"') do if "%%~xf"==".c" echo Compiling %%f && %BULL_BIN_PATH%\covc.exe -i --file %COVFILE% gcc.exe -g -finstrument-functions -c %MODULE_ROOT_DIR%/out/module/gen/module_emb/%CFG_NAME%\%%f %INCLUDES% -o %OUTDIR%\%%f.o
%BULL_BIN_PATH%\cov01.exe --off

@echo ====================================
@echo Compiling Test Files (%TESTDIR%/src)
@echo ====================================
for /f %%f in ('dir /b "%TESTDIR%/src"') do echo Compiling %%f && gcc.exe %INCLUDES% -DTESSY -c %TESTDIR%/src\%%f -o %OUTDIR%\%%f.o

@echo ====================================
@echo Compiling Test Harness (%TESTHARNESSDIR%/src)
@echo ====================================
for /f %%f in ('dir /b "%TESTHARNESSDIR%/src"') do echo Compiling %%f && gcc.exe %INCLUDES% -c %TESTHARNESSDIR%/src\%%f -o %OUTDIR%\%%f.o
for /f %%f in ('dir /b "%MODULE_ROOT_DIR%/ext/src"') do if "%%~xf"==".c" echo Compiling %%f && gcc.exe %INCLUDES% -c %MODULE_ROOT_DIR%/ext/src\%%f -o %OUTDIR%\%%f.o

@echo ====================================
@echo Creating Instrumented Binaries
@echo ====================================
%BULL_BIN_PATH%\cov01.exe --on
%BULL_BIN_PATH%\covc.exe -i --file %COVFILE% gcc.exe %OUTDIR%\*.o -o %OUTDIR%\test.exe
%BULL_BIN_PATH%\cov01.exe --off

@echo ====================================
@echo Building Input Seed Dictionaries
@echo ====================================
python Executor.py -i%TESTDIR%\inputs -e%OUTDIR%\test.exe -c%COVFILE% -w.\..\baseline\metrics\FunctionWeight.txt -g.\..\baseline\metrics\CallGraph.txt --high=%OUTDIR%\high.txt --low=%OUTDIR%\low.txt --all=%OUTDIR%\all.txt

@echo ====================================
@echo Fuzz Testing Instrumented Binaries
@echo ====================================
for /l %%N in (1 1 5) do python Fuzz.py -e%OUTDIR%\test.exe -c%COVFILE% -w.\..\baseline\metrics\FunctionWeight.txt -g.\..\baseline\metrics\CallGraph.txt --high=%OUTDIR%\high.txt --low=%OUTDIR%\low.txt --all=%OUTDIR%\all.txt --valid=%OUTDIR%\valid.txt --hang=%OUTDIR%\hang.txt --crash=%OUTDIR%\crash.txt

@echo .
@echo ====================================
@echo Done.

