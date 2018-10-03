import os
import sys
import time

HELP_TEXT = """\
Directory compare by Kalle (http://qalle.net)

Compare files under two directories (non-recursively).
Times of last modification are in UTC.
Note: does not compare actual contents of files.
Command line arguments: path1 path2\
"""

def to_ASCII(string):
    """Replace non-7-bit ASCII characters in string with backslash codes."""

    byteString = string.encode("ascii", errors = "backslashreplace")
    return byteString.decode("ascii")

def get_files(path):
    """Get list of files under path.
    return: {filename: os.stat_result, ...}"""

    files = {}
    with os.scandir(path) as dirIter:
        for entry in dirIter:
            if entry.is_file():
                files[entry.name] = os.stat(entry)
    return files

def sort_case_insensitively(iterable):
    """Return a list sorted case-insensitively."""

    sortedList = sorted(iterable)
    sortedList.sort(key = lambda name: name.lower())
    return sortedList

def print_file_info(filename, fileInfo, dir = None):
    """Print filename with path, size and time of last modification.
    fileInfo: os.stat_result"""

    if dir is not None:
        filename = os.path.join(dir, filename)
    size = fileInfo.st_size
    mtime = time.gmtime(fileInfo.st_mtime)
    mtimeStr = time.strftime("%Y-%m-%d %H:%M:%S", mtime)
    print('"{:s}": size {:d}, last modified {:s}'.format(
        to_ASCII(filename), size, mtimeStr
    ))

def print_file_list(files, fileInfo):
    for file in sort_case_insensitively(files):
        print_file_info(file, fileInfo[file])

def print_file_pair_list(files, fileInfo1, fileInfo2, path1, path2):
    for file in sort_case_insensitively(files):
        print_file_info(file, fileInfo1[file], path1)
        print_file_info(file, fileInfo2[file], path2)
        print()

def main():
    # validate number of args
    if len(sys.argv) != 3:
        exit(HELP_TEXT)

    # get args
    (path1, path2) = sys.argv[1:]

    # validate args
    if not os.path.isdir(path1):
        exit("Error: path1 not found.")
    if not os.path.isdir(path2):
        exit("Error: path2 not found.")
    if os.path.samefile(path1, path2):
        exit("Error: paths are the same.")

    files1 = get_files(path1)
    files2 = get_files(path2)

    print('=== Files under "{:s}" but not under "{:s}" ==='.format(
        to_ASCII(path1), to_ASCII(path2)
    ))
    print()
    print_file_list(set(files1) - set(files2), files1)
    print()

    print('=== Files under "{:s}" but not under "{:s}" ==='.format(
        to_ASCII(path2), to_ASCII(path1)
    ))
    print()
    print_file_list(set(files2) - set(files1), files2)
    print()

    sameName = set(files1) & set(files2)

    print(
        '=== Files with the same name but the one under "{:s}" is '
        'larger ==='.format(path1)
    )
    print()
    files = (
        file for file in sameName
        if files1[file].st_size > files2[file].st_size
    )
    print_file_pair_list(files, files1, files2, path1, path2)

    print(
        '=== Files with the same name but the one under "{:s}" is '
        'larger ==='.format(path2)
    )
    print()
    files = (
        file for file in sameName
        if files1[file].st_size < files2[file].st_size
    )
    print_file_pair_list(files, files1, files2, path1, path2)

    sameNameAndSize = set(
        file for file in sameName
        if files1[file].st_size == files2[file].st_size
    )

    print(
        '=== Files with the same name and size but the one under "{:s}" is '
        'newer ==='.format(path1)
    )
    print()
    files = (
        file for file in sameNameAndSize
        if files1[file].st_mtime > files2[file].st_mtime
    )
    print_file_pair_list(files, files1, files2, path1, path2)

    print(
        '=== Files with the same name and size but the one under "{:s}" is '
        'newer ==='.format(path2)
    )
    print()
    files = (
        file for file in sameNameAndSize
        if files1[file].st_mtime < files2[file].st_mtime
    )
    print_file_pair_list(files, files1, files2, path1, path2)

if __name__ == "__main__":
    main()
