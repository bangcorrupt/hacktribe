#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read sample library from e2sSample.all file, 
list RIFF pointer and metadata for each sample 
and create a lookup table. 

Sample file format: see https://github.com/untergeekDE/electribe2-docs/blob/main/e2sSample-all-file-format.md

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
    categories = ['Analog',
                  'Audio In', 
                  'Kick', 
                  'Snare', 
                  'Clap',
                  'HiHat', 
                  'Cymbal', 
                  'Hits', 
                  'Shots', 
                  'Voice', 
                  'SE', 
                  'FX', 
                  'Tom', 
                  'Perc', 
                  'Phrase', 
                  'Loop', 
                  'PCM', 
                  'User',
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

def main():        
    explanation = """Reads an e2ssample.all file and gives back metadata
        for all the samples in the file."""
    parser = argparse.ArgumentParser(epilog=explanation)    
    parser.add_argument("-s", "--sample", dest='sampleFile', help="path/to/input/file.e2sallpat")
    parser.add_argument("-o", "--outdir", dest='outDir', help="path/to/output/")
    args = parser.parse_args()
    
    sampleFile = './e2sSample.all'
    outDir = "."
    
    if args.sampleFile:
        sampleFile = args.sampleFile
    if args.outDir:
        outDir = args.outDir    

    # Read sample file into memory
    try:
        with open(sampleFile, 'rb') as f:
            sample_buf =  bytearray(f.read())   
    except:
        print("Could not read ",sampleFile," into memory. Stopping.")
        return()
    else: 
        print(len(sample_buf)," bytes read from ",sampleFile)
        
    sample_list = get_sample_list(sample_buf)

    # Now: Move sample pointers and correct sample references.  
    os.chdir(outDir)
    with open('sample_list.txt', 'w') as f:
        for osc_no in sample_list:     
            # Start reading from slot 019 to 421
            # Humans count from 1, machines from 0.
            p = get_sample_pointer(sample_buf,osc_no)
            output_str = f"---- Osc No. {osc_no+1}, sample pointer {p:04x} ----\n"
            # Write sample slot number: is stored 0x494 bytes before the end
            p = get_sample_pointer(sample_buf,osc_no)
            if p == 0: 
                osc_name="?"
                osc_cat = "?"
            else:
                RIFF_len = int.from_bytes(sample_buf[p+4:p+8],'little') + 8
                esli_p = p + RIFF_len - 0x494
                # Calculate location of sample slot number: 0x494 bytes before the end
                sample_name_p = esli_p + 0x02
                # Assign the new sample number
                osc_name = re.sub(r'[^\w\s-]',' ',str(sample_buf[sample_name_p:sample_name_p+16],encoding="utf-8"))
                osc_cat = get_category(sample_buf[esli_p + 0x12]+ 256*sample_buf[esli_p+0x13])
                osc_snum = sample_buf[esli_p+0x14]+ 256* sample_buf[esli_p+0x15]
                playback_period= sample_buf[esli_p+0x22]+ 256* sample_buf[esli_p+0x23]
                playback_volume = sample_buf[esli_p+0x24]+ 256* sample_buf[esli_p+0x25]
                loop = sample_buf[esli_p+0x34] == 0
                
            output_str = output_str + (
                f'{osc_no+1:03d} {osc_name} ({osc_cat})\n'
                f'Sample Num: {osc_snum:04x}\n'
                f'Playback Period: {playback_period:04x}'
                f' Volume: {playback_volume:04x} Loop: {loop}\n'
                )
            f.write(output_str)
            print(output_str,end="")
    
    print("Done.")
    
if __name__ == '__main__':
    main()
