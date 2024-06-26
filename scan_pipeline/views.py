from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep
from PIL import Image
from .ui.window import Ui_Form
from pathlib import Path
import sys, os

class FileWatcher(QThread):
    folderChanged = pyqtSignal()

    def __init__(self, folder):
        super().__init__()
        self.folder = folder
        self.currentContents = list(Path(self.folder).iterdir())

    def run(self):
        while True:
            newContents = list(Path(self.folder).iterdir())
            if newContents!= self.currentContents:
                self.currentContents = newContents
                self.folderChanged.emit()
            sleep(0.5)

class Window(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self._currentFile = None
        self._queue = []
        self._inputFolder = None
        self._outputFolder = None
        try:
            wd = sys._MEIPASS
        except AttributeError:
            wd = os.getcwd()
        scanLogoPath = os.path.join(wd, "Scan_Pipeline_Logo.png")
        self.setWindowIcon(QtGui.QIcon(scanLogoPath))
        self._setupUI()
        self._connectSignals()
        self._stateNoFiles()

    def _setupUI(self):
        self.setupUi(self)

    def _connectSignals(self):
        self.changeInputButton.clicked.connect(self._chooseInputFolder)
        self.changeOutputButton.clicked.connect(self._chooseOutputFolder)
        self.renameButton.clicked.connect(self._renameFile)
        self.newName.returnPressed.connect(self._renameFile)
        self.deleteButton.clicked.connect(self._deleteFile)
        self.rotateButton.clicked.connect(self._rotateImage)
        self.reloadButton.clicked.connect(self._reloadImage)

    def _startFileWatcher(self):
        if self._inputFolder:
            self.fileWatcherThread = FileWatcher(self._inputFolder)
            self.fileWatcherThread.folderChanged.connect(self._loadInputFiles)
            self.fileWatcherThread.start()

    def _chooseInputFolder(self):
        self._inputFolder = Path(QFileDialog.getExistingDirectory(self, "Select input folder"))
        self.inputDirLabel.setText(f'Input Directory: {self._inputFolder}')
        self._loadInputFiles()
        self._startFileWatcher()

    def _chooseOutputFolder(self):
        self._outputFolder = Path(QFileDialog.getExistingDirectory(self, "Select output folder"))
        self.outputDirLabel.setText(f'Output Directory: {self._outputFolder}')
        if self._outputFolder == Path("."):
            self._outputFolder = None
        self.outputDirLabel.setText(f'Output Directory: {self._outputFolder}')

    def _checkImage(self, path:Path):
        try:
            Image.open(path)
            return True
        except:
            return False

    def _loadInputFiles(self):
        files = self._inputFolder.iterdir()
        self._queue = [f for f in files if self._checkImage(f)]
        if len(self._queue) > 0:
            self._nextFile()
        else:
            self._stateNoFiles()

    def _nextFile(self):
        self.newName.setText('')
        if len(self._queue) == 0:
            self._loadInputFiles()
        else:
            self._stateFilesLoaded()
            self._currentFile = self._queue.pop(0)
            newImage = QPixmap(str(self._currentFile))
            w, h = self.imageLabel.width(), self.imageLabel.height()
            self.imageLabel.setPixmap(newImage.scaled(w, h, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def _renameFile(self):
        if self._outputFolder is not None:
            if self.newName.text():
                if not Path.exists(self._outputFolder.joinpath(f'{self.newName.text()}{self._currentFile.suffix}')):
                    self._currentFile.rename(self._outputFolder.joinpath(f'{self.newName.text()}{self._currentFile.suffix}'))
                else:
                    count = 1
                    while True:
                        if not Path.exists(self._outputFolder.joinpath(f'{self.newName.text()}_{count}{self._currentFile.suffix}')):
                            self._currentFile.rename(self._outputFolder.joinpath(f'{self.newName.text()}_{count}{self._currentFile.suffix}'))
                            break
                        else:
                            count += 1
                self._nextFile()
        else:
            self.outputDirLabel.setText('Please select output folder. -->')

    def _stateNoFiles(self):
        self.imageLabel.setText('No more files in input folder.')
        self._currentFile = None
        self.newName.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.rotateButton.setEnabled(False)
        self.reloadButton.setEnabled(False)
    
    def _stateFilesLoaded(self):
        self.newName.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.rotateButton.setEnabled(True)
        self.reloadButton.setEnabled(True)

    def _validatePrefixChars(self):
        #check for characters that are not allowed in file names
        prefix = self.newName.text()
        invalidCharacters = '"\/:*?"<>|'
        for i in invalidCharacters:
            if i in prefix:
                self._spawnMessageBox(
                    "Invalid Prefix",
                    f"The prefix cannot contain the following characters: {invalidCharacters}"
                )
                self.newName.clear()
                self.newName.setFocus(True)
                break

    def _spawnMessageBox(self, title, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec_()

    def _deleteFile(self):
        if self._currentFile != None:
            self._currentFile.unlink()
            self._nextFile()

    def _rotateImage(self):
        rotated = Image.open(self._currentFile).rotate(90, expand=True)
        rotated.save(self._currentFile)
        self._reloadImage()

    def _reloadImage(self):
        updatedImage = QPixmap(str(self._currentFile))
        w, h = self.imageLabel.width(), self.imageLabel.height()
        self.imageLabel.setPixmap(updatedImage.scaled(w, h, QtCore.Qt.AspectRatioMode.KeepAspectRatio))