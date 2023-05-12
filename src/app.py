from copy import copy
import shutil
from pathlib import Path
from os.path import isfile, isdir, join
import subprocess, os, platform
from PyQt5.QtWidgets import QApplication, QStyle, QAbstractItemView, QLineEdit, QTableView, QSplitter, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QToolButton, QMenu, QWidget, QAction,QMessageBox, QDirModel, QFileSystemModel, QTreeView, QListView, QGridLayout, QFrame, QLabel, QDialogButtonBox, QDialog
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt,QDir, QVariant, QSize, QModelIndex
import sys

class AboutDialog(QDialog):  # 상단바의 help의 about클릭 시 Made by Antonin Desfontaines.를 출력하는 창을 띄우기 위한 클래스
    # QDialog를 상속받아 만들어진 클래스 // QDialog : 짧은 기간의 일을 처리할 때 사용되는 창(ex.경고창, 메시지 팝업창)을 띄우기 위한 PyQt5의 클래스
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel("Made by Antonin Desfontaines.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class App(QMainWindow):  # main application window를 위한 클래스
    def __init__(self, initialDir): 
        super().__init__()

        # Variables
        self.currentDir = initialDir  # pathlib모듈의 Path객체를 받음. main함수에서 App객체를 생성할 때에는 home디렉토리(사용자 폴더)를 인자로 넘겨줌
        self.history = {}
        self.mainExplorer = None  # QListView 클래스 객체를 받는 필드. 파일 목록을 리스트로 보여주기 위함

        # App init
        self.initUI()
    def initUI(self): # UI를 초기화하는 함수
        # Status bar
        self.statusBar() # 상태바를 생성하는 함수
        
        # Dir model
        dirModel = QFileSystemModel() # QFileSystemModel : 파일 시스템의 디렉토리 구조를 표현하는 모델
        dirModel.setFilter(QDir.Dirs | QDir.NoDotAndDotDot) # QDir.Dirs : 디렉토리만 표시하도록 필터링 # QDir.NoDotAndDotDot : "."과 ".."을 표시하지 않도록 필터링 # setFilter : 모델의 필터를 설정하는 함수
        dirModel.setRootPath(QDir.rootPath()) # QDir.rootPath() : 루트 디렉토리의 경로를 반환하는 함수 # setRootPath : 모델의 루트 경로를 설정하는 함수

        # Side explorer
        self.sideExplorer = QTreeView() # QTreeView : QAbstractItemView를 상속받은 클래스. 트리 형태로 데이터를 표시하는 위젯
        self.sideExplorer.setModel(dirModel) # QTreeView의 모델을 dirModel로 설정
        self.sideExplorer.hideColumn(3) #QTreeView의 3번째 열을 숨김
        self.sideExplorer.hideColumn(2) #QTreeView의 2번째 열을 숨김
        self.sideExplorer.hideColumn(1) #QTreeView의 1번째 열을 숨김
        self.sideExplorer.header().hide() #QTreeView의 헤더를 숨김
        self.sideExplorer.clicked.connect(self.navigate) #QTreeView의 아이템을 클릭했을 때 navigate함수를 호출
        self.sideExplorer.setFrameStyle(QFrame.NoFrame) #QTreeView의 테두리를 없앰
        self.sideExplorer.uniformRowHeights = True #QTreeView의 행의 높이를 일정하게 설정

        self.mainModel = QFileSystemModel() #QFileSystemModel : 파일 시스템의 디렉토리 구조를 표현하는 모델
        self.mainModel.setRootPath(QDir.rootPath()) #QDir.rootPath() : 루트 디렉토리의 경로를 반환하는 함수
        self.mainModel.setReadOnly(False) #QFileSystemModel의 읽기 전용 속성을 False로 설정
        self.mainModel.directoryLoaded.connect(self.updateStatus) #QFileSystemModel의 디렉토리가 로드될 때 updateStatus함수를 호출
        # Main explorer
        self.changeView("Details") #changeView함수를 호출하여 QListView를 생성
        
        # Set layout and views
        layout = QVBoxLayout() #QVBoxLayout : 위젯을 수직으로 배치하는 레이아웃 클래스
        layout.setContentsMargins(0, 0, 0, 0) #QVBoxLayout의 여백을 없앰
        
        explorerLayout = QHBoxLayout() #QHBoxLayout : 위젯을 수평으로 배치하는 레이아웃 클래스
        explorerLayout.setContentsMargins(0, 0, 0, 0) #QHBoxLayout의 여백을 없앰

        layout.addLayout(explorerLayout) #QVBoxLayout에 QHBoxLayout을 추가

        self.explorerSplitter = QSplitter(Qt.Horizontal) #QSplitter : 위젯을 분할하여 배치하는 클래스
        self.explorerSplitter.addWidget(self.sideExplorer) #QSplitter에 QTreeView를 추가
        self.explorerSplitter.addWidget(self.mainExplorer) #QSplitter에 QListView를 추가

        self.explorerSplitter.setStretchFactor(1, 2) #QSplitter의 1번째 위젯의 크기를 2배로 설정
        self.explorerSplitter.setSizes([400, 800]) #QSplitter의 크기를 설정
        explorerLayout.addWidget(self.explorerSplitter) #QHBoxLayout에 QSplitter를 추가

        # Top menus
        self.createTopMenu() #createTopMenu함수를 호출하여 상단바를 생성
        self.createActionBar() #createActionBar함수를 호출하여 상단바의 action바를 생성


        # Main widget
        widget = QWidget() #QWidget : 위젯을 생성하는 클래스
        widget.setLayout(layout)  #QVBoxLayout을 위젯의 레이아웃으로 설정
        self.setCentralWidget(widget) #QMainWindow의 중앙 위젯을 설정


        self.setWindowIcon(QIcon('./src/ico/application-sidebar.png')) #QMainWindow의 아이콘을 설정
        self.setLayout(layout) #QMainWindow의 레이아웃을 설정
        self.setGeometry(800,600,600,560) #QMainWindow의 위치와 크기를 설정
        self.navigate(self.mainModel.setRootPath(QDir.homePath())) #QMainWindow의 디렉토리를 homePath로 설정
        self.show() #QMainWindow를 보여줌
    def about(self, event):#상단바의 help의 about클릭 시
        dlg = AboutDialog(self)
        if dlg.exec():#exec() : QDialog의 메소드. QDialog의 창을 띄우는 메소드
            print("Success!")
        else: # Cancel 출력 -창의 x버튼을 누르면
            print("Cancel!")
    def createActionBar(self):#상단바의 action바를 위한 메소드 - 상위 디렉토리로 가거나 현제 디렉토리를 표시하거나 검색하는 기능
        
        self.toolbar = self.addToolBar("actionToolBar")
        self.toolbar.setMovable(False) #상단의 action바를 움직일 수 없게 설정
        self.toolbar.setFloatable(False) #상단의 action바를 떠다니지 않게 설정

        self._navigateBackButton = QToolButton() #이전 디렉토리로 가는 버튼이나 이것과 connect된 메소드가 없어서 작동 X
        self._navigateBackButton.setIcon(QIcon("./src/ico/arrow-180.png"))
        self._navigateBackButton.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self._navigateForwardButton = QToolButton() #다음 디렉토리로 가는 버튼이나 이것과 connect된 메소드가 없어서 작동 X
        self._navigateForwardButton.setIcon(QIcon("./src/ico/arrow.png"))
        self._navigateForwardButton.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self._navigateUpButton = QToolButton() #상위 디렉토리로 가는 버튼
        self._navigateUpButton.setIcon(QIcon("./src/ico/arrow-090.png"))
        self._navigateUpButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._navigateUpButton.clicked.connect(self.navigateUp) #클릭 시 navigateUp메소드 실행

        splitter = QSplitter(Qt.Horizontal) #상단바의 action바에 들어갈 위젯들을 위한 splitter

        self.addressBar = QLineEdit() #현재 디렉토리를 표시하는 위젯
        self.addressBar.setMaxLength(255)
        splitter.addWidget(self.addressBar)

        self.searchField = QLineEdit()#검색을 위한 위젯 - 작동 x
        self.searchField.setPlaceholderText("Search")
        splitter.addWidget(self.searchField)

        splitter.setStretchFactor(10    , 1)
        splitter.setSizes([500, 200])


        self.toolbar.addWidget(self._navigateBackButton) #상단바의 action바에 위젯들을 추가
        self.toolbar.addWidget(self._navigateForwardButton)
        self.toolbar.addWidget(self._navigateUpButton)
        self.toolbar.addWidget(splitter)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }")

    def selectAll(self, event):#상단바의 Edit의 selectAll 클릭시, QListView클래스의 selectAll함수 이용.
        self.mainExplorer.selectAll()
    def unselectAll(self):#상단바의 Edit의 unselectAll 클릭시, QListView클래스의 selectionModel함수 이용.
        self.mainExplorer.selectionModel().clearSelection()
    def navigate(self, index):
        self.currentDir = self.mainModel.fileInfo(index).absoluteFilePath()
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))
        self.setWindowTitle(os.path.basename(self.currentDir))
        self.addressBar.setText(self.currentDir)
    def navigateUp(self, event):
        self.currentDir = os.path.dirname(self.currentDir)
        self.navigate(self.mainModel.setRootPath(self.currentDir))
    def navigateFromSideTree(self, selected, unselected):
        print(selected)
    def deleteFiles(self, event):
        reply = QMessageBox.question(self, 'Delete', 'Are you sure you sure you want to delete those elements ?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if  reply == QMessageBox.Yes:
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes();
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                filePath = join(self.currentDir, fileName)
                if os.path.exists(filePath):
                    try:
                        if isdir(filePath):
                            shutil.rmtree(filePath)
                        elif isfile(filePath):
                            os.remove(filePath) 
                        self.mainModel.remove(file)
                    except OSError:
                        print("failed to delete: " + filePath)
                        pass
                else:
                    self.mainModel.remove(file)
    def changeView(self, view):
        if(view == "List"):
            if type(self.mainExplorer) is not QListView:
                self.mainExplorer = QListView()

            self.mainExplorer.setViewMode(QListView.ListMode)
            self.mainExplorer.setIconSize(QSize(64, 64))
        elif(view == "Icons"):
            if type(self.mainExplorer) is not QListView:
                self.mainExplorer = QListView()

            self.mainExplorer.setViewMode(QListView.IconMode)
            self.mainExplorer.setWordWrap(True)
            self.mainExplorer.setIconSize(QSize(64, 80))
            # self.mainExplorer.setGridSize(QSize(150, 150));
            self.mainExplorer.setUniformItemSizes(True)
        elif(view == "Details"):
            self.mainExplorer = QTableView()
            self.mainExplorer.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.mainExplorer.setSelectionMode(QAbstractItemView.ExtendedSelection)

            self.mainExplorer.verticalHeader().hide()
            self.mainExplorer.setShowGrid(False)
            self.mainExplorer.horizontalHeader().setSectionsMovable(True)
            self.mainExplorer.horizontalHeader().setHighlightSections(False)
            self.mainExplorer.setFrameStyle(QFrame.NoFrame)
            self.mainExplorer.setSortingEnabled(True)
            self.mainExplorer.setEditTriggers(QAbstractItemView.EditKeyPressed)

        # Common
        self.mainExplorer.doubleClicked.connect(self.onDoubleClick)
        self.mainExplorer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mainExplorer.customContextMenuRequested.connect(self.contextItemMenu)
        self.mainExplorer.setModel(self.mainModel)

        if hasattr(self, "explorerSplitter"):
            self.explorerSplitter.replaceWidget(1, self.mainExplorer)
            self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))


    def updateStatus(self, path):
        status = str(self.mainModel.rowCount(self.mainModel.index(path))) + " elements"
        selectedCount = len(self.mainExplorer.selectionModel().selectedIndexes())
        if selectedCount > 0:      
            status += " | " + str(selectedCount) + " elements selected"
        
        self.statusBar().showMessage(status)
    def onKeyPress(self, key):
        if key.key() == Qt.Key_Delete:
            self.deleteFiles(None)
    def onDoubleClick(self, event):
        itemPath = self.mainModel.fileInfo(event)

        if isdir(itemPath):
            self.navigate(event)
        elif isfile(itemPath):
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', itemPath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(itemPath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', itemPath))
    def contextItemMenu(self, position):
        index = self.mainExplorer.indexAt(position)
        if (index.isValid()):
            menu = QMenu()
            cutAction = menu.addAction("Cut")
            cutAction.triggered.connect(self.cutFiles)

            deleteAction = menu.addAction("Delete")
            deleteAction.triggered.connect(self.deleteFiles)
            
            renameAction = menu.addAction("Rename")
            renameAction.triggered.connect(self.renameFile)

            copyAction = menu.addAction("Copy")
            copyAction.triggered.connect(self.copyFiles)
            menu.addSeparator()
            # menu.addSeparator()
            # menu.addAction("Properties")
            action = menu.exec_(QCursor.pos())
        else:
            menu = QMenu()
            menu.addAction("Refresh")
            menu.addSeparator()
            pasteAction = menu.addAction("Paste")
            pasteAction.triggered.connect(self.pasteFiles)

            action = menu.exec_(QCursor.pos())
    def cutFiles(self, event):#관련 QAction이 trigger되었을때 connect되도록 되어있지 않아 무쓸모
        self.selectedFiles = self.mainExplorer.selectionModel().selectedIndexes()
    def copyFiles(self, event):#관련 QAction이 trigger되었을때 connect되도록 되어있지 않아 무쓸모
        self.selectedFiles = self.mainExplorer.selectionModel().selectedIndexes()
    def pasteFiles(self, event):#관련 QAction이 trigger되었을때 connect되도록 되어있지 않아 무쓸모
        for file in self.selectedFiles:
            fileName = self.mainModel.itemData(file)[0]
            filePath = join(self.currentDir, fileName)
            if os.path.exists(filePath):
                try:
                    shutil.copy(filePath, self.currentDir)
                    # self.mainModel.remove(file)
                except OSError:
                    print("failed to copy: " + filePath)
                    pass
            else:
                self.mainModel.remove(file)
    def renameFile(self, event):#선택된 파일을 mainExplorer.selectionModel().selectedIndexes()로 받아와서 이름을 바꿔줌
        selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes();
        for file in selectedIndexes:
            fileName = self.mainModel.itemData(file)[0]
            filePath = join(self.currentDir, fileName)
            if os.path.exists(filePath):
                self.mainExplorer.edit(file)

    def createTopMenu(self):
        # Add menus
        menuBar = self.menuBar()  # 상단 메뉴바

        fileMenu = menuBar.addMenu('&File')  # 메뉴바에 File Edit View Go Help 추가
        editMenu = menuBar.addMenu("&Edit")
        viewMenu = menuBar.addMenu("&View")
        goMenu = menuBar.addMenu("&Go")
        helpMenu = menuBar.addMenu("&Help")

        # File
        # New Exit는 해당 QAction이 trigger되었을때 connect되는 것이 없어서 해당 매뉴를 클릭해도 동작하지 않는 것으로 보임
        newAction = QAction('&New', self)
        newAction.setStatusTip('New')  # 상단 메뉴바의 File을 클릭하면 New매뉴가 보이도록

        exitAction = QAction('&Exit', self)
        exitAction.setStatusTip('Exit')  # 상단 메뉴바의 File을 클릭하면 Exit매뉴가 보이도록

        fileMenu.addAction(newAction)  # editMenu에 Qaction들 추가
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # Edit
        # cut copy paste는 해당 QAction이 trigger되었을때 connect되는 것이 없어서 해당 매뉴를 클릭해도 동작하지 않는 것으로 보임
        cutAction = QAction('&Cut', self)
        cutAction.setStatusTip('Cut')  # 상단 메뉴바의 Edit를 클릭하면 Cut매뉴가 보이도록

        copyAction = QAction('&Copy', self)
        copyAction.setStatusTip('Copy')  # 상단 메뉴바의 Edit를 클릭하면 Copy매뉴가 보이도록

        pasteAction = QAction('&Paste', self)
        pasteAction.setStatusTip('Paste')  # 상단 메뉴바의 Edit를 클릭하면 Paste매뉴가 보이도록

        selectAllAction = QAction('&Select All', self)
        selectAllAction.setStatusTip('Select All')  # 상단 메뉴바의 Edit를 클릭하면 Select All매뉴가 보이도록
        selectAllAction.triggered.connect(self.selectAll)  # selectAllAction이 trigger될 경우 self.selectAll실행

        unselectAllAction = QAction('&Unselect All', self)
        unselectAllAction.setStatusTip('Unselect All')  # 상단 메뉴바의 Edit를 클릭하면 Unselect All매뉴가 보이도록
        unselectAllAction.triggered.connect(self.unselectAll)  # unselectAllAction이 trigger될 경우 self.unselectAll실행

        editMenu.addAction(cutAction)  # editMenu에 Qaction들 추가
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(selectAllAction)
        editMenu.addAction(unselectAllAction)

        # View
        iconsViewAction = QAction('&Icons', self)
        iconsViewAction.setStatusTip('Icons')  # 상단 메뉴바의 View를 클릭하면 Icons매뉴가 보이도록
        iconsViewAction.triggered.connect(
            lambda checked: self.changeView("Icons"))  # iconsViewAction이 triggger될경우  self.changeView("Icons")실행

        listViewAction = QAction('&List', self)
        listViewAction.setStatusTip('List')  # 상단 메뉴바의 View를 클릭하면 List매뉴가 보이도록
        listViewAction.triggered.connect(
            lambda checked: self.changeView("List"))  # listViewAction이 triggger될경우  self.changeView("List")실행

        detailViewAction = QAction('&Details', self)
        detailViewAction.setStatusTip('Details')  # 상단 메뉴바의 View를 클릭하면 Details매뉴가 보이도록
        detailViewAction.triggered.connect(
            lambda checked: self.changeView("Details"))  # detailViewAction이 triggger될경우  self.changeView("Details")실행

        viewMenu.addAction(iconsViewAction)  # viewMenu에 Qaction들 추가
        viewMenu.addAction(listViewAction)
        viewMenu.addAction(detailViewAction)
        # About
        aboutAction = QAction('&About', self)
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.about)  # aboutAction이 triggger될경우  self.about실행//안내메시지 창 띄움

        helpMenu.addAction(aboutAction)  # helpMenu(menuBar.addMenu("&Help"))에 Qaction추가
if __name__ == '__main__': #프로그램 실행시 실행되는 부분
    app = QApplication(sys.argv) #QApplication생성
    ex = App(Path.home()) #App생성 #Path.home()은 사용자의 홈디렉토리를 의미 - 홈디렉토리는 윈도우 11 기준 사용자 폴더 #ex는 App객체
    sys.exit(app.exec_()) #프로그램 종료시까지 실행 #app.exec_()는 이벤트 루프를 실행시키는 함수 #sys.exit()는 프로그램 종료
