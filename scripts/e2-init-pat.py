# Set Electribe 2 Sampler firmware version 2.02 init pattern

import os
import sys

if len(sys.argv) < 3:
    print('Usage:')
    print()
    print('Supports Electribe 2 Sampler firmware version 2.02 only')
    print()
    print('python e2s-init-pat.py SYSTEM.VSB init-pat.e2spat')
    print()
    exit()

print('Supports Electribe 2 Sampler firmware version 2.02 only')

vsb_path = sys.argv[1]
if os.path.exists(vsb_path):

    pat_path = sys.argv[2]
    if os.path.exists(pat_path):
 
        print('Modifying firmware')
        
        with open(vsb_path, 'rb') as f:
            vsb = bytearray(f.read())
        
        with open(pat_path, 'rb') as f:
            pat = bytearray(f.read())[0x100:0x3d00]
        
        assert len(pat) == 0x3c00

        head = vsb[:0x100]
        hak = vsb[0x100:]

        # Sampler v2.02
        hak[0xcff58:0xcff58+0x3c00] = pat

        fw = head + hak
        
        assert len(fw) == 0x200100
        
        with open(vsb_path, 'wb') as f:
            f.write(fw)

    else:
        print('Pattern file not found')

else:
    print('Firmware file not found')
