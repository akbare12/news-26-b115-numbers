#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261126 grader (account b115).

The grader runs in a standard-library-only environment: this module must
not import anything beyond the Python standard library, so it simply
copies the pre-rendered entry.png (produced at build time by gen.py,
which uses Pillow and is committed alongside this file) into the output
directory the grader provides through MAKEFUN_OUTPUT_DIR.

Layout V111: masthead -> hero 1 full-width with art on the right ->
DATE CHECK -> heroes 2+3 in two columns -> full-width map -> 5x2 cards
-> ALSO in 3 columns -> timeline -> footer. 50 stories, 10 regions,
Thursday 26 November 2026. The image is 1024x1024 and under 1 MiB.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    dst = os.path.join(out_dir, "entry.png")
    # The grader mounts the repo read-only, so the source file is never
    # written in place; only the copy in the output directory is produced.
    if not os.path.isfile(src):
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    size = os.path.getsize(dst)
    print("copied entry.png -> %s (%d bytes)" % (dst, size))
    # The bounty caps the entry at 1024x1024 px and 1 MiB; the committed
    # entry.png is 1024x1024 and about 172 KB, so this guard only ever
    # trips if the file was replaced by something out of spec.
    if size <= 0 or size > 1024 * 1024:
        print("entry.png size out of range: %d" % size, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
