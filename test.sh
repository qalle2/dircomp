clear

echo "=== Don't compare file contents ==="
echo
python3 dircomp.py test1/ test2/
echo

echo "=== Compare file contents ==="
echo
python3 dircomp.py --compare-contents test1/ test2/
echo

echo "=== These should cause two 'path not found' errors ==="
echo
python3 dircomp.py nonexistent1 nonexistent2
python3 dircomp.py test1 nonexistent2
echo

echo "=== These should cause seven 'one path is under another' errors ==="
echo
python3 dircomp.py . .
python3 dircomp.py test1/.. .
python3 dircomp.py . test1/..
python3 dircomp.py test1 ./test1
python3 dircomp.py test1 .
python3 dircomp.py ./test1 .
python3 dircomp.py test1 test1/..
echo
