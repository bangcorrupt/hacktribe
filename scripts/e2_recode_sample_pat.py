#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read sample library from e2sSample.all file, 
move sample references into slots 501+ as far as possible,
save altered library as e2sSample.shift.all,
and create a lookup table for the new osc locations. 

Sample file format: see https://github.com/untergeekDE/electribe2-docs/blob/main/e2sSample-all-file-format.md
Pattern file format: see e2pat_shift.py script

Read pattern file and recode patterns to use new osc locations.

2022-01-02
@author: untergeekDE
"""
import argparse
import os
import re # Regular Expressions

# Using bangcorrupt's e2all2pat.py script as a base.
# For testing in Spyder IDE: change working directory one level up
# os.chdir("..")

def get_category(c):
    # Convert integer to category string
    categories = ['Analog', # 0
                  'Audio In', 
                  'Kick', 
                  'Snare', 
                  'Clap',
                  'HiHat', #5
                  'Cymbal', 
                  'Hits', 
                  'Shots', 
                  'Voice', 
                  'SE', #10
                  'FX', 
                  'Tom', 
                  'Perc', 
                  'Phrase', 
                  'Loop', #15
                  'VPM', 
                  'Wave']
    if c > 17:
            return f"Error: {c}"
    return categories[c]

def get_pointers(buffer):
    # Return a list of pointers
    l = []
    for i in range(1000):
        ii = i * 4 +0x10
        p = int.from_bytes(buffer[ii:ii+4],'little')
        if (p > 0):
            l.append(p)
    return l

def get_used_osc_set(buffer):
    # Return a set with all the oscs used in the patterns. 
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
    osc_list = []
    pat_ofs = 0x10100
    pat_len = 0x4000
    part_ofs = 0x0800
    part_len = 0x0330
    # Repeat for all 250 patterns: 
    for i in range(250):
        # Repeat for all 16 parts:
        for k in range(16):
            part_ptr = pat_ofs + (i * pat_len) + part_ofs + (k * part_len)
            # Return oscillator for pattern 
            osc_list.append(buffer[part_ptr + 0x08] + 256 * buffer[part_ptr + 0x09])
    osc_set = set(osc_list)
    return osc_set

def get_used_pattern_set(buffer,osc):
    # Return a set with all the patterns making use of that osc. 
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
    pattern_set ={} 
    pat_ofs = 0x10100
    pat_len = 0x4000
    part_ofs = 0x0800
    part_len = 0x0330
    # Repeat for all 250 patterns: 
    for i in range(250):
        # Repeat for all 16 parts:
        for k in range(16):
            part_ptr = pat_ofs + (i * pat_len) + part_ofs + (k * part_len)
            # Return oscillator for pattern and add to list
            if osc == (buffer[part_ptr + 0x08] + 256 * buffer[part_ptr + 0x09]):
                pattern_set.append(i)
    return pattern_set


def get_sample_pointer(buf,i):
    # Read pointer from header block
    return(int.from_bytes(buf[i*4+16:i*4+20],'little'))

def get_sample_list(buf):
    # Check if sample is referenced, add to list if yes
    sample_list = []
    for i in range(1000):
        if get_sample_pointer(buf[0:0x1000],i) > 0:
            sample_list.append(i)
    return sample_list

def get_sample_name(buf,i):
    # Follow pointer and get category
    p = get_sample_pointer(buf,i)
    if p == 0: 
        return "?"
    RIFF_len = int.from_bytes(buf[p+4:p+8],'little') + 8
    # Calculate location of sample slot number: 0x494 bytes before the end
    sample_name_p = p + RIFF_len - 0x494 + 0x02
    # Assign the new sample number
    name = str(buf[sample_name_p:sample_name_p+16],encoding="utf-8")
    return re.sub(r'[^\w\s-]',' ',name)


def get_sample_category(buf,i):
    # Follow pointer and get category
    if i == 17: 
        # This is Audio In
        return 1 
    if i < 17: 
        # These are the Analog Synth models
        return 0
    p = get_sample_pointer(buf, i)
    if p == 0: 
        return 18 # "--"
    RIFF_len = int.from_bytes(buf[p+4:p+8],'little') + 8
    # Calculate location of sample slot number: 0x494 bytes before the end
    sample_cat_p = p + RIFF_len - 0x494 + 0x012
    # Assign the new sample number
    return int.from_bytes(buf[sample_cat_p:sample_cat_p+2],'little')

def main():        
    explanation = """This script reads an Electribe's sample library and pattern 
    dump files, and adapts them for the HackTribe: As you cannot use the 
    Factory sample slots (1-500).  
    in the HackTribe, the factory and user samples are moved to 501-999. The 
    code tries to fit as much as possible to the User slots; if there are 
    more samples than slots available,
    it starts overwriting loops and phrases not used in the patterns."""
    parser = argparse.ArgumentParser(epilog=explanation)    
    parser.add_argument("-s", "--sample", dest='sampleFile', help="path/to/input/file.e2sallpat")
    parser.add_argument("-p", "--pattern", dest='patternFile', help="path/to/input/e2sSample.all")
    parser.add_argument("-o", "--outdir", dest='outDir', help="path/to/output/")
    parser.add_argument("-f", "--ofs", dest='user_ofs', help="Offset in user memory (default: 18 to start factory samples at slot 519, makes it easier to find them)")
    parser.add_argument("-m", "--minimal", action="store_true", help="If this flag is set, all unused samples are discarded, and offset is set to 0")
    args = parser.parse_args()
    
    patternFile = './electribe_sampler_allpattern.e2sallpat'
    sampleFile = './e2sSample.all'
    outDir = "."
    minimalMode = args.minimal
    if minimalMode: 
        user_ofs = "0"
    else:
        user_ofs = "18"
    
    if args.sampleFile:
        sampleFile = args.sampleFile
    if args.patternFile:
        patternFile = args.patternFile
    if args.outDir:
        outDir = args.outDir
    
    if args.user_ofs:
        user_ofs = args.user_ofs

    # Check for valid range
    ofs_val = abs(int(user_ofs))
    if ofs_val > 500:
        ofs_val = ofs_val % 500
        

    # Conversion strategy: 
    #     - Start by moving factory samples 019-420 
    #     - Fill the empty slots at the end with user samples until full (999)
    #     - Fill any empty slots at the beginning (only if ofs is used)
    #     - Start overwriting sample slots not used in patterns, from the loop/phrase category dowmnwards 
    #     - When running out of slots, stop reassignment with a message listing unassigned samples. 
    #     Reorder:
    #     - Create a dictionary mapping old -> new osc slots
    #     - Create a text file containing the mappings
    #     - Remap osc numbers in patterns 
    #     - Write changed osc slots to sample blocks
    #     - Create the new pointer table
    #     - Save modified copies of .all and .e2sallpat files

    # Read sample file into memory
    try:
        with open(sampleFile, 'rb') as f:
            sample_buf =  bytearray(f.read())   
    except:
        print("Could not read ",sampleFile," into memory. Stopping.")
        return()
    else: 
        print(len(sample_buf)," bytes read from ",sampleFile)

    # Read pattern file into memory

            
    
    
    # Read pattern file into memory
    try:
        with open(patternFile, 'rb') as f:
            pattern_buf =  bytearray(f.read())    
    except:
        print("Could not read ",patternFile," into memory. Stopping.")
        return()
    else: 
        print(len(pattern_buf)," bytes read from ",patternFile)
        

    # Get a set of all oscs used in the patterns
    unfiltered_set = get_used_osc_set(pattern_buf)
    # ...and take out the synth oscs (0-17)
    osc_set = {x for x in unfiltered_set if x > 17}
    # Get a list of the existing samples from the sample bank
    old_header = sample_buf[0:0x1000]
    sample_list = get_sample_list(old_header)
    dropped_sample_list = []
    # Prepare Lookup dictionary; for first 18 slots: input = output. 
    old_to_new_dict = {}
    for i in range(18): 
        old_to_new_dict[i] = i
        
    # Test for number of sample slots needed. More samples used than slots
    # available? Will lose memory. 
    free_slots = 499
    if len(osc_set) > free_slots:
        print("WARNING: ",len(osc_set)," samples in use - only 499 will fit!!")
        print("Forcing Minimal Mode.")
        minimalMode = True
        # Cut off all samples beyond no. 499
        dropped_sample_list.append(sample_list[free_slots:])
        sample_list = sample_list[0:free_slots]
        print("See dropped_samples.txt for details.")
    #---- Remove unused samples in --minimal mode. ----
    if minimalMode: 
        for osc_no in sample_list:
            if not (osc_no in osc_set):
                # Erase entry in pre-move pointer table
                old_header[4*osc_no + 0x10] = 0
                old_header[4*osc_no + 0x11] = 0
                old_header[4*osc_no + 0x12] = 0
                old_header[4*osc_no + 0x13] = 0
                # Remove from sample list, add to removed samples list
                sample_list.remove(osc_no)
                dropped_sample_list.append(osc_no)
    
    #---- Remove unused samples if more space is needed. ----
    needed_slots = len(sample_list)
    # Do we need to lose some samples?
    # Calculate how many, and lose them.
    p = 0
    while needed_slots > free_slots:
        if sample_list[p] not in osc_set:
            needed_slots = needed_slots - 1
            dropped_sample_list.append(sample_list[p])
            del sample_list[p]
        else:
            p = p + 1

    #---- Generate all output files in output directory ---- 
    # Change to output directory
    if not os.path.isdir(outDir):
        os.mkdir(outDir)
    os.chdir(outDir)
    
    # Write samples marked for deletion to a file before deleting. 
    with open('dropped_samples.txt', 'w') as f:
        f.write("Dropped files listed by old number and name\n")
        f.write("-------------------------------------------\n")
    # Iterate over the dictionary and write each key-value pair to the file
        for osc in dropped_sample_list:
            osc_name = get_sample_name(sample_buf, osc)
            osc_cat = get_category(get_sample_category(sample_buf, osc))
            end_str = ""
            if osc in osc_set:
                # Very special case - samples dropped that are being used
                end_str = '!!!USED IN PATTERNS ' 
                for pat in get_used_pattern_set(pattern_buf, osc):
                    end_str = end_str + str(pat + 1) + " "
            f.write (f"{osc:03d} {osc_name} ({osc_cat}) {end_str}\n")
    
            
    #---- Moving samples ----
    # For the time being, don't move the samples, only change references. 
    
    # This loop steps through all existing samples.
    # First, it goes looking for the next free position.
    # If it doesn't find any, it gets more and more aggressive, 
    # overwriting unused sample slots in the process.)   
            
    # Assign first free position with offset. 
    # Why the offset? I found that I could keep track better if the
    # factory samples are still in their original position +500, so I
    # run this script with the --ofs 18 parameter, i.e. the factory samples
    # go from 19...421 to 519...921. 
    # Create a blank pointer table for moving
    for i in range(0x10,0x1000):
        sample_buf[i] = 0
    i = 500+ofs_val
    # Now: Move sample pointers and correct sample references.  
    for osc_no in sample_list:     
        # Start reading from slot 019 to 421
        # Humans count from 1, machines from 0.
        p = get_sample_pointer(old_header,osc_no)
        # Save sample pointer to new location in pointer table
        sample_buf[4*i + 0x10:4*i + 0x14] = p.to_bytes(4,'little')
        # Rewrite osc number in RIFF block
        # Get length of whole RIFF chunk
        RIFF_len = int.from_bytes(sample_buf[p+4:p+8],'little') + 8
        # Pointer to beginning of ESLI data data block
        esli_p = p + RIFF_len - 0x494
        # Write slot number: is stored 0x494 bytes before the end
        sample_buf[esli_p] = i % 256
        sample_buf[esli_p + 1] = i // 256
        # Write "Absolute Sample No" in esli_p + 0x14  
        abs_sample_no = i + 50
        sample_buf[esli_p + 0x14] = abs_sample_no % 256
        sample_buf[esli_p + 0x15] = abs_sample_no // 256
        # Rewrite categories 16 (PCM) and 17 (User) - 
        # ...the Hacktribe firmware re-brands them VPM and WAVE. 
        sample_cat = sample_buf[esli_p + 0x12] + 256 * sample_buf[esli_p + 0x13]
        if sample_cat == 16:
            sample_buf[esli_p + 0x12] = 17 # Make former PCM WAVE
        # Leave former USER category as WAVE
        # Add new location to dictionary
        old_to_new_dict[osc_no] = i
        # And don't forget to add 1 for the humans.
        print("Moved factory sample ",osc_no + 1," to slot ",i + 1)
        i = (i + 1) 
        if i > 500+free_slots:
            i = 500
    print("Changed categories: PCM -> WAVE, User -> WAVE")
    
    #---- Rewrite new osc numbers to patterns ----
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
            partOsc = pattern_buf[partPtr + 0x08] + 256 * pattern_buf[partPtr + 0x09]
            # New Oscillator
            try:
                shiftOsc = old_to_new_dict[partOsc]
                # Write shifted osc reference to data buffer
                pattern_buf[partPtr + 0x08] = shiftOsc % 256
                pattern_buf[partPtr + 0x09] = shiftOsc // 256
            except: 
                print("!!WARNING: Osc",partOsc+1,
                      "in Pattern ", i + 1,
                      ", Part ",k + 1,
                      "does not exist in sample set")
    
    #---- Write mappings
    with open('old_to_new_map.txt', 'w') as f:
        f.write("OLD --- NEW Osc Numbers ------\n")
    # Iterate over the dictionary and write each key-value pair to the file
        for key, value in old_to_new_dict.items():
            osc_name = get_sample_name(sample_buf, value)
            osc_cat = get_category(get_sample_category(sample_buf, value))
            osc_old = key + 1
            osc_new = value +1 
            map_text = (f'{osc_old:03d} --- {osc_new:03d} {osc_name} ({osc_cat})\n')
            f.write(map_text)
            print(map_text,end="")
    
    # Generate new pattern bank file hacktribe.e2sallpat
    # Copy to /KORG/hacktribe/
    with open("hacktribe.e2sallpat", 'wb') as f:
        f.write(pattern_buf)
    print("File hacktribe.e2sallpat generated - copy to SD card to load.")
    
    # Generate new sample bank file hacktribeSample.all
    with open("hacktribeSample.all", 'wb') as f:
        f.write(sample_buf)
    # Copy to /KORG/hacktribe/sample/e2sSample.all
    print("File hacktribeSample.all generated - copy to /KORG/hacktribe/Sample/e2sSample.all on SD CARD.")
    print("Done.")
    
if __name__ == '__main__':
    main()
