#!/usr/bin/env python3
"""
Updates e2sallpat after updating a sample library.
Useful for when the order of your samples changes frequently.
NOTE: This script does not understand renamed samples!

Sample file format: see https://github.com/untergeekDE/electribe2-docs/blob/main/e2sSample-all-file-format.md
Pattern file format: see http://www.korgforums.com/forum/phpBB3/viewtopic.php?t=95368

Usage: e2_update_pat_samples.py <patterns file> <old sample all> <new sample all>

March 19th 2025
@author: noVictim
"""

import sys

def eat_file(filepath) -> bytes:
    data = bytes()
    with open(filepath, "rb") as f:
        data += f.read()
    return data

def read_sample_addrs(data) -> list:
    addrs = []
    for i in range(1002):
        offset = 0x58 + (4 * i)
        address = int.from_bytes(data[offset : offset + 4], 'little')
        addrs.append(address)
    return addrs

def get_samples(data) -> dict:
    samples = {}
    for i, addr in enumerate(read_sample_addrs(data)):
        if addr == 0x00000000:
            continue
        esli_p = addr + int.from_bytes(data[addr+4:addr+8], 'little') - 0x494
        id_p = esli_p + 0x08
        name_p = esli_p + 0x0A
        sample_id = int.from_bytes(data[id_p:id_p+2], 'little')
        sample_name = data[name_p:name_p+16]
        samples[sample_id] = sample_name
    return samples

def find_changes(old_names, new_names) -> tuple[list,dict,list]:
    added_nums = []
    deleted_nums = []
    moved_nums = {}
    for num, name in old_names.items():

        # Deleted items
        if name not in new_names.values():
            print(f"Deleted {name.decode('ascii')}")
            deleted_nums.append(num)
            continue
        
        # Moved items
        if name != new_names[num]:
            for new_num, new_name in new_names.items():
                if name == new_name:
                    break
            print(f"Moved {name.decode('ascii')} {num} -> {new_num}")
            moved_nums[num] = new_num
    
    for num, name in new_names.items():
        if not name in old_names.values():
            print(f"Added {name.decode('ascii')} at {num}")
            added_nums.append(num)
    return (deleted_nums, moved_nums, added_nums)



if __name__ == '__main__':

    if sys.version_info <= (3,10):
        exit(f"Assumes Python version 3.10+, you have {sys.version_info.major}.{sys.version_info.minor}")
    if len(sys.argv) != 4:
        exit("Usage: e2_update_pat_samples.py <patterns file> <old sample all> <new sample all>")

    old_names = get_samples(eat_file(sys.argv[2]))
    new_names = get_samples(eat_file(sys.argv[3]))
    deleted, moved, added = find_changes(old_names, new_names)

    e2allpat_mode = True # TODO: implement the latter
    input_allpat = eat_file(sys.argv[1])
    output_allpat = bytearray(input_allpat)

    for pattern_index in range(250):
        for part_num in range(16):

            # Read oscillator ID
            pattern_offset = 0
            if e2allpat_mode:
                pattern_offset = 0x10100 + (0x4000 * pattern_index)
            offset = pattern_offset + 0x800 + (0x330 * part_num) + 0x08
            oscillator = int.from_bytes(input_allpat[offset : offset+2], 'little')

            # Update this part's oscillator to the newly corresponding ID if needed
            if oscillator in moved.keys():
                output_allpat[offset : offset+2] = moved[oscillator].to_bytes(2, 'little')

    with open(sys.argv[1], "wb") as f:
        f.write(bytes(output_allpat))
