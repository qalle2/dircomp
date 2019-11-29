@echo off
cls

echo === test.bat: don't compare file contents ===
python dircomp.py test1 test2
echo.

echo === test.bat: compare file contents ===
python dircomp.py -c test1 test2
echo.

echo === test.bat: these should all cause syntax errors ===
python dircomp.py
python dircomp.py a b c
python dircomp.py --nonexistent-arg a b
echo.

echo === test.bat: these should all cause "path not found" errors ===
python dircomp.py nonexistent1
python dircomp.py nonexistent1 nonexistent2
python dircomp.py test1 nonexistent2
echo.

echo === test.bat: these should all cause "paths are the same" errors ===
python dircomp.py .
python dircomp.py test1/..
python dircomp.py . .
python dircomp.py . test1/..
python dircomp.py test1 ./test1
echo.

echo === test.bat: these should all cause "one path is under another" errors ===
python dircomp.py test1
python dircomp.py ./test1
python dircomp.py test1 test1/..
