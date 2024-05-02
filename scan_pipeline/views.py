from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep
from PIL import Image
from .ui.window import Ui_Form
from pathlib import Path

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
            self.imageLabel.setPixmap(QPixmap(str(self._currentFile)))

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
        
    
    def _stateFilesLoaded(self):
        self.newName.setEnabled(True)

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