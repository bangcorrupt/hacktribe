#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read e2sSample.all library and split it into single .WAV files with e2 metadata

For file format, see https://github.com/untergeekDE/electribe2-docs/blob/main/e2sSample-all-file-format.md
Created on Fri Dec 30 00:31:16 2022

@author: jan
"""

import argparse
import os
import re

# os.chdir("..")

# Using bangcorrupt's e2all2pat.py script as a base.

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
                  'User']
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

def main():        
    explanation = """This script reads a sample dump library and
        outputs each sample as a .WAV file followed by Korg's looping metadata.
        These files can be imported individually using the DATA UTILITY menu. """
    parser = argparse.ArgumentParser(epilog=explanation)    
    parser.add_argument("-s", "--sample", dest='sample_file', help="path/to/input/e2sSample.all")
    parser.add_argument("-o", "--outdir", dest='out_dir', help="path/to/output/")
    args = parser.parse_args()
    
    sample_file = './e2sSample.all'
    out_dir = "./output"

    if args.sample_file:
        sample_file = args.sample_file
    if args.out_dir:
        out_dir = args.out_dir
        
    # Start reading sample file into memory
    try:
        with open(sample_file, 'rb') as f:
            buffer =  bytearray(f.read())   
    except:
        print("Could not read ",sample_file," into memory. Stopping.")
        return()
    else: 
        print("Samples read from ",sample_file)
    
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    os.chdir(out_dir)
    # Copy pointers to all the samples 
    pointers = get_pointers(buffer)
    
    for p in pointers:
        # Get length of whole RIFF chunk
        # It's in the 4 bytes just after the "RIFF" marker. 
        RIFF_len = int.from_bytes(buffer[p+4:p+8],'little') + 8
        # Copy the whole thing to a new buffer
        wavebuf = buffer[p:p+RIFF_len]
        # Get the sample number
        sample_no = wavebuf[RIFF_len - 0x494] + wavebuf[RIFF_len - 0x493] * 256
        sample_name = str(wavebuf[RIFF_len - 0x492:RIFF_len - 0x482], encoding="utf-8")
        cat_no = wavebuf[RIFF_len - 0x482] + wavebuf[RIFF_len - 0x481] * 256
        print(sample_no+1,"  ",sample_name," (",get_category(cat_no),") len: ",len(wavebuf))
        # Create file name removing all non-alphanumeric chars via Regex
        # Add 1 to sample no for humans.
        wavefile = re.sub(r'[^\w\s-]','','{0:03d}-{1:s}'.format(sample_no+1,sample_name))
        with open(str(wavefile) + '.wav', 'wb') as f:
            f.write(wavebuf)
            
    print("Done - written ",len(pointers)," sample files")
                

if __name__ == '__main__':
    main()
