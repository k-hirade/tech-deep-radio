#!/usr/bin/env python3
"""台本の字数を数える（話者記号 `T|` `Y|` を除いた本文の文字数）。使い方: python3 scripts/count_chars.py episodes/<日付>"""
import glob
import os
import sys


def count(ep_dir):
    per_file = {}
    for path in sorted(glob.glob(os.path.join(ep_dir, "script_*.txt"))):
        with open(path, encoding="utf-8") as f:
            per_file[os.path.basename(path)] = sum(len(s.strip()) - 2 for s in f if s.strip())
    return per_file


if __name__ == "__main__":
    files = count(sys.argv[1])
    for name, n in files.items():
        print(f"{name}\t{n}")
    print(f"合計\t{sum(files.values())}")
