# dircomp
```
usage: dircomp.py [-h] [-c] [-m MTIME_TOLERANCE] path path

Compare files and subdirectories under two directories recursively.

positional arguments:
  path                  Two paths separated by a space.

options:
  -h, --help            show this help message and exit
  -c, --compare-contents
                        Compare the contents of the files too.
  -m MTIME_TOLERANCE, --mtime-tolerance MTIME_TOLERANCE
                        Consider times of last modification the same if the
                        absolute value of their difference in seconds does not
                        exceed this. Default=0.
```

## Example
```
*** Reading path test1/ ***
directories: 2, files: 8
*** Reading path test2/ ***
directories: 2, files: 7
*** Entries only under test1/ ***
dir_test1_only/
dir_test1_only/dir/
dir_test1_only/dir/file
dir_test1_only/file
file_or_dir
file_test1_only
*** Entries only under test2/ ***
dir_test2_only/
dir_test2_only/file
file_or_dir/
file_or_dir/file
file_test2_only
*** Files with different size ***
file_different_size
*** Files with same size, different time of last modification ***
*** Files with same size, different contents ***
file_different_contents
```
