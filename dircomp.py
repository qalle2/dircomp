"""Compare two directories recursively."""

import getopt
import os
import sys
import time

def to_ASCII(string):
    """Replace non-7-bit ASCII characters in string with backslash codes."""

    byteString = string.encode("ascii", errors="backslashreplace")
    return byteString.decode("ascii")

def parse_arguments():
    """Parse and validate command line arguments with getopt."""

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "c")
    except getopt.GetoptError:
        sys.exit("Invalid command line argument.")

    opts = dict(opts)

    # validate number of args
    if 1 <= len(args) <= 2:
        path1 = args[0]
        path2 = args[1] if len(args) >= 2 else "."
    else:
        sys.exit("Invalid number of command line arguments.")

    # paths must exist
    for path in (path1, path2):
        if not os.path.isdir(path):
            sys.exit('Path not found: "{:s}"'.format(to_ASCII(path)))

    # paths must be different
    if os.path.samefile(path1, path2):
        sys.exit("Paths are the same.")

    # one path must not be under another
    absPaths = tuple(os.path.abspath(path) for path in (path1, path2))
    try:
        commonPath = os.path.commonpath(absPaths)
        if any(os.path.samefile(path, commonPath) for path in (path1, path2)):
            sys.exit("One path is under another.")
    except ValueError:
        pass

    return {
        "fileContents": "-c" in opts,
        "path1": path1,
        "path2": path2,
    }

def get_entries(baseDir, subDir=""):
    """Read a directory recursively.
    Return a set of entries (files and directories) without baseDir."""

    dir_ = os.path.join(baseDir, subDir)
    entries = set()

    try:
        with os.scandir(dir_) as dirIter:
            for entry in dirIter:
                subPath = os.path.join(subDir, entry.name)
                entries.add(subPath)
                if entry.is_dir():
                    entries.update(get_entries(baseDir, subPath))
    except PermissionError:
        pass

    return entries

def format_heading(text, *paths):
    """Format a heading with path names."""

    return "*** {:s} ***".format(
        text.format(*(to_ASCII(path) for path in paths))
    )

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
    return time.strftime("%Y-%m-%d %H:%M:%S", timeTuple)

def read_file(handle):
    """Generate a file in chunks."""

    bytesLeft = handle.seek(0, 2)
    handle.seek(0)

    while bytesLeft:
        chunkSize = min(bytesLeft, 2**20)
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
    """The main function."""

    if sys.version_info[0] != 3:
        print("Warning: possibly incompatible Python version.", file=sys.stderr)

    settings = parse_arguments()

    print(format_heading('Reading path "{:s}"', settings["path1"]))
    entries1 = get_entries(settings["path1"])
    print(format_heading('Reading path "{:s}"', settings["path2"]))
    entries2 = get_entries(settings["path2"])

    # common entries (entries that are in both sets)
    commonEntries = entries1 & entries2

    # common files (no directories)
    commonFiles = set(
        entry for entry in commonEntries if not any(
            os.path.isdir(os.path.join(settings[path], entry))
            for path in ("path1", "path2")
        )
    )

    # common entries of a different type (one is a file, the other a
    # directory); note: common files need not be searched
    diffTypeEntries = set(
        entry for entry in commonEntries - commonFiles
        if os.path.isdir(os.path.join(settings["path1"], entry))
        != os.path.isdir(os.path.join(settings["path2"], entry))
    )

    # common files with the same size
    try:
        sameSizeFiles = set(
            file for file in commonFiles
            if os.path.getsize(os.path.join(settings["path1"], file))
            == os.path.getsize(os.path.join(settings["path2"], file))
        )
    except OSError:
        sys.exit("Error getting file size.")

    # print entries missing from one directory
    print(format_heading(
        'Entries under "{:s}" but not under "{:s}"',
        settings["path1"], settings["path2"]
    ))
    for entry in sorted((entries1 - entries2) | diffTypeEntries):
        print(format_entry(settings["path1"], entry))
    print(format_heading(
        'Entries under "{:s}" but not under "{:s}"',
        settings["path2"], settings["path1"]
    ))
    for entry in sorted((entries2 - entries1) | diffTypeEntries):
        print(format_entry(settings["path2"], entry))

    # print files with different size
    print(format_heading(
        'Files with different size under "{:s}" vs. "{:s}"',
        settings["path1"], settings["path2"]
    ))
    try:
        for entry in sorted(commonFiles - sameSizeFiles):
            print("{:s}: {:d} vs. {:d} byte(s)".format(
                entry,
                os.path.getsize(os.path.join(settings["path1"], entry)),
                os.path.getsize(os.path.join(settings["path2"], entry))
            ))
    except OSError:
        sys.exit("Error getting file size.")

    # print files with different mtime
    print(format_heading(
        'Files with same size, different mtime under "{:s}" vs. "{:s}"',
        settings["path1"], settings["path2"]
    ))
    entries = (
        file for file in sameSizeFiles
        if os.path.getmtime(os.path.join(settings["path1"], file))
        != os.path.getmtime(os.path.join(settings["path2"], file))
    )
    try:
        for entry in sorted(entries):
            print("{:s}: {:s} vs. {:s}".format(
                entry,
                format_timestamp(settings["path1"], entry),
                format_timestamp(settings["path2"], entry)
            ))
    except OSError:
        sys.exit("Error getting file mtime.")

    if settings["fileContents"]:
        # print files with different contents
        print(format_heading(
            'Files with same size, different contents under "{:s}" vs. "{:s}"',
            settings["path1"], settings["path2"]
        ))
        entries = (
            file for file in sameSizeFiles if not are_files_identical(
                settings["path1"], settings["path2"], file
            )
        )
        for entry in sorted(entries):
            print(entry)

if __name__ == "__main__":
    main()
