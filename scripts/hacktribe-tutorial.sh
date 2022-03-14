#!/bin/bash

# Hacktribe firmware patch interactive tutorial
#
# See https://github.com/bangcorrupt/hacktribe for details.

# This tutorial will help you learn how to run a few bash commands and a python script.
# For best results, read everything, 
# run each command separately and pay attention to the output.
# 
# You can use a terminal on your local Linux machine, 
# or, on replit.com click 'Shell' (next to 'Console', either below or to the right)
# to access a shell here in your browser.
#
# If you're viewing this on replit.com and just want to see the end result, 
# click [>Run] at top of the screen to run all the commands automatically.
# Read the output in the 'Console' and check the files on the left.
#
# Anything starting with a '#' character is a comment and ignored by the shell 
# (you don't need to type these).  
# We can use comments to disable a command (see line 66 below).
#
# If you're running this on your local machine, you will need to install git, python and pip.
#
# Happy hacking!


# First we need to download some files.  Clone the repo, including all submodules:
git clone --recursive https://github.com/bangcorrupt/hacktribe.git

# Then change directory to the 'hacktribe' directory we just downloaded:
cd hacktribe

# Next we need to download the factory firmware.  
# This is proprietary and copyrighted.  
# Please only download it for yourself and do not distribute it.  
# 
# 'wget' command can be used to download files if we know the URL:
wget https://cdn.korg.com/us/support/download/files/0b87bcd3112fbb8c0ad7b0f55e618837.zip

# Unzip the zip archive we just downloaded to access the files inside:
unzip 0b87bcd3112fbb8c0ad7b0f55e618837.zip

# Move the firmware update file 'SYSTEM.VSB' to our current directory '.' :
mv electribe_sampler_system_v202/SYSTEM.VSB .

# Now we have all the files in the right places.

# Next, make sure the required python packages are installed:
pip install argparse bsdiff4

# Now we are ready to run the firmware patching script.
# This will apply the hacktribe patch to the factory firmware,
# then check the sha256 hash of the patched file.
# If the hashes match, you have the same file I tested.
# If not, you will get a scary error message saying 'patch failed' or something.
#
# If you're installing hacktribe to a factory synth (grey or blue) 
# for the first time, we need to modify the update file header as well.
# (If you already have a previous version of hacktribe installed, this is not necessary).
#
# EITHER: Run the firmware patching script for synth, using '-e' flag to modify header:
python scripts/e2-firmware-patch.py -e

# OR: Run the firmware patching script for sampler/hacktribe, no flags necessary:
# python scripts/e2-firmware-patch.py

# Everything is done now, the rest is just moving files and tidying up.

# Move up one directory:
cd ..

# Move the patched firmware to our current directory:
mv hacktribe/hacked-SYSTEM.VSB .

# If you're running this on replit.com,
# now is a good time to download any files you want to keep.
# <-- Check the 'Files' pane on the left.

# See https://github.com/bangcorrupt/hacktribe/discussions/41 if you are having difficulties
