# Hacktribe
Electribe 2 hacks.

## Features
- Sampling
- All filters
- Dual, Octave, Ring Mod, Chip oscillators
- Hardware agnostic

## How To
Apply patch to Electribe Sampler firmware version 2.02 only.

    sha256sum -c hash/SYSTEM.VSB.sha
    bspatch SYSTEM.VSB hacked-SYSTEM.VSB patch/hacktribe-2.patch
    sha256sum -c hash/hacked-SYSTEM.VSB.sha

Edit header if currently running synth firmware.
    
    python scripts/e2-header.py hacked-SYSTEM.VSB

Use `samples/hacktribe-blank-e2sSample.all` to free up sampling time.

## License
Contents of patch directory not covered by GPL.
