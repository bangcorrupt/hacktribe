import e2_formats as fmt

from pathlib import Path
import hashlib
import bsdiff4
import logging


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    fp = FirmwarePatcher()

class FirmwarePatcher:
    def __init__(self):
        self.root_path = Path('../')
        self.src_path = self.root_path / 'SYSTEM.VSB'
        self.patch_path = self.root_path / 'patch/hacktribe-2.patch'
        self.dest_path = self.root_path
        self.src_hash_path = self.root_path / 'hash/SYSTEM.VSB.sha'
        self.targ_hash_path = self.root_path / 'hash/hacked-SYSTEM.VSB.sha'
        self.edit_header = False
        self.prefix_filename = True

    def apply_patch(self):
        logging.debug('Apply firmware patch')
        
        # Open firmware file
        if self.src_path.is_file():
            with open(self.src_path, 'rb') as f:
                src = f.read()
        else:
            logging.error('File not found: ' + str(self.src_path))
            logging.warning('Source file not found\n')
            return
     
        # Get source hash string
        if self.src_hash_path.is_file():
            with open(self.src_hash_path, 'r') as f:
                source_hash = f.readlines()[0].split()[0]
        else:
            logging.error('File not found: ' + str(self.src_hash_path))
            logging.warning('Source hash file not found\n')
            return
        
        # Check source file hash        
        if not self.check_hash(src, source_hash):
            logging.error('Incorrect source file.')
            logging.warning('Electribe 2 Sampler firmware version 2.02 only.\n')
            return
        else:
            logging.info('Electribe 2 Sampler firmware version 2.02 found.\n')
                     
        # Open patch file
        if self.patch_path.is_file():
            with open(self.patch_path, 'rb') as f:
                p = f.read()
        else:
            logging.error('File not found: ' + str(self.patch_path))
            logging.warning('Patch file not found\n')
            return
        
        # Apply patch
        logging.info('Applying patch...')
        patched = bsdiff4.patch(src, p)
        
        # Modify header
        if self.edit_header:
            self.targ_hash_path = self.root_path / 'hash/modified-hacked-SYSTEM.VSB.sha'
            logging.info('Modifying header...')
            fw = fmt.system_vsb.parse(patched)
            fw.head.dev_id = 0x123
            fw.head.dev_name = 'E2'
            patched = fmt.system_vsb.build(fw)                    
        else:
            self.targ_hash_path = self.root_path / 'hash/hacked-SYSTEM.VSB.sha'
        
        # Get target hash string
        if self.targ_hash_path.is_file():
            with open(self.targ_hash_path, 'r') as f:
                target_hash = f.readlines()[0].split()[0]   
        else:
            logging.error('File not found: ' + str(self.targ_hash_path))
            logging.warning('Target hash file hash not found\n')
            return
                
        # Check hash
        logging.info('Checking hash...\n')
        if self.check_hash(patched, target_hash):
            
            if self.prefix_filename:
                dest_file = 'hacked-SYSTEM.VSB'
            else:
                dest_file = 'SYSTEM.VSB'
           
            # Save patched firmware to destination path
            dest = self.dest_path / dest_file 
            logging.info('Saving patched firmware to ' + str(dest) + '\n')
            
            # ADD - Warn before overwrite
            # ADD - Prompt to create path if parent directory not found
            with open(dest, 'wb') as f:
                f.write(patched)
            logging.info('Firmware patched successfully.')        
        
        else:
            logging.error('Hash check failed')
            logging.warning('Patch failed.')

        logging.info('-------------------------------------------------')


    def check_hash(self, data, targ_hash):
        if self.get_digest(data) == targ_hash:
            return True
        else:
            return False
    
    # Get sha256 hash of bytes
    # byt is bytes to be hashed
    def get_digest(self, byt):
        h = hashlib.sha256()
        h.update(byt)
        return h.hexdigest()


if __name__ == "__main__":
    main()
