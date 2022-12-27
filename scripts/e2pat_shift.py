# Simple program that reads an .e2allpat file and shifts all oscillator numbers 
# by the number given. This is to simplify using existing patterns with 
# bangcorrupt's wonderful HACKTRIBE ROM - https://github.com/bangcorrupt/hacktribe - 
# which brings a host of new possibilities, including new oscillators. (VPM!!!)
# This means, though, that all factory samples have to move to slots 501+.
#
# I wanted to keep my existing patterns, this kept me from installing HACKTRIBE - 
# but now that I've done it, I did not want to correct all existing patterns by hand

import argparse

# Using bangcorrupt's e2all2pat.py script as a base.
# (I'd normally use snake_case instead of camelCase for variables. Never mind!)

def main():        
    explanation = """This script adapts all the osc numbers in your existing patterns\n
            if you had to move the samples to make room for the new Hacktribe waveforms.\n 
            The factory waveforms 1..18 are left untouched."""
    parser = argparse.ArgumentParser(epilog=explanation)    
    parser.add_argument("-i", "--input", dest='inFile', help="path/to/input/file.e2sallpat")
    parser.add_argument("-o", "--output", dest='outFile', help="path/to/output/shiftedxxx.e2sallpat")
    parser.add_argument("-s", "--shift", dest='shiftBy', help="Shift osc by -999...999")
    args = parser.parse_args()
    
    inFile = 'electribe_allpattern.e2sallpat'
    shiftBy = "500"

    
    if args.inFile:
        inFile = args.inFile
    
    if args.shiftBy:
        shiftBy = args.shiftBy

    # Check for valid range
    shiftVal = int(shiftBy)
    if shiftVal > 999 or shiftVal < -999:
        shiftVal = shiftVal % 1000

    # Create output file name containing shift
    outFile = 'shifted' + str(shiftVal) + '.e2sallpat'
    if args.outFile:
        outFile = args.outFile
    

    with open(inFile, 'rb') as f:
        apData =  bytearray(f.read())    
    
    # Structure of .e2allpat file: 
    # Extensive info can be found here: http://www.korgforums.com/forum/phpBB2/viewtopic.php?t=95368
    #    
    # 0x00000-0x00100: Korg Electribe file header
    # Next 0x10000 bytes (64k) are filler bytes containing 0xFF.
    # Length of one pattern is 0x4000 (16k) 
    # Data for the patterns 1-250 follows from 0x10100.
    # Part data starts 0x800 (2k) into the pattern data, i.e. first pattern is from 0x10900.
     # Length of one part is 0x330.
    # Osc data is 0x08 (lo) and 0x09 (hi) into this data. 
    #
    # So
    patOff = 0x10100
    patLen = 0x4000
    partOff = 0x0800
    partLen = 0x0330
    # Repeat for all 250 patterns: 
    for i in range(250):
        # When printing, add 1 for humans. 
        print("== Processing pattern ",i+1," ==")
        # Repeat for all 16 parts:
        for k in range(16):
            partPtr = patOff + (i*patLen) + partOff + (k * partLen)
            partOsc = apData[partPtr + 0x08] + 256 * apData[partPtr + 0x09]
            # Shift and correct
            # (Leave the base waveforms 0-17 unchanged)
            if partOsc < 18:
                shiftOsc = partOsc
            else:
                shiftOsc = partOsc  + shiftVal
            if shiftOsc > 999 or shiftOsc < -999:
                shiftOsc = shiftOsc % 1000
            # Write shifted osc reference to data buffer
            apData[partPtr + 0x08] = shiftOsc % 256
            apData[partPtr + 0x09] = shiftOsc // 256
            # When printing, add 1 for humans. 
            print("Part ",k+1,": Shift osc ",partOsc + 1," ->  ",shiftOsc + 1)
    with open(outFile, 'wb') as f:
        f.write(apData)

if __name__ == '__main__':
    main()
