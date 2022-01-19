from e2_firmware import *
from pathlib import Path

def main():
    be = HacktribeAppBackend()


# ADD - Separate classes for patcher, groove editor, etc...
# ADD - logging
class HacktribeAppBackend:
    def __init__(self):
        
        self.welcome_msg()
        
        self.root_path = Path('../')
        self.src_path = self.root_path / 'SYSTEM.VSB'
        self.patch_path = self.root_path / 'patch/hacktribe-2.patch'
        self.dest_path = self.root_path
        self.src_hash_path = self.root_path / 'hash/SYSTEM.VSB.sha'
        self.targ_hash_path = self.root_path / 'hash/hacked-SYSTEM.VSB.sha'
        self.edit_header = False
        self.prefix_filename = True


    def welcome_msg(self):
        print('\nHacktribe Editor\n')
        print('https://github.com/bangcorrupt/hacktribe\n')

    def apply_firmware_patch(self):
        
        print('Apply firmware patch')
        
        # Open firmware file
        if self.src_path.is_file():
            with open(self.src_path, 'rb') as f:
                src = bytearray(f.read())
        else:
            #  ADD - Error dialog box
            print('File not found: ' + str(self.src_path))
            #self.ui.log_text.append('File not found: ' + str(self.src_path))
            #self.ui.log_text.append('ERROR: Source file not found\n')
            return
        
        # Instantiate firmware object
        fw = E2Firmware(src)
        
        
        # Get source hash string
        if self.src_hash_path.is_file():
            with open(self.src_hash_path, 'r') as f:
                source_hash = f.readlines()[0].split()[0]
        else:
            #  ADD - Error dialog box
            print('File not found: ' + str(self.src_hash_path))
            #self.ui.log_text.append('File not found: ' + str(self.src_hash_path))
            #self.ui.log_text.append('ERROR: Source file hash not found\n')
            return
        
        # Check source file hash        
        if not fw.check_hash(source_hash):
            print('ERROR: Incorrect source file.')
            #self.ui.log_text.append('ERROR: Incorrect source file.')
            #self.ui.log_text.append('Electribe 2 Sampler firmware version 2.02 only\n.')
            return
        else:
            print('Electribe 2 Sampler firmware version 2.02 found.\n')
            #self.ui.log_text.append('Electribe 2 Sampler firmware version 2.02 found.\n')
                
        
        # Open patch file
        if self.patch_path.is_file():
            with open(self.patch_path, 'rb') as f:
                p = f.read()
        else:
            #  ADD - Error dialog box
            print('File not found: ' + str(self.patch_path))
            #self.ui.log_text.append('File not found: ' + str(self.patch_path))
            #self.ui.log_text.append('ERROR: Patch file not found\n')
            return
        
        # Apply patch and check hash
        #self.ui.log_text.append('Applying patch...\n')
        fw.apply_patch(p)

        
        if self.edit_header:
            self.targ_hash_path = self.root_path / 'hash/modified-hacked-SYSTEM.VSB.sha'        
            #self.ui.log_text.append('Modifying header...\n')
            fw.modify_header()
        
        else:
            self.targ_hash_path = self.root_path / 'hash/hacked-SYSTEM.VSB.sha'
        
        # Get target hash string
        if self.targ_hash_path.is_file():
            with open(self.targ_hash_path, 'r') as f:
                target_hash = f.readlines()[0].split()[0]   
        else:
            # ADD - Error dialog box
            print('File not found: ' + str(self.targ_hash_path))
            #self.ui.log_text.append('File not found: ' + str(self.targ_hash_path))
            #self.ui.log_text.append('ERROR: Target hash file hash not found\n')
            return
        
        
        # Check hash
        #self.ui.log_text.append('Checking hash...\n')
        if fw.check_hash(target_hash):
            
            if self.prefix_filename:
                dest_file = 'hacked-SYSTEM.VSB'
            else:
                dest_file = 'SYSTEM.VSB'
            
            dest = self.dest_path / dest_file
            # Save patched firmware to destination path
            #self.ui.log_text.append('Saving patched firmware to ' + str(dest) + '\n')
            
            # ADD - Warn before overwrite
            # ADD - Prompt to create path if parent directory not found
            with open(dest, 'wb') as f:
                f.write(fw.data)
            
            #self.ui.log_text.append('Firmware patched successfully.')
        
        else:
            print('ERROR: Patch failed.')
            #self.ui.log_text.append('ERROR: Patch failed.')

        #self.ui.log_text.append('-------------------------------------------------')
        
        
if __name__ == "__main__":
    main()
