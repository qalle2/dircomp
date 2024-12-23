# dircomp
Compare files and subdirectories under two directories recursively.

Table of contents:
* [Command line arguments](#command-line-arguments)
* [Example](#example)

## Command line arguments
Syntax: *path1* *path2* *mTimeTolerance*
* *path1*, *path2*: the paths to read.
* *mTimeTolerance*: Consider times of last modification the same if they are within this many seconds of each other.
  * Optional.
  * Must be a nonnegative integer.
  * The default is 0.

## Example
```
@ python3 dircomp.py test1/ test2/
*** Reading paths ***
test1/: 3 directories, 8 files
test2/: 3 directories, 7 files

*** Entries only under test1/ ***
test1/dir_test1_only/
test1/dir_test1_only/dir/
test1/dir_test1_only/dir/file
test1/dir_test1_only/file
test1/file_or_dir
test1/file_test1_only

*** Entries only under test2/ ***
test2/dir_test2_only/
test2/dir_test2_only/file
test2/file_or_dir/
test2/file_or_dir/file
test2/file_test2_only

*** Files with different contents - newer under test1/ ***

*** Files with different contents - same last modification time ***
file_different_contents
file_different_size

*** Files with different contents - newer under test2/ ***

*** Files with identical contents and all common directories ***
dir_same/
file_different_mtime
file_same
```
