@echo off
cls
python dircomp.py test1 test2
echo.
echo === test.bat: these should cause errors ===
python dircomp.py
python dircomp.py x y
python dircomp.py .
python dircomp.py . .
