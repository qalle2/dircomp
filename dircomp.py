# "entry" = file or directory

import os, sys

HELP_TEXT = (
    "Compare files and subdirectories under two directories recursively. "
    "Args: path1 path2 [mTimeTolerance]. See README.md for details."
)

def append_dir_separator(entry):
    # append directory separator to entry name
    return os.path.join(entry, "")

def get_entries(baseDir, subDir=""):
    # read a directory recursively;
    # generate: entries without baseDir (dirs end with directory separator)

    dir_ = os.path.join(baseDir, subDir)
    try:
        with os.scandir(dir_) as dirIter:
            for entry in dirIter:
                subPath = os.path.join(subDir, entry.name)
                if entry.is_dir():
                    yield append_dir_separator(subPath)
                    yield from get_entries(baseDir, subPath)
                else:
                    yield subPath
    except PermissionError:
        print(f"Warning: no permission: {dir_}", file=sys.stderr)
    except OSError:
        sys.exit("Error reading the directory structure.")

def is_dir_name(entry):
    # is the entry a directory (ends with the directory separator)?
    return append_dir_separator(entry) == entry

def read_file(handle):
    # generate file in chunks

    try:
        bytesLeft = handle.seek(0, 2)
        handle.seek(0)
        while bytesLeft:
            chunkSize = min(bytesLeft, 2 ** 20)
            yield handle.read(chunkSize)
            bytesLeft -= chunkSize
    except OSError:
        sys.exit("Error reading file.")

def are_files_identical(path1, path2, subPath):
    # are contents of path1/subPath and path2/subPath the same?

    path1 = os.path.join(path1, subPath)
    path2 = os.path.join(path2, subPath)
    try:
        if os.path.getsize(path1) != os.path.getsize(path2):
            return False
    except OSError:
        sys.exit("Error getting file size.")

    with open(path1, "rb") as handle1, open(path2, "rb") as handle2:
        return all(
            chunks[0] == chunks[1]
            for chunks in zip(read_file(handle1), read_file(handle2))
        )

def main():
    # parse command line arguments
    if not 3 <= len(sys.argv) <= 4:
        sys.exit(HELP_TEXT)
    paths = sys.argv[1:3]
    mTimeTolerance = sys.argv[3] if len(sys.argv) >= 4 else "0"
    #
    try:
        mTimeTolerance = int(mTimeTolerance, 10)
        if mTimeTolerance < 0:
            raise ValueError
    except ValueError:
        sys.exit("mTimeTolerance must be a nonnegative integer.")
    #
    for path in paths:
        if not os.path.isdir(path):
            sys.exit(f"Path {path} does not exist or is not a directory.")

    # get entries (dicts)
    print(f"*** Reading paths ***")
    entries = []
    for path in paths:
        entries.append(set(get_entries(path)))
        print("{}: {} directories, {} files".format(
            path,
            sum(1 for e in entries[-1] if     is_dir_name(e)),
            sum(1 for e in entries[-1] if not is_dir_name(e))
        ))
    print()

    # entries only under one path
    for i in range(2):
        print(f"*** Entries only under {paths[i]} ***")
        for entry in sorted(set(entries[i]) - set(entries[1-i])):
            print(os.path.join(paths[i], entry))
        print()

    commonFiles = set(e for e in entries[0] & entries[1] if not is_dir_name(e))
    identicalFiles = set(
        f for f in commonFiles if are_files_identical(*paths, f)
    )

    # get differences of mtimes for non-identical files
    try:
        timeDiffs = dict(
            (
                f,
                  os.path.getmtime(os.path.join(paths[1], f))
                - os.path.getmtime(os.path.join(paths[0], f))
            ) for f in commonFiles - identicalFiles
        )
    except OSError:
        sys.exit("Error getting times of last modification for files.")

    print(f"*** Files with different contents - newer under {paths[0]} ***")
    for entry in sorted(f for f in timeDiffs if timeDiffs[f] < mTimeTolerance):
        print(entry)
    print()

    print(
        "*** Files with different contents - same last modification time ***"
    )
    for entry in sorted(
        f for f in timeDiffs if abs(timeDiffs[f]) <= mTimeTolerance
    ):
        print(entry)
    print()

    print(f"*** Files with different contents - newer under {paths[1]} ***")
    for entry in sorted(f for f in timeDiffs if timeDiffs[f] > mTimeTolerance):
        print(entry)
    print()

    print("*** Files with identical contents and all common directories ***")
    commonDirs = set(e for e in entries[0] & entries[1] if is_dir_name(e))
    for entry in sorted(commonDirs | identicalFiles):
        print(entry)
    print()

main()
