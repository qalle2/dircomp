"""Compare files and subdirectories under two directories recursively."""

import argparse
import os
import sys

def parse_arguments():
    """Parse and validate command line arguments with argparse."""

    parser = argparse.ArgumentParser(
        description="Compare files and subdirectories under two directories recursively.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-c", "--compare-contents", action="store_true",
        help="Compare the contents of the files (may take a long time)."
    )
    parser.add_argument(
        "-m", "--mtime-tolerance", type=int, default=0,
        help="Consider times of last modification the same if the absolute value of their "
        "difference in seconds does not exceed this."
    )
    parser.add_argument("path", nargs=2, help="Two paths separated by a space.")

    args = parser.parse_args()

    if not all(os.path.isdir(path) for path in args.path):
        sys.exit("One of the paths does not exist or is not a directory.")

    absPaths = tuple(os.path.abspath(path) for path in args.path)
    try:
        commonPath = os.path.commonpath(absPaths)
        if any(os.path.samefile(path, commonPath) for path in args.path):
            sys.exit("One of the paths is under the other.")
    except ValueError:
        pass

    return args

def get_entries(baseDir, subDir=""):
    """Read a directory recursively. Return a dict of files and directories without baseDir.
    Value: is the entry a directory."""

    dir_ = os.path.join(baseDir, subDir)
    entries = {}
    try:
        with os.scandir(dir_) as dirIter:
            for entry in dirIter:
                subPath = os.path.join(subDir, entry.name)
                isDir = entry.is_dir()
                entries[subPath] = isDir
                if isDir:
                    entries.update(get_entries(baseDir, subPath))
    except PermissionError:
        print('Warning: no permission: "{:s}"'.format(dir_), file=sys.stderr)
    return entries

def to_ASCII(string_):
    """Replace non-ASCII characters with backslash codes."""

    return string_.encode("ascii", errors="backslashreplace").decode("ascii")

def format_heading(text, *paths):
    """Format a heading with a path name."""

    return "*** " + text.format(*('"' + to_ASCII(path) + '"' for path in paths)) + " ***"

def format_entry(basePath, entry):
    """Add a directory separator to end of the entry if it is a directory."""

    return os.path.join(entry, "") if os.path.isdir(os.path.join(basePath, entry)) else entry

def read_file(handle):
    """Read a file. Yield one chunk per call."""

    bytesLeft = handle.seek(0, 2)
    handle.seek(0)
    while bytesLeft:
        chunkSize = min(bytesLeft, 2 ** 20)
        yield handle.read(chunkSize)
        bytesLeft -= chunkSize

def are_files_identical(basePaths, subPath):
    """Are the contents of the files the same? (The files must be the same size.)"""

    paths = tuple(os.path.join(basePath, subPath) for basePath in basePaths)

    with open(paths[0], "rb") as handle1, open(paths[1], "rb") as handle2:
        return all(
            chunk1 == chunk2 for (chunk1, chunk2) in zip(read_file(handle1), read_file(handle2))
        )

def main():
    """The main function."""

    settings = parse_arguments()

    # get entries (dicts)
    entries = []
    for path in settings.path:
        print(format_heading("Reading path {:s}", path))
        entries.append(get_entries(path))

    # get entries under both paths
    commonEntries = set(entries[0]) & set(entries[1])

    # print entries only under one path
    diffTypeEntries = set(e for e in commonEntries if entries[0][e] != entries[1][e])
    for i in range(2):
        print(format_heading("Entries only under {:s}", settings.path[i]))
        for entry in sorted((set(entries[i]) - set(entries[1-i])) | diffTypeEntries):
            print(format_entry(settings.path[i], entry))

    # print files with the same size
    commonFiles = set(e for e in commonEntries if not (entries[0][e] or entries[1][e]))
    sameSizeFiles = set(
        file for file in commonFiles
        if len(set(os.path.getsize(os.path.join(base, file)) for base in settings.path)) == 1
    )

    print(format_heading("Files with different size"))
    for entry in sorted(commonFiles - sameSizeFiles):
        print(entry)

    print(format_heading("Files with same size, different time of last modification"))
    diffMtimeFiles = (
        file for file in sameSizeFiles if abs(
            os.path.getmtime(os.path.join(settings.path[0], file))
            - os.path.getmtime(os.path.join(settings.path[1], file))
        ) > settings.mtime_tolerance
    )
    for entry in sorted(diffMtimeFiles):
        print(entry)

    if settings.compare_contents:
        print(format_heading("Files with same size, different contents"))
        diffContFiles = (
            file for file in sameSizeFiles if not are_files_identical(settings.path, file)
        )
        for entry in sorted(diffContFiles):
            print(entry)

if __name__ == "__main__":
    main()
