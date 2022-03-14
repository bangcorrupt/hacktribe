import argparse
from construct import *


# File format struct defs

# VSB file header format
# Default is SYSTEM.VSB for E2S v2.02
vsb_header = Struct('title' / Default(PaddedString(0x10, 'ascii'), 'KORG SYSTEM FILE'),
                    'dev_name' / Default(PaddedString(0x10, 'ascii'), 'E2S'),
                    'file_id' / Default(PaddedString(0x8, 'ascii'), 'SYSTEM'),
                    'rev' / Default(Int16ub, 1),
                    'maj_ver' / Default(Int8ub, 2),
                    'min_ver' / Default(Int8ub, 2),
                    Padding(1),
                    'dev_id' / Default(Hex(Int16ub), 0x124),
                    Padding(1, pattern=b'\xff'),
                    Padding(4),
                    'src_len' / Default(Hex(Int32ul), 0x200000),
                    Padding(4),
                    'dest_len' / Default(Hex(Int32ul), 0x200000),
                    'unk_int' / Default(Int16ul, 2),
                    Padding(0xbe, pattern=b'\xff')
                   )

def main():
    parser = argparse.ArgumentParser()	
    parser.add_argument("-s", "--src", dest='src_path', help="path/to/source/SYSTEM.VSB")
    parser.add_argument("-d", "--dst", dest='dst_path', help="path/to/destination/hacked-SYSTEM.VSB")
    
    args = parser.parse_args()
    
    if args.src_path:
        src_path = args.src_path
    else:
        src_path = 'test.hacktribe.bin'

    if args.dst_path:
        dst_path = args.dst_path
    else:
        dst_path = 'test.hacktribe.SYSTEM.VSB'

    with open(src_path, 'rb') as f:
        src_bin = f.read()
    
    header = vsb_header.build(dict())
    
    dest_vsb = header + src_bin
    
    with open(dst_path, 'wb') as f:
        f.write(dest_vsb)
    
    
if __name__ == "__main__":
    main()
