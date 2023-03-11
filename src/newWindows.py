import sys, os
from onlineCamera import Ui_MainWindow
from PyQt5 import QtWidgets

class mywindow2(QtWidgets.QMainWindow): 
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        super(mywindow2, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
                
def main():
    app = QtWidgets.QApplication([])
    application = mywindow2()
    application.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    