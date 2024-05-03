import sys, os
from PyQt5.QtWidgets import QApplication
from .views import Window
try:
    import pyi_splash
except ImportError:
    pass

def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    try:
        pyi_splash.close()
    except:
        pass
    sys.exit(app.exec_())