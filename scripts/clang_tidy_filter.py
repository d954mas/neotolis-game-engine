#!/usr/bin/env python3
import subprocess
import sys


def _filter_compile_args(args):
    filtered = []
    for arg in args:
        if arg.startswith("--use-port="):
            continue
        filtered.append(arg)
    return filtered


def main():
    if len(sys.argv) < 2:
        print("clang_tidy_filter.py expects at least the clang-tidy path", file=sys.stderr)
        return 1

    tidy_exe = sys.argv[1]
    remaining = sys.argv[2:]

    if "--" in remaining:
        sep_index = remaining.index("--")
        tidy_args = remaining[:sep_index]
        compile_args = remaining[sep_index + 1 :]
    else:
        tidy_args = remaining
        compile_args = []

    sanitized_compile_args = _filter_compile_args(compile_args)

    cmd = [tidy_exe, *tidy_args]
    if sanitized_compile_args:
        cmd.extend(["--", *sanitized_compile_args])

    result = subprocess.run(cmd, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
