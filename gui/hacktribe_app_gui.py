from hacktribe_gui_autogen import *
from hacktribe_app_backend import *
from e2_firmware import *

import sys
from pathlib import Path

def main():
    a = HacktribeAppGUI()

class HacktribeAppGUI:

    def __init__(self):
        
        # Initialise backend
        self.be = HacktribeAppBackend()
        
        # Initialise GUI
        self.init_gui()


    def init_gui(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        
        self.ui.edit_src_path.setText(str(self.be.src_path))
        self.ui.edit_patch_path.setText(str(self.be.patch_path))
        self.ui.edit_dest_path.setText(str(self.be.dest_path))
        
        self.ui.browse_src_path.clicked.connect(self.select_src_path)
        self.ui.edit_src_path.textChanged.connect(self.edit_src_path)
        self.ui.browse_patch_path.clicked.connect(self.select_patch_path)
        self.ui.edit_patch_path.textChanged.connect(self.edit_patch_path)
        self.ui.browse_dest_path.clicked.connect(self.select_dest_path)
        self.ui.edit_dest_path.textChanged.connect(self.edit_dest_path)
        self.ui.check_edit_header.clicked.connect(self.select_edit_header)
        self.ui.check_prefix_filename.clicked.connect(self.select_prefix_filename)
        self.ui.patch_firmware.clicked.connect(self.click_patch_firmware)
        
        self.MainWindow.show()
        
        #self.ui.log_text.append('\nHacktribe Editor\n')
        #self.ui.log_text.append('https://github.com/bangcorrupt/hacktribe\n')
        
        sys.exit(self.app.exec())


    def select_src_path(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.ui.edit_src_path.setText(path)

    def edit_src_path(self):
        self.be.src_path = Path(self.ui.edit_src_path.text())
    
    def select_patch_path(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.ui.edit_patch_path.setText(path)

    def edit_patch_path(self):
        self.be.patch_path = Path(self.ui.edit_patch_path.text())
   
    def select_dest_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        self.ui.edit_dest_path.setText(path)

    def edit_dest_path(self):
        self.be.dest_path = Path(self.ui.edit_dest_path.text())

    def select_edit_header(self):
        self.be.edit_header = self.ui.check_edit_header.isChecked()

    def select_prefix_filename(self):
        self.be.prefix_filename = self.ui.check_prefix_filename.isChecked()


    def click_patch_firmware(self):        
        self.be.apply_firmware_patch()
        

if __name__ == "__main__":
    main()
