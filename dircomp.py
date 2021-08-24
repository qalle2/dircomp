import argparse, os, sys

def parse_arguments():
    # parse command line arguments with argparse

    parser = argparse.ArgumentParser(
        description="Compare files and subdirectories under two directories recursively."
    )

    parser.add_argument(
        "-c", "--compare-contents", action="store_true",
        help="Compare the contents of the files (may take a long time)."
    )
    parser.add_argument(
        "-m", "--mtime-tolerance", type=int, default=0,
        help="Consider times of last modification the same if the absolute value of their "
        "difference in seconds does not exceed this. Default=0."
    )
    parser.add_argument("path", nargs=2, help="Two paths separated by a space.")

    args = parser.parse_args()

    if not all(os.path.isdir(path) for path in args.path):
        sys.exit("One of the paths does not exist or is not a directory.")

    absPaths = [os.path.abspath(path) for path in args.path]
    try:
        commonPath = os.path.commonpath(absPaths)
        if any(os.path.samefile(path, commonPath) for path in args.path):
            sys.exit("One of the paths is under the other.")
    except ValueError:
        pass

    return args

def get_entries(baseDir, subDir=""):
    # read a directory recursively; return: {entry_without_baseDir: is_directory, ...}

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
        print(f"Warning: no permission: {dir_}", file=sys.stderr)
    return entries

def format_entry(basePath, entry):
    # add directory separator to end of entry if it's a directory

    return os.path.join(entry, "") if os.path.isdir(os.path.join(basePath, entry)) else entry

def read_file(handle):
    # generate file in chunks

    bytesLeft = handle.seek(0, 2)
    handle.seek(0)
    while bytesLeft:
        chunkSize = min(bytesLeft, 2 ** 20)
        yield handle.read(chunkSize)
        bytesLeft -= chunkSize

def are_files_identical(basePaths, subPath):
    # are contents of files the same? (files must be same size)

    paths = tuple(os.path.join(basePath, subPath) for basePath in basePaths)

    with open(paths[0], "rb") as handle1, open(paths[1], "rb") as handle2:
        return all(
            chunks[0] == chunks[1] for chunks in zip(read_file(handle1), read_file(handle2))
        )

def main():
    args = parse_arguments()

    # get entries (dicts)
    entries = []
    for path in args.path:
        print(f"*** Reading path {path} ***")
        entries.append(get_entries(path))

    # get entries under both paths
    commonEntries = set(entries[0]) & set(entries[1])

    # print entries only under one path
    diffTypeEntries = set(e for e in commonEntries if entries[0][e] != entries[1][e])
    for i in range(2):
        print(f"*** Entries only under {args.path[i]} ***")
        for entry in sorted((set(entries[i]) - set(entries[1-i])) | diffTypeEntries):
            print(format_entry(args.path[i], entry))

    # print files with the same size
    commonFiles = set(e for e in commonEntries if not (entries[0][e] or entries[1][e]))
    sameSizeFiles = set(
        f for f in commonFiles
        if len(set(os.path.getsize(os.path.join(p, f)) for p in args.path)) == 1
    )

    print("*** Files with different size ***")
    for entry in sorted(commonFiles - sameSizeFiles):
        print(entry)

    print("*** Files with same size, different time of last modification ***")
    for entry in sorted(
        f for f in sameSizeFiles if abs(
            os.path.getmtime(os.path.join(args.path[0], f))
            - os.path.getmtime(os.path.join(args.path[1], f))
        ) > args.mtime_tolerance
    ):
        print(entry)

    if args.compare_contents:
        print("*** Files with same size, different contents ***")
        for entry in sorted(f for f in sameSizeFiles if not are_files_identical(args.path, f)):
            print(entry)

main()
