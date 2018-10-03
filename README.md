# dircomp
Compares files under two directories (non-recursively at the moment).
Developed with Python 3 under 64-bit Windows.

## Example

```
=== Files under "test1" but not under "test2" ===

"b.txt": size 4, last modified 2018-10-03 21:27:57

=== Files under "test2" but not under "test1" ===

"c.txt": size 4, last modified 2018-10-03 21:28:02

=== Files with the same name but the one under "test1" is larger ===

"test1\h.txt": size 5, last modified 2018-10-03 22:03:32
"test2\h.txt": size 4, last modified 2018-10-03 22:03:37

=== Files with the same name but the one under "test2" is larger ===

"test1\d.txt": size 4, last modified 2018-10-03 21:37:04
"test2\d.txt": size 5, last modified 2018-10-03 21:37:07

=== Files with the same name and size but the one under "test1" is newer ===

"test1\e.txt": size 4, last modified 2018-10-03 21:59:04
"test2\e.txt": size 4, last modified 2018-10-03 21:58:56

"test1\f.txt": size 4, last modified 2018-10-03 21:59:55
"test2\f.txt": size 4, last modified 2018-10-03 21:59:52

=== Files with the same name and size but the one under "test2" is newer ===

"test1\g.txt": size 4, last modified 2018-10-03 22:00:24
"test2\g.txt": size 4, last modified 2018-10-03 22:00:26
```
