@echo off
cls
set CWD=%CD%

set INFRA_ROOT_DIR=C:/Users/Infra

cd %INFRA_ROOT_DIR%
call %INFRA_ROOT_DIR%/tools/buildsystem/infra_paths.cmd
cd %INFRA_ROOT_DIR%/modules/%1
make update_tools -B OFFLINE_MODE=y
cd %INFRA_ROOT_DIR%
call %INFRA_ROOT_DIR%/tools/buildsystem/infra_paths.cmd
cd %INFRA_ROOT_DIR%/modules/%1
for %%a in ("unit_test/module_emb/src\*") do if /i not "%%~nxa"=="%2" del "%%a"
if exist out rmdir out /q /s
@echo make clean unit_test OFFLINE_MODE=y
make clean unit_test OFFLINE_MODE=y
cd %CWD%
