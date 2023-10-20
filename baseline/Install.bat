@echo off
SET PATH=%~dp0\..\tools\PYTHON;%~dp0\..\tools\PYTHON\Scripts;%~dp0\..\tools\PYTHON\Lib;%~dp0\..\tools\PYTHON\libs;%PATH%;
echo %~dp0\..\tools\PYTHON
pip install --upgrade pip
pip install networkx
pip install matplotlib
pip install anytree
pip install pygraphviz
pip install cdifflib
