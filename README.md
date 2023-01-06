# Hacktribe
Electribe 2 hacks, based on sampler firmware version 2.02. Work by [bangcorrupt](https://github.com/bangcorrupt), with some additional scripts and info.

## Features
- Sampling
- Filter types from the E2 Synth version: Electribe, Moog, MS20, Oberheim, Prophet-5, Acid
- Oscillator models: Dual and Oct Saw/Square/Tri/Sine ("Supersaws"!), 2-OP FM, VPM 
- More IFX, grooves, scales
- Import/Export IFX, grooves
- Expanded MIDI implementation
- Custom init pattern
- Supports synth and sampler hardware

If you have an Electribe Sampler, it's all the things you know and love - plus the additional goodies mentioned above. See a list of [demo videos](https://github.com/bangcorrupt/hacktribe/wiki/Features#demo-videos) in the [wiki](https://github.com/bangcorrupt/hacktribe/wiki).

## How To HackTribe your Electribe

There are several ways to turn your Electribe into a Hacktribe: 
- If you have the Sampler version, you can just use [this online Notebook](./scripts/HackTribing_Notebook.ipynb). Follow the step-by-step explanations and execute code online. 
- If you have Python installed on your computer, you can use the scripts (a list of provided scripts can be found below). See **[the hacktribe WIKI.](https://github.com/bangcorrupt/hacktribe/wiki/How-To#Firmware-Patch)**.
- There is also [a shell script](https://github.com/untergeekDE/hacktribe/blob/main/scripts/hacktribe-tutorial.sh) doing the work for you on Linux and OSX machines. 

Everything is fully reversible - you can go back to the Electribe Sampler firmware any time. 

## Python scripts

A list of the Python scripts and utilities provided in the [```/scripts```](./scripts) directory (you usually run them with ```python scriptname.py```, and if you add ```--help```, you will get additional info on how to use them) 

- **e2-firmware-patch.py** - Take e2 Sampler firmware v2.02 file and patch it to HackTribe firmware
- **e2_recode_sample_pat.py** - Takes your existing e2sSample.all sample and .e2sallpat pattern files and rewrites them for use with the HackTribe
- **e2_sample_all_to_wav.py** - Breaks up a e2sSample.all sample dump into individual .WAV files for importing
- **e2all2pat.py** - Breaks up an .e2ssallpat pattern dump into individual .pat files for importing
- **e2pat2all.py** - Fuses individual .pat files into an .e2sallpat file
- **e2pat2syx.py** - .pat Pattern file to MIDI Sysex conversion
- **e2syx2pat.py** - MIDI Sysex to .pat Pattern file conversion
- **e2pat_shift.py** - Changes the oscillator numbers in an .e2sallpat file to sample numbers in user space (obsolete, use e2_recode_sample_pat.py now)
- **e2s_sample_lister.py** - Lists all samples in an .all sample dump file

There are additional scripts for inserting custom groove templates and init patterns, as well as for manipulating/splitting event files, in [bangcorrupt's original repository](https://github.com/bangcorrupt/hacktribe/tree/main/scripts).  

## Sponsor
Hacktribe is free (as in beer) and always will be.  

If you want to support bangcorrupt's project financially, you are most welcome to [become a sponsor](https://github.com/sponsors/bangcorrupt).  

See [How to support hacktribe](https://github.com/bangcorrupt/hacktribe/discussions/63) for more details.

## License
Contents of `patch` directory is not open source and is not covered by the GPL.

All other files licensed AGPL-3.0 unless stated otherwise.
