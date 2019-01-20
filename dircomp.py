import os
import sys
import time

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
FILE_BUFFER_SIZE = 2**20

def to_ASCII(string):
    """Replace non-7-bit ASCII characters in string with backslash codes."""

    byteString = string.encode("ascii", errors = "backslashreplace")
    return byteString.decode("ascii")

def get_common_path(path1, path2):
    """Get longest common sub-path.
    Note: Paths may be absolute, relative or on different drives."""

    absPaths = (os.path.abspath(path1), os.path.abspath(path2))

    try:
        return os.path.commonpath(absPaths)
    except Exception:
        return ""

def file_error(file, msg):
    """Print an error message regarding a file or a path and exit."""

    exit('"{:s}": error: {:s}.'.format(to_ASCII(file), msg))

def parse_arguments():
    """Parse and validate command line arguments."""

    # validate number of args
    if 2 <= len(sys.argv) <= 3:
        path1 = sys.argv[1]
        path2 = sys.argv[2] if len(sys.argv) >= 3 else "."
    else:
        exit("Syntax error. See readme file for help.")

    # validate args
    if not os.path.isdir(path1):
        file_error(path1, "path not found")
    if not os.path.isdir(path2):
        file_error(path2, "path not found")
    if os.path.samefile(path1, path2):
        exit("Error: the paths are the same.")

    commonPath = get_common_path(path1, path2)
    if commonPath and (
        os.path.samefile(path1, commonPath)
        or os.path.samefile(path2, commonPath)
    ):
        exit("Error: one path is under the other one.")

    return (path1, path2)

def get_entries(baseDir, subDir = ""):
    """Read a directory recursively.
    Return a set of entries (files and directories) without baseDir."""

    dir = os.path.join(baseDir, subDir)
    entries = set()

    with os.scandir(dir) as dirIter:
        for entry in dirIter:
            subPath = os.path.join(subDir, entry.name)
            entries.add(subPath)
            if entry.is_dir():
                entries.update(get_entries(baseDir, subPath))

    return entries

def format_entry(basePath, entry):
    """Add directory separator to end of entry if the path is a directory."""

    if os.path.isdir(os.path.join(basePath, entry)):
        return os.path.join(entry, "")
    return entry

def format_timestamp(path, file):
    """Format time of last modification of a file."""

    path = os.path.join(path, file)
    timestamp = os.path.getmtime(path)
    timeTuple = time.gmtime(timestamp)
    return time.strftime(TIME_FORMAT, timeTuple)

def read_file(handle):
    """Generate a file in chunks."""

    bytesLeft = handle.seek(0, 2)
    handle.seek(0)

    while bytesLeft:
        chunkSize = min(bytesLeft, FILE_BUFFER_SIZE)
        yield handle.read(chunkSize)
        bytesLeft -= chunkSize

def are_files_identical(path1, path2, file):
    """Are the contents of the files the same?
    (The files must be the same size.)"""

    path1 = os.path.join(path1, file)
    path2 = os.path.join(path2, file)

    with open(path1, "rb") as hnd1:
        with open(path2, "rb") as hnd2:
            for (chunk1, chunk2) in zip(read_file(hnd1), read_file(hnd2)):
                if chunk1 != chunk2:
                    return False

    return True

def main():
    (path1, path2) = parse_arguments()

    print('Reading path "{:s}"...'.format(to_ASCII(path1)))
    entries1 = get_entries(path1)
    print('Reading path "{:s}"...'.format(to_ASCII(path2)))
    entries2 = get_entries(path2)
    print()

    # common entries (entries that are in both sets)
    commonEntries = entries1 & entries2

    # common files (no directories)
    commonFiles = set(
        entry for entry in commonEntries
        if not os.path.isdir(os.path.join(path1, entry))
        and not os.path.isdir(os.path.join(path2, entry))
    )

    # common entries of a different type (one is a file, the other a
    # directory); note: common files need not be searched
    commonEntriesDifferentType = set(
        entry for entry in commonEntries - commonFiles
        if os.path.isdir(os.path.join(path1, entry))
        != os.path.isdir(os.path.join(path2, entry))
    )

    # common files with the same size
    commonFilesSameSize = set(
        file for file in commonFiles
        if os.path.getsize(os.path.join(path1, file))
        == os.path.getsize(os.path.join(path2, file))
    )

    print('=== Files/directories under "{:s}" but not under "{:s}" ==='.format(
        to_ASCII(path1), to_ASCII(path2)
    ))
    print()
    entries = (entries1 - entries2) | commonEntriesDifferentType
    if entries:
        for entry in sorted(entries):
            print(format_entry(path1, entry))
        print()

    print('=== Files/directories under "{:s}" but not under "{:s}" ==='.format(
        to_ASCII(path2), to_ASCII(path1)
    ))
    print()
    entries = (entries2 - entries1) | commonEntriesDifferentType
    if entries:
        for entry in sorted(entries):
            print(format_entry(path2, entry))
        print()

    print(
        '=== Files with different size under "{:s}" vs. under "{:s}" '
        "===".format(to_ASCII(path1), to_ASCII(path2))
    )
    print()
    entries = commonFiles - commonFilesSameSize
    if entries:
        for entry in sorted(entries):
            print("{:s}: {:d} vs. {:d} byte(s)".format(
                entry,
                os.path.getsize(os.path.join(path1, entry)),
                os.path.getsize(os.path.join(path2, entry))
            ))
        print()

    print(
        "=== Files with same size but different time of last modification "
        'under "{:s}" vs. under "{:s}" ==='.format(
            to_ASCII(path1), to_ASCII(path2)
        )
    )
    print()
    entries = set(
        file for file in commonFilesSameSize
        if int(os.path.getmtime(os.path.join(path1, file)))
        != int(os.path.getmtime(os.path.join(path2, file)))
    )
    if entries:
        for entry in sorted(entries):
            print("{:s}: {:s} vs. {:s}".format(
                entry,
                format_timestamp(path1, entry),
                format_timestamp(path2, entry)
            ))
        print()

    print(
        '=== Files with same size but different contents under "{:s}" vs. '
        'under "{:s}" ==='.format(
            to_ASCII(path1), to_ASCII(path2)
        )
    )
    print()
    entries = (
        file for file in commonFilesSameSize
        if not are_files_identical(path1, path2, file)
    )
    for entry in sorted(entries):
        print(entry)

if __name__ == "__main__":
    main()
