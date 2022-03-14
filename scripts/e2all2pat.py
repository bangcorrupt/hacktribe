import pathlib
import argparse

def main():		
	parser = argparse.ArgumentParser()	
	parser.add_argument("-i", "--input", dest='inFile', help="path/to/input/file.e2allpat")
	parser.add_argument("-o", "--output", dest='outDir', help="path/to/output/directory")
	args = parser.parse_args()
	
	inFile = 'electribe_allpattern.e2allpat'
	outDir = 'split_allpat'
	
	if args.inFile:
		inFile = args.inFile
	if args.outDir:
		outDir = args.outDir
		
	pathlib.Path(outDir).mkdir(parents=True, exist_ok=True)
	
	with open(inFile, 'rb') as f:
		apData =  bytearray(f.read())	
	
	patOff = 0x10100
	patLen = 0x4000
	for i in range(250):
		start = patOff+(i*patLen)
		end = start + patLen
		data = apData[start:end]
		outFile = outDir + '/' + str(i+1).zfill(3) + '_' + data[16:32].decode().rstrip('\0')	# get pattern name from data

		data = apData[:256] + data																# add korg file header
		with open(outFile + '.e2pat', 'wb') as f:
			f.write(data)

if __name__ == '__main__':
    main()
