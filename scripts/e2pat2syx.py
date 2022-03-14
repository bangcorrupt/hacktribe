# Converts .e2pat to .syx
import argparse
from e2_syx_codec import syx_enc

def main():	
	
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pattern", dest='patNum', help="destination pattern number (1-250)")
    parser.add_argument("file", metavar="filepath", type=str, help="path/to/file.e2pat")

    args = parser.parse_args()

    with open(args.file, 'rb') as f:	
        data =  bytearray(f.read())	

    
    if args.patNum:
        syx_data = pat_to_syx(pat_data, pat_num=int(args.patNum))
    else:
        syx_data = pat_to_syx(pat_data)
    
    
    outfile = args.file[:-5] + 'syx'											# change filename extension
    with open(outfile, 'wb') as f:
        f.write(syx_data)

    if args.patNum:
        print(args.file + ' converted to ' + outfile + ', pattern number ' + args.patNum)
    else:
        print(args.file + ' converted to ' + outfile)




def pat_to_syx(pat_data, pat_num=False):
    
    data = pat_data[0x100:]

    bytearray(syx_head = [0xf0, 0x42, 0x30, 0x00, 0x01, 0x23, 0x40])                 # dump to current pattern

    if pat_num:
        pat_num = int(pat_num)-1
        msb = 0
        lsb = pat_num % 128
        if pat_num > 127:
            msb = 1
        syx_head = bytearray([0xf0, 0x42, 0x30, 0x00, 0x01, 0x23, 0x4c, lsb, msb])   # dump to patNum

    syx_data = syx_head + syx_enc(data) + b'\xf7'

    return syx_data


if __name__ == '__main__':
    main()
