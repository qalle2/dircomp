clear

echo "=== Testing ==="
echo
python3 dircomp.py test1/ test2/
echo

echo "=== These should cause four errors ==="
echo
python3 dircomp.py nonexistent1 nonexistent2 x
python3 dircomp.py nonexistent1 nonexistent2 -1
python3 dircomp.py nonexistent1 nonexistent2
python3 dircomp.py test1        nonexistent2
echo
