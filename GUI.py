import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from Okno_obrazy_test import Ui_MainWindow
from Final_functions import Bottle_inspection
import cv2 as cv

class Main_Window(QtWidgets.QMainWindow, QtWidgets.QFileDialog):

    def __init__(self, *args, **kwargs):
        super(*args, **kwargs).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.f_name = "Zdjecia/w_z_e_11.jpg"
        self.is_browse_clicked()
        self.is_start_clicked()
    
    def is_start_clicked(self):
        self.ui.start_button.clicked.connect(self.start_inspection)
        
    def start_inspection(self):
        self.ui.log_box.clear()
        file_name = self.f_name
        try:
            input_img, processed_img = Bottle_inspection(file_name, self.add_log)
            inp_img = self.convert_cv_qt(input_img)
            proc_img = self.convert_cv_qt(processed_img)
            self.ui.inp_img.setPixmap(inp_img)
            self.ui.proc_img.setPixmap(proc_img)
        except:
            self.add_log("A problem occurde.\nPlease pick other image!")
    
    def is_browse_clicked(self):
        self.ui.browse.clicked.connect(self.browse_files)
    
    def browse_files(self):
        f_name = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", "Zdjecia")
        self.ui.file_name.setText(str(f_name[0]))
        self.f_name = str(f_name[0])
        
    def add_log(self, log: str):
        self.ui.log_box.append(log)
    
    def convert_cv_qt(self, cv_img):
        rgb_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytse_per_line = ch * w
        p = QtGui.QImage(rgb_img.data, w, h, bytse_per_line, QtGui.QImage.Format_RGB888)

        return QtGui.QPixmap.fromImage(p)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = Main_Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()