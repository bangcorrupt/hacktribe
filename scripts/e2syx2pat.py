# Converts .syx to .e2pat
import argparse
from e2_syx_codec import syx_dec


def main():	

    parser = argparse.ArgumentParser()
    parser.add_argument("file", metavar="filepath", type=str, help="path/to/file.syx")

    args = parser.parse_args()

    with open(args.file, 'rb') as f:	
        data =  bytearray(f.read())

    if data[6] == 0x40:						# remove syx header from 'current pattern dump'
        data = data[7:-1]		
    elif data[6] == 0x4c:					# remove syx header from 'pattern dump'
        data = data[9:-1]


    pat_data = syx_to_pat(data)

    outfile = args.file[:-3] + 'e2pat'			# change filename extension
    with open(outfile, 'wb') as f:
        f.write(pat_data)

    print(args.file + ' converted to ' + outfile)



def syx_to_pat(syx_data):
    
    pat_head = (b'KORG'.ljust(16, b'\x00') + 
               b'electribe'.ljust(16, b'\x00') +
               b'\x01\x00\x00\x00'.ljust(224, b'\xff'))
                    
    pat_data = pat_head + syx_dec(syx_data)
    
    return pat_data

if __name__ == '__main__':
    main()
