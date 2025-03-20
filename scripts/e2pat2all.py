import pathlib
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest='inFile',
                        help="path/to/input/file.e2pat")
    parser.add_argument("-o", "--output", dest='outDir',
                        help="path/to/output/directory")
    args = parser.parse_args()

    inFile = 'init/init.e2pat'
    outDir = 'merged_allpat'
    outFile = 'electribe_sampler_allpattern.e2sallpat'
    initFile = 'init/electribe_sampler_allpattern.e2sallpat'

    if args.inFile:
        inFile = args.inFile
    if args.outDir:
        outDir = args.outDir

    pathlib.Path(outDir).mkdir(parents=True, exist_ok=True)
    outFile = outDir + '/' + outFile

    # Read reference allpatterns file to grab header
    # EOF is at 0x3F80D8 e.g. 4161752 (4.2 MB total size)
    # Korg header is up to 0x10100
    with open(initFile, 'rb') as f:
        allData = bytearray(f.read())

    # Read init pattern file to populate new allpatterns file
    with open(inFile, 'rb') as f:
        apData = bytearray(f.read())

    patOff = 0x10100  # where the pattern content starts in the allpatterns file
    patLen = 0x4000  # predefined size for each pattern (16384 bytes each)

    # Iterate 250 times and swap the patterns in our allData, starting from patOff
    data = allData[:0x10100]

    for i in range(250):
        start = patOff+(i*patLen)
        data[start:start+patLen] = apData[256:]

    with open(outFile, 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
