import sys
from src.launch import mywindow
from PyQt5 import  QtWidgets

def main():
    while True:
        app = QtWidgets.QApplication([])
        application = mywindow()
        application.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()