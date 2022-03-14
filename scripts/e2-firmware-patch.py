# Hacktribe 2 firmware patcher

import argparse
import hashlib
from bsdiff4 import file_patch

def main():
    parser = argparse.ArgumentParser()	
    parser.add_argument("-s", "--src", dest='src_path', help="path/to/source/SYSTEM.VSB")
    parser.add_argument("-d", "--dst", dest='dst_path', help="path/to/destination/hacked-SYSTEM.VSB")
    parser.add_argument("-p", "--patch", dest='patch_path', help="path/to/hacktribe-2.patch")
    parser.add_argument("-e", "--edit-header", dest='edit_header', action='store_true', help="Edit file header to allow install on e2 synth.")
    parser.set_defaults(edit_header=False)
    
    args = parser.parse_args()

    if args.src_path:
        src_path = args.src_path
    else:
        src_path = 'SYSTEM.VSB'

    if args.dst_path:
        dst_path = args.dst_path
    else:
        dst_path = 'hacked-SYSTEM.VSB'

    if args.patch_path:
        patch_path = args.patch_path
    else:
        patch_path = 'patch/hacktribe-2.patch'
    
    if args.edit_header:
        edit_header = True
        sd_path = 'KORG/electribe/System/SYSTEM.VSB'
        device = 'Electribe 2 Synth'
    else:
        edit_header = False
        sd_path = 'KORG/electribe sampler/System/SYSTEM.VSB'
        device = 'Electribe 2 Sampler'

    
    src_hash = '1d0f0689d5a12c8a8bde9f821f2a59adc5f6cd6012ddb201ebb192b72468a646'

    if edit_header:
         with open ("hash/modified-hacked-SYSTEM.VSB.sha", "r") as f:
            targ_hash=f.readlines()[0].split()[0]       
    else:
        with open ("hash/hacked-SYSTEM.VSB.sha", "r") as f:
            targ_hash=f.readlines()[0].split()[0]


    print('\nHacktribe firmware patcher.\n')
    print('https://github.com/bangcorrupt/hacktribe\n')
    
    print('Source file hash'.ljust(32, ' '), ':', src_hash, '\n')

    if get_digest(src_path) != src_hash:
        print('ERROR: Incorrect source file.')
        print('Electribe 2 Sampler firmware version 2.02 only.')
        print("Download Electribe 2 Sampler firmware version 2.02 and move 'SYSTEM.VSB' to 'hacktribe' directory.\n")
        exit()

    else:
        print('Electribe 2 Sampler firmware version 2.02 found.\n')

    print('Patching firmware for ' +device+ '...\n')

    file_patch(src_path, dst_path, patch_path)

    if edit_header:
        modify_header(dst_path)
    
    dst_hash = get_digest(dst_path)   

    print('Target file hash'.ljust(32, ' '), ':', targ_hash)

    if  dst_hash != targ_hash:
        print('Destination file hash'.ljust(32, ' '), ':', dst_hash, '\n')
        print('ERROR: Patch FAILED.')
        print('Do not install modified firmware.\n')
        exit(1)

    else:
        print('Destination file hash'.ljust(32, ' '), ':', dst_hash, '\n')
        print('Firmware patched successfully.\n')
        print("Copy '" +dst_path+ "' to 'SD:/" +sd_path+ "' and update firmware.\n") 
        exit(0)


def modify_header(path):
    with open(path, 'rb') as f:
        hak = bytearray(f.read())

    print("Modifying header of '" +path+ "'...\n")
    
    # e2
    hak[0x12] = 0x00
    hak[0x2e] = 0x23

    with open(path, 'wb') as f:
        f.write(hak)


def get_digest(path):
    h = hashlib.sha256()

    with open(path, 'rb') as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()

if __name__ == '__main__':
    main()
