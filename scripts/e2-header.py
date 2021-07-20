# Modify Electribe 2 Sampler file header for Electribe 2 Synth

import os
import sys

if len(sys.argv) < 2:
    print('Usage:')
    print()
    print('e2-header.py FILE_PATH')
    exit()

path = sys.argv[1]
if os.path.exists(path):
    print('Modifying header', os.path.basename(path))


    with open(path, 'rb') as f:
        hak = bytearray(f.read())

    # e2s-e2
    hak[0x12] = 0x00
    hak[0x2e] = 0x23

    with open(path, 'wb') as f:
        f.write(hak)

else:
    print('File not found')
