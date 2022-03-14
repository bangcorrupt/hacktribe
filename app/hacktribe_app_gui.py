from hacktribe_gui_autogen import *
from hacktribe_app_backend import *
from hacktribe_app_log import *


import sys
from pathlib import Path
import logging

def main():
    # Initialise logging
    HacktribeAppLog()
    
    # Run App GUI
    a = HacktribeAppGUI()

class HacktribeAppGUI:
    def __init__(self):
        
        
        logging.debug('Initialising App')
        
        # Initialise backend
        self.be = HacktribeAppBackend()
        
        # Initialise GUI
        self.init_gui()


    def init_gui(self):
        logging.debug('Initialising GUI')
        
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        
        self.ui.edit_src_path.setText(str(self.be.fw_patcher.src_path))
        self.ui.edit_patch_path.setText(str(self.be.fw_patcher.patch_path))
        self.ui.edit_dest_path.setText(str(self.be.fw_patcher.dest_path))
        
        self.ui.browse_src_path.clicked.connect(self.select_src_path)
        self.ui.edit_src_path.textChanged.connect(self.edit_src_path)
        self.ui.browse_patch_path.clicked.connect(self.select_patch_path)
        self.ui.edit_patch_path.textChanged.connect(self.edit_patch_path)
        self.ui.browse_dest_path.clicked.connect(self.select_dest_path)
        self.ui.edit_dest_path.textChanged.connect(self.edit_dest_path)
        self.ui.check_edit_header.clicked.connect(self.select_edit_header)
        self.ui.check_prefix_filename.clicked.connect(self.select_prefix_filename)
        self.ui.patch_firmware.clicked.connect(self.click_patch_firmware)
        
        # Initialise GUI log display
        self.gui_log = QTextEditLogger(self.ui)
        logging.getLogger().addHandler(self.gui_log)
        self.gui_log.setLevel(logging.INFO)
        
        self.MainWindow.show()
        self.be.welcome_msg()
        
        sys.exit(self.app.exec())


    def select_src_path(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.ui.edit_src_path.setText(path)

    def edit_src_path(self):
        self.be.fw_patcher.src_path = Path(self.ui.edit_src_path.text())
    
    def select_patch_path(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.ui.edit_patch_path.setText(path)

    def edit_patch_path(self):
        self.be.fw_patcher.patch_path = Path(self.ui.edit_patch_path.text())
   
    def select_dest_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory()
        self.ui.edit_dest_path.setText(path)

    def edit_dest_path(self):
        self.be.fw_patcher.dest_path = Path(self.ui.edit_dest_path.text())

    def select_edit_header(self):
        self.be.fw_patcher.edit_header = self.ui.check_edit_header.isChecked()

    def select_prefix_filename(self):
        self.be.fw_patcher.prefix_filename = self.ui.check_prefix_filename.isChecked()


    def click_patch_firmware(self):        
        self.be.fw_patcher.apply_patch()

        
# Logging handler for GUI log_text
class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = parent.log_text
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

if __name__ == "__main__":
    main()
