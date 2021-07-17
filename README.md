# Hacktribe
Electribe 2 hacks.

## Features
- Sampling
- Filters

## How To
Apply patch to Electribe Sampler firmware version 2.02 only.

    sha256sum -c hash/SYSTEM.VSB.sha
    bspatch SYSTEM.VSB hacked-SYSTEM.VSB patch/hacktribe-2.patch
    sha256sum -c hash/hacked-SYSTEM.VSB.sha

## License
Contents of patch directory not covered by GPL.
