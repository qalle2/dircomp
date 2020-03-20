@echo off
cls

echo === test.bat: don't compare file contents ===
python dircomp.py test1 test2
echo.

echo === test.bat: compare file contents ===
python dircomp.py --compare-contents test1 test2
echo.

echo === test.bat: these cause "path not found" errors ===
python dircomp.py nonexistent1 nonexistent2
python dircomp.py test1 nonexistent2
echo.

echo === test.bat: these should all cause "one path is under another" errors ===
python dircomp.py . .
python dircomp.py test1/.. .
python dircomp.py . test1/..
python dircomp.py test1 ./test1
python dircomp.py test1 .
python dircomp.py ./test1 .
python dircomp.py test1 test1/..
echo.

echo === test.bat: help text ===
python dircomp.py --help
