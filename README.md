# dircomp
Compares files and subdirectories under two directories recursively.
Developed with Python 3 under 64-bit Windows.

## Command line arguments

Syntax: *path1* *path2*

### *path1*, *path2*
* two paths to compare
* the paths must be different
* one path must not be under the other one

## Example

```
Reading path "test1"...
Reading path "test2"...

=== Files/directories under "test1" but not under "test2" ===

dir_test1_only\
dir_test1_only\dir\
dir_test1_only\dir\file
dir_test1_only\file
file_or_dir
file_test1_only

=== Files/directories under "test2" but not under "test1" ===

dir_test2_only\
dir_test2_only\file
file_or_dir\
file_or_dir\file
file_test2_only

=== Files with different size under "test1" vs. under "test2" ===

file_different_size: 10 vs. 20 byte(s)

=== Files with same size but different time of last modification under "test1" vs. under "test2" ===

file_different_mtime: 2019-01-18 01:55:18 vs. 2019-01-18 01:55:28

=== Files with same size but different contents under "test1" vs. under "test2" ===

file_different_contents
```
