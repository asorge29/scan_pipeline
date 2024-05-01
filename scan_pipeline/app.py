import sys, os
from PyQt5.QtWidgets import QApplication
from .views import Window

def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())