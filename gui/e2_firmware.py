import bsdiff4
import hashlib

# E2 Firmware class
# data is bytearray of firmware update file (including header)
class E2Firmware:
    
    hash_dict = {'Electribe 2 Sampler v2.02': '1d0f0689d5a12c8a8bde9f821f2a59adc5f6cd6012ddb201ebb192b72468a646'}
    
    def __init__(self, data):        
        self.data = data
        
        # Check hash for known versions

    # Applies patch to firmware data, modifying in place
    # p is patch as bytes
    def apply_patch(self, p):
        self.data = bytearray(bsdiff4.patch(bytes(self.data), p))
        
    # Modifies header to allow installation over factory firmware
    def modify_header(self, device='synth'):

        if device == 'synth':
            self.data[0x12] = 0x00
            self.data[0x2e] = 0x23 
        
        elif device == 'sampler':
            self.data[0x12] = 0x53
            self.data[0x2e] = 0x24 
    
    
    def check_hash(self, targ_hash):
        if self.get_digest(self.data) == targ_hash:
            return True
        else:
            return False


    # Get sha256 hash of bytes
    # byt is bytes to be hashed
    def get_digest(self, byt):
        h = hashlib.sha256()
        h.update(byt)
        return h.hexdigest()
