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
    path: str
    return: {filename: os.stat_result, ...}"""

    files = {}
    with os.scandir(path) as dirIter:
        for entry in dirIter:
            if entry.is_file():
                files[entry.name] = os.stat(entry)
    return files

def sort_case_insensitively(iterable):
    """Convert iterable to list and sort case-insensitively."""

    sortedList = sorted(iterable)
    sortedList.sort(key = lambda name: name.lower())
    return sortedList

def print_file_info(dir, filename, fileInfo):
    """Print filename with path, size and time of last modification.
    dir: directory (str)
    filename: str
    fileInfo: os.stat_result"""

    path = os.path.normpath(os.path.join(dir, filename))
    size = fileInfo.st_size
    mtime = time.gmtime(fileInfo.st_mtime)
    mtimeStr = time.strftime("%Y-%m-%d %H:%M:%S", mtime)
    print("{:s}: size {:d}, modified {:s}".format(to_ASCII(path), size, mtimeStr))

def main():
    # validate number of args
    if len(sys.argv) != 3:
        exit(HELP_TEXT)

    # get args
    (path1, path2) = sys.argv[1:]

    # validate args
    if not os.path.isdir(path1):
        exit("path1: not an existing directory")
    if not os.path.isdir(path2):
        exit("path2: not an existing directory")
    if os.path.samefile(path1, path2):
        exit("error: paths are the same")

    files1 = get_files(path1)
    files2 = get_files(path2)

    print("=== files under {:s} but not under {:s} ===".format(to_ASCII(path1), to_ASCII(path2)))
    for file in sort_case_insensitively(set(files1) - set(files2)):
        print_file_info(path1, file, files1[file])
    print()

    print("=== files under {:s} but not under {:s} ===".format(to_ASCII(path2), to_ASCII(path1)))
    for file in sort_case_insensitively(set(files2) - set(files1)):
        print_file_info(path2, file, files2[file])
    print()

    sameName = set()
    sameNameAndSize = set()
    sameNameAndSizeAndMtime = set()

    for filename in set(files1) & set(files2):
        file1 = files1[filename]
        file2 = files2[filename]
        if file1.st_size != file2.st_size:
            sameName.add(filename)
        elif file1.st_mtime != file2.st_mtime:
            sameNameAndSize.add(filename)
        else:
            sameNameAndSizeAndMtime.add(filename)

    print("=== same name but different size ===")
    for file in sort_case_insensitively(sameName):
        print_file_info(path1, file, files1[file])
        print_file_info(path2, file, files2[file])
    print()

    print("=== same name&size but different time of last modification ===")
    for file in sort_case_insensitively(sameNameAndSize):
        print_file_info(path1, file, files1[file])
        print_file_info(path2, file, files2[file])
    print()

    print("=== same name, size & time of last modification ===")
    for file in sort_case_insensitively(sameNameAndSizeAndMtime):
        print_file_info(path1, file, files1[file])
        print_file_info(path2, file, files2[file])

if __name__ == "__main__":
    main()
