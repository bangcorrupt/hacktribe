from e2sysex import *

# Read the Secondary Bootloader (SBL) from On-Chip RAM
#   This is not the Application Image Script (AIS) stored in the flash
#   Do not write this data to flash memory

e = E2Sysex()

print('Reading SBL from On-Chip RAM')
b = e.read_cpu_ram(0x80000000, 0x1c000)

path = 'e2-bootloader.bin'
with open(path, 'wb') as f:
    f.write(b)

print('Bootloader saved to', path)
print('Do not write this data to flash memory')
