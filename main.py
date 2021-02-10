from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QMenu, QMessageBox, QMainWindow
import sys
import os
import shutil


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setuiUp()
        self.nextPath = None
        self.previousPath = []
        self.fullPath = []
        self.fileForCopyOrCut = None
        # if cutFile is True program will cut the fileForCopyOrCut instead of copy it
        self.cutFile = False

    def setuiUp(self):
        self.setWindowTitle("File explorer")
        self.resize(1000, 600)
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setStyleSheet("""
            QMenu{padding:5px;background-color:#fff;}
            QMenu::item::selected{
                background-color:#838485;color:white;
            }
            background-color:#fff;
            border:none;
        """)
        self.centralLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.centralLayout.setSpacing(0)

        self.filePath = QtWidgets.QLineEdit(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.filePath.sizePolicy().hasHeightForWidth())
        self.filePath.setSizePolicy(sizePolicy)
        self.filePath.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.filePath.setFont(font)
        self.filePath.setStyleSheet("border:1px solid #ddd;padding:3px;")
        self.filePath.setPlaceholderText("File path")
        self.filePath.returnPressed.connect(lambda: self.doubleClickedOnFileOrFolderOnFileOrFolder(event=None, path=self.filePath.text()))
        self.centralLayout.addWidget(self.filePath, 0, 0, 1, 1)
        self.mainFrame = QtWidgets.QFrame(self.centralWidget)
        self.mainFrame.setStyleSheet("background-color:white;border:none;")

        self.gridLayout = QtWidgets.QGridLayout(self.mainFrame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)

        # addWidget(self, QWidget, row, column, rowSpan, columnSpan)
        self.centralLayout.addWidget(self.mainFrame, 1, 0, 1, 1)

        self.menuBar = QtWidgets.QMenuBar(self)
        menuFile = QMenu(self.menuBar)
        menuFile.setTitle("File")
        self.setMenuBar(self.menuBar)
        actionExit = QtWidgets.QAction(self)
        actionExit.setText("Exit")
        actionExit.triggered.connect(lambda: sys.exit(0))
        actionExit.setObjectName("actionExit")
        menuFile.addAction(actionExit)
        self.menuBar.addMenu(menuFile)
        self.setCentralWidget(self.centralWidget)
        self.showFiles()

    def showFiles(self, path=QtCore.QDir.rootPath()):
        if path != QtCore.QDir.rootPath():
            for child in self.mainFrame.children():
                if child != self.gridLayout:
                    child.deleteLater()

        frameButtons = QtWidgets.QFrame(self.mainFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(frameButtons.sizePolicy().hasHeightForWidth())
        frameButtons.setSizePolicy(sizePolicy)
        frameButtons.setMinimumHeight(40)
        frameButtons.setStyleSheet("border:none;background-color:#fff;")
        self.btnPrevious = QtWidgets.QPushButton(frameButtons)
        self.btnPrevious.setGeometry(QtCore.QRect(20, 10, 25, 25))
        self.btnPrevious.setIcon(QtGui.QIcon("left-arrow.png"))
        self.btnPrevious.setCursor(QtCore.Qt.PointingHandCursor)
        self.btnPrevious.setIconSize(QtCore.QSize(15, 15))
        self.btnPrevious.clicked.connect(self.previous)

        self.btnNext = QtWidgets.QPushButton(frameButtons)
        self.btnNext.setGeometry(QtCore.QRect(55, 10, 25, 25))
        self.btnNext.setIcon(QtGui.QIcon("right-arrow.png"))
        self.btnNext.setCursor(QtCore.Qt.PointingHandCursor)
        self.btnNext.setIconSize(QtCore.QSize(15, 15))
        self.btnNext.clicked.connect(self.next)

        self.treeView = QtWidgets.QTreeView(self.mainFrame)
        self.treeView.setStyleSheet("border:none;background-color:white;")
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(path)
        self.treeView.setModel(self.model)
        self.treeView.setSortingEnabled(True)
        self.treeView.setAnimated(True)
        self.treeView.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.treeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.treeView.doubleClicked.connect(self.doubleClickedOnFileOrFolder)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.contextMenu)
        self.gridLayout.addWidget(frameButtons, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.treeView, 1, 0, 1, 1)

    def contextMenu(self, position):
        menu = QMenu()
        openFile = menu.addAction("Open")
        menu.addSeparator()
        cut = menu.addAction("Cut")
        copy = menu.addAction("Copy")
        paste = menu.addAction("Paste")
        action = menu.exec_(self.mapToGlobal(position))
        if action == copy:
            # Get current index of the selected item
            index = self.treeView.currentIndex()
            # model.filepath(index) will return a filepath
            self.fileForCopyOrCut = self.model.filePath(index)

            # self.cutFile is a status variable to decide should we copy the file or move it (cut it)
            self.cutFile = False
        if action == paste:
            index = self.treeView.currentIndex()
            dst_Path = self.model.filePath(index)
            # if self.fileForCopyOrCut is None it means there is no selected file to copy
            # or we already copied it
            if self.fileForCopyOrCut is not None:
                if self.cutFile:
                    shutil.move(self.fileForCopyOrCut, dst_Path)
                    # set self.fileForCopyOrCut to None to prevent of moving or coping the file again
                    self.fileForCopyOrCut = None
                    self.showFiles()
                else:
                    shutil.copy(self.fileForCopyOrCut, dst_Path)
                    self.fileForCopyOrCut = None
        if action == cut:
            index = self.treeView.currentIndex()
            self.fileForCopyOrCut = self.model.filePath(index)
            self.cutFile = True
        if action == openFile:
            index = self.treeView.currentIndex()
            self.openFile(path=self.model.filePath(index))

    def openFile(self, path):
        if os.path.isdir(path):
            # self.model is a QFileSystemModel
            # self.model.index() take a 'path' as argument and return the index of it
            self.treeView.setRootIndex(self.model.index(path))
            previous = path.split("/")
            self.fullPath = [p for p in previous if p != '']
            self.previousPath = [p for p in previous if p != '']
        else:
            try:
                # open the file
                os.startfile(path)
            except OSError:
                pass

    def doubleClickedOnFileOrFolder(self, event):
        # event is a QtCore.QModelIndex
        path = self.model.filePath(event)
        self.filePath.setText(path)
        self.openFile(path)

    # Move to the next
    def next(self):
        if self.nextPath is not None:
            nextDir = ""
            for i in range(len(self.fullPath)):
                try:
                    nextDir += self.nextPath[i] + '\\'
                except IndexError:
                    self.nextPath.append(self.fullPath[i])
                    nextDir += self.nextPath[-1] + '\\'
                    break
            textPath = "/".join(self.nextPath) + "/"
            self.filePath.setText(textPath)
            self.treeView.setRootIndex(self.model.index(nextDir))

    def previous(self):
        if self.previousPath:
            if len(self.previousPath) <= 1:
                self.previousPath = []
                self.nextPath = self.previousPath
                self.showFiles()
                self.filePath.setText("")
            else:
                prePath = "\\".join(self.previousPath[0:-1])
                textPath = "/".join(self.previousPath[0:-1])
                self.filePath.setText(textPath)
                self.treeView.setRootIndex(self.model.index(prePath))
                self.previousPath = self.previousPath[0:-1]
                self.nextPath = self.previousPath


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = Window()
    mainWindow.show()
    sys.exit(app.exec_())
