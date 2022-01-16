from hacktribe_gui import *
from e2_firmware import *

import sys
from pathlib import Path

def main():
    a = HacktribeApp()

class HacktribeApp:

    def __init__(self):
        
        self.root_path = Path('../')
        self.src_path = self.root_path / 'SYSTEM.VSB'
        self.patch_path = self.root_path / 'patch/hacktribe-2.patch'
        self.dest_path = self.root_path
        self.src_hash_path = self.root_path / 'hash/SYSTEM.VSB.sha'
        self.targ_hash_path = self.root_path / 'hash/hacked-SYSTEM.VSB.sha'
        self.edit_header = False
        self.prefix_filename = True
        
        self.init_gui()
        

        
    def init_gui(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        
        self.ui.edit_src_path.setText(str(self.src_path))
        self.ui.edit_patch_path.setText(str(self.patch_path))
        self.ui.edit_dest_path.setText(str(self.dest_path))
        
        self.ui.browse_src_path.clicked.connect(self.select_src_path)
        self.ui.edit_src_path.textChanged.connect(self.edit_src_path)
        self.ui.browse_patch_path.clicked.connect(self.select_patch_path)
        self.ui.edit_patch_path.textChanged.connect(self.edit_patch_path)
        self.ui.browse_dest_path.clicked.connect(self.select_dest_path)
        self.ui.edit_dest_path.textChanged.connect(self.edit_dest_path)
        self.ui.check_edit_header.clicked.connect(self.select_edit_header)
        self.ui.check_prefix_filename.clicked.connect(self.select_prefix_filename)
        self.ui.patch_firmware.clicked.connect(self.apply_firmware_patch)
        
        self.MainWindow.show()
        
        self.ui.log_text.append('\nHacktribe firmware patcher.\n')
        self.ui.log_text.append('https://github.com/bangcorrupt/hacktribe\n')
        
        sys.exit(self.app.exec())


    def select_src_path(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.ui.edit_src_path.setText(path)

    def edit_src_path(self):
        self.src_path = Path(self.ui.edit_src_path.text())
    
    def select_patch_path(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.ui.edit_patch_path.setText(path)

    def edit_patch_path(self):
        self.patch_path = Path(self.ui.edit_patch_path.text())
   
    def select_dest_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        self.ui.edit_dest_path.setText(path)

    def edit_dest_path(self):
        self.dest_path = Path(self.ui.edit_dest_path.text())

    def select_edit_header(self):
        self.edit_header = self.ui.check_edit_header.isChecked()

    def select_prefix_filename(self):
        self.prefix_filename = self.ui.check_prefix_filename.isChecked()


    def apply_firmware_patch(self):        
        # Open firmware file
        with open(self.src_path, 'rb') as f:
            src = bytearray(f.read())
        
        # Instantiate firmware object
        fw = E2Firmware(src)
        
        
        # Get source hash string
        with open(self.src_hash_path, 'r') as f:
            source_hash = f.readlines()[0].split()[0]
        
        # Check source file hash        
        if not fw.check_hash(source_hash):
            self.ui.log_text.append('ERROR: Incorrect source file.')
            self.ui.log_text.append('Electribe 2 Sampler firmware version 2.02 only.')
            return
        else:
            self.ui.log_text.append('Electribe 2 Sampler firmware version 2.02 found.\n')
                
        
        # Open patch file
        with open(self.patch_path, 'rb') as f:
            p = f.read()
        
        # Apply patch and check hash
        self.ui.log_text.append('Applying patch...\n')
        fw.apply_patch(p)

        
        if self.edit_header:
            self.targ_hash_path = self.root_path / 'hash/modified-hacked-SYSTEM.VSB.sha'        
            self.ui.log_text.append('Modifying header...\n')
            fw.modify_header()
        
        else:
            self.targ_hash_path = self.root_path / 'hash/hacked-SYSTEM.VSB.sha'
        
         # Get target hash string
        with open(self.targ_hash_path, 'r') as f:
            target_hash = f.readlines()[0].split()[0]       
        
        
        # Check hash
        self.ui.log_text.append('Checking hash...\n')
        if fw.check_hash(target_hash):
            
            if self.prefix_filename:
                dest_file = 'hacked-SYSTEM.VSB'
            else:
                dest_file = 'SYSTEM.VSB'
            
            dest = self.dest_path / dest_file
            # Save patched firmware to destination path
            self.ui.log_text.append('Saving patched firmware to ' +str(dest)+ '\n')
            with open(dest, 'wb') as f:
                f.write(fw.data)
            
            self.ui.log_text.append('Firmware patched successfully.')
            
            self.ui.log_text.append('-------------------------------------------------')
        
        else:
            self.ui.log_text.append('ERROR: Patch failed.')


if __name__ == "__main__":
    main()
