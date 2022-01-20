import bsdiff4
import hashlib
import logging


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    b = bytes(0x100)   
    fw = E2Firmware(b)


# E2 Firmware class
# data is bytearray of firmware update file (including header)
class E2Firmware:
    
    hash_dict = {'Electribe 2 Sampler v2.02': '1d0f0689d5a12c8a8bde9f821f2a59adc5f6cd6012ddb201ebb192b72468a646'}
    
    def __init__(self, data):        
        self.data = bytearray(data)
  

if __name__ == "__main__":
    main()
