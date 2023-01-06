# e2-scripts

Scripts for dealing with electribe2 files.

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
