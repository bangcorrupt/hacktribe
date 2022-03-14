
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest='path', help="path/to/pattern/file")	
parser.add_argument("-o", "--output", dest='outpath', help="path/to/save/file")	
parser.add_argument("-p", "--part", dest='part', help="part number")
parser.add_argument("-r", "--rot", dest='rot', help="rotation steps")	
args = parser.parse_args()
	
def rotate(l, n):
    return l[n:] + l[:n]
	
with open(args.path, 'rb') as f:
	pattern =  bytearray(f.read())	
partOff = 0x900
partLen = 0x330
seqOff = 0x30
seqLen = 0xC0
stepLen = 0x0C
part = int(args.part) - 1
rot = int(args.rot)

seqStart = partOff + (part * partLen) + seqOff
seqEnd = seqStart + seqLen
steps = pattern[seqStart:seqEnd]
output = rotate(steps, rot*stepLen)

for i in range(len(steps)):
	pattern[i+seqStart] = output[i]

with open(args.outpath, 'wb') as f:
	f.write(pattern)
