"""
Merges e2spat files in a directory into a single e2sallpat file.
I am very unpleased with another script that is named "e2pat2all.py" >:(
Usage: e2_merge_patterns.py <input directory> <output patterns file>

Expects filenames to be in format "XXX_NAME.e2pat" for example:
001_Something off.e2pat
051_W[`IRNMO.e2pat
250_ACIDSATAN.e2pat

March 20th 2025
@author: noVictim
"""

import re
import os
import sys

def eat_file(filepath) -> bytearray:
    with open(filepath, "rb") as f:
        return bytearray(f.read())
    return bytearray()

def find_pattern_files(directory):
    matched_files = {}
    pattern = re.compile(r"^(\d{3})_\s*[\w\[\]`!@#$%^&*()\-+=~'. ]*\.e2pat$", re.IGNORECASE)
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 250:
                matched_files[num] = filename
    return matched_files


if __name__ == '__main__':

    if sys.version_info <= (3,10):
        exit(f"Assumes Python version 3.10+, you have {sys.version_info.major}.{sys.version_info.minor}")
    if len(sys.argv) != 3:
        exit("Usage: e2_merge_patterns.py <input directory> <output patterns file>")
    if not os.path.exists(sys.argv[1]) or not os.path.isdir(sys.argv[1]):
        exit(f'Invalid input directory "{sys.argv[1]}"')
    
    # Grab reference init file and work from there
    allpat = eat_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'init/electribe_sampler_allpattern.e2sallpat'))

    for num, filename in find_pattern_files(sys.argv[1]).items():
        pattern = eat_file(os.path.join(sys.argv[1], filename))

        # Rename pattern to filename just in case
        pattern[0x110:0x110+16] = filename[4:-6].encode('ascii').ljust(16, b'\x00')

        offset = 0x10100 + (0x4000 * (num - 1))
        allpat[offset:offset+0x4000] = pattern[256:] # we mustn't copy the pattern's header

    with open(sys.argv[2], "wb") as f:
        f.write(allpat)
