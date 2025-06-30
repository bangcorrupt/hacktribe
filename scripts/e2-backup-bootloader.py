import sys
import logging

from e2sysex import *

logging.basicConfig(level=logging.DEBUG)

in_port = None
out_port = None

if len(sys.argv) > 1:
    in_port = sys.argv[1]

if len(sys.argv) > 2:
    out_port = sys.argv[2]

# Read the Secondary Bootloader (SBL) from On-Chip RAM
#   This is not the Application Image Script (AIS) stored in the flash
#   Do not write this data to flash memory

e = E2Sysex(in_port, out_port)

print("Reading SBL from On-Chip RAM")
b = e.read_cpu_ram(0x80000000, 0x1C000)

path = "e2-bootloader.bin"
with open(path, "wb") as f:
    f.write(b)

print("Bootloader saved to", path)
print("Do not write this data to flash memory")
