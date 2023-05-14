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

class FileSystemModelWithGitStatus(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.git_statuses = {}  # A dictionary to store git statuses, where the key is the filePath(QModelIndex) of file path
    def columnCount(self, parent=None):
            return super().columnCount() + 1  # Increase the column count by 1
    def data(self, index, role):#QFileSystemModel의data함수를 오버라이딩#QFileSystemModel의4번째 열의 데이터를 git status로 설정
            if index.column() == 4 and role == Qt.DisplayRole:
                # If the column is 4 (the git status column) and the role is DisplayRole, return the git status with self.git_statuses[index]
                if self.filePath(index) in self.git_statuses:
                    return self.git_statuses.get(self.filePath(index), self.git_statuses[self.filePath(index)])
                else:
                    return self.git_statuses.get(self.filePath(index), "")
            return super().data(index, role)
    def headerData(self, section, orientation, role=Qt.DisplayRole):#QFileSystemModel의headerData함수를 오버라이딩 #QFileSystemModel의4번째 열의 헤더를"Git Status"로 설정
        if section == 4 and role == Qt.DisplayRole:
            return "Git Status"
        return super().headerData(section, orientation, role)
    def update_git_status(self, file_path, status):#FilesystemModelWithGitStatus의 git_statuses필드에 git status를 저장한 후 모델을 업데이트하는 함수- self.data이용
        self.git_statuses[file_path] = status
        self.data(self.index(file_path), Qt.DisplayRole)

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

        self.mainModel = FileSystemModelWithGitStatus() #QFileSystemModel : 파일 시스템의 디렉토리 구조를 표현하는 모델
        self.mainModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Hidden)
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

    def isTargetOfAdd(gitState):
        if gitState == "modified" or gitState == "untracked":
            return True
        else:
            return False
    
    def isTargetOfRestore(gitState):
        if gitState == "unmodified" or gitState == "staged":
            return True
        else:
            return False
    
    def isTargetOfRmDelete(gitState):
        if gitState != "untracked":
            return True
        else:
            return False

    def GitInit(self):  # 상단바의 Git의 Init을 클릭 시 - git init을 실행하는 메소드(현재 디렉토리에 .git이 없는 디렉토리에서만 git init 실행) - .git이 있을 경우 경고 창
        # 현재 디렉토리 확인
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        print(path)
        # 현재 디렉토리에 .git이 있는지 확인
        if os.path.isdir(path + "/.git"):  # os.path.isdir() : 디렉토리가 존재하는지 확인하는 함수
            print("이미 git init이 되어있습니다.")
            # 이미 git init이 되어있는 경우
            QMessageBox.warning(self, "Warning", "이미 git init이 되어있습니다.", QMessageBox.Ok)  # QMessageBox : 메시지 박스를 생성하는 클래스
        else:# 현재 디렉토리에 .git이 없는 경우
            print("git init 실행")
            # git init 실행
            os.system("git init " + path)
            QMessageBox.information(self, "Information", "git init이 완료되었습니다.", QMessageBox.Ok)
            #.git은 숨김 파일이므로 숨김 파일을 보이게 하는 명령어 실행
            os.system("attrib -h -s " + path + "/.git")
            #숨김처리가 해제된 .git이 gui에서 보이도록 처리
            self.mainModel.setRootPath(path) #QFileSystemModel의 루트 디렉토리를 설정하는 함수
            self.mainExplorer.setRootIndex(self.mainModel.index(path)) #QListView의 루트 인덱스를 설정하는 함수

    # @todo : prototype, maybe error will occur
    def GitAdd(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        print(path)
        if os.path.isdir(path + '/.git'):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                fileGitState = self.mainModel.itemData(file)[4]
                filePath = join(self.currentDir, fileName)
                addResult = ""
                if os.path.exists(filePath) and self.isTargetOfAdd(fileGitState):
                    os.system("git add " + fileName)
                    addResult += fileName + '\n'
            QMessageBox.information(self, "Result", addResult, QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)
    
    def GitRestore(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        if os.path.isdir(path + '/.git'):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                fileGitState = self.mainModel.itemData(file)[4]
                filePath = join(self.currentDir, fileName)
                restoreResult = ""
                if os.path.exits(filePath) and self.isTargetOfRestore(fileGitState):
                    if fileGitState == "unmodified":
                        os.system("git restore " + fileName)
                    elif fileGitState == "staged":
                        os.system("git restore --staged " + fileName)
                    restoreResult += fileName + '\n'
            QMessageBox.information(self, "Result", restoreResult, QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)
    
    def GitRmDelete(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        if os.path.isdir(path + '/.git'):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                fileGitState = self.mainModel.itemData(file)[4]
                filePath = join(self.currentDir, fileName)
                rmDeleteResult = ""
                if os.path.exits(filePath) and self.isTargetOfRmDelete(fileGitState):
                    os.system("git rm " + fileName)
                    rmDeleteResult += fileName + '\n'
            QMessageBox.information(self, "Result", rmDeleteResult, QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

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
    def navigate(self, index): #QListView클래스의 setRootIndex함수 이용.
        self.currentDir = self.mainModel.fileInfo(index).absoluteFilePath() #현재 디렉토리를 설정
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir)) #QListView의 디렉토리를 설정
        self.setWindowTitle(os.path.basename(self.currentDir)) #QMainWindow의 타이틀을 현재 디렉토리로 설정
        self.addressBar.setText(self.currentDir) #현재 디렉토리를 표시하는 위젯에 현재 디렉토리를 설정
    def navigateUp(self, event): #상위 디렉토리로 가는 메소드
        self.currentDir = os.path.dirname(self.currentDir) #현재 디렉토리의 상위 디렉토리를 설정
        self.navigate(self.mainModel.setRootPath(self.currentDir)) #QListView의 디렉토리를 설정
    def navigateFromSideTree(self, selected, unselected): #QTreeView의 디렉토리
        print(selected)
    def deleteFiles(self, event): #상단바의 Edit의 delete 클릭시, 선택된 파일들을 삭제하는 메소드
        reply = QMessageBox.question(self, 'Delete', 'Are you sure you sure you want to delete those elements ?', #삭제 여부를 묻는 메시지 박스
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No) #Yes와 No버튼을 생성
        if  reply == QMessageBox.Yes: #Yes버튼을 누르면
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes(); #선택된 파일들의 인덱스를 가져옴
            for file in selectedIndexes: #선택된 파일들을 삭제
                fileName = self.mainModel.itemData(file)[0] #파일의 이름을 가져옴
                filePath = join(self.currentDir, fileName) #파일의 경로를 가져옴
                if os.path.exists(filePath): #파일이 존재하면
                    try:#파일을 삭제
                        if isdir(filePath): #파일이 디렉토리면
                            shutil.rmtree(filePath) #디렉토리를 삭제
                        elif isfile(filePath):#파일이 파일이면
                            os.remove(filePath) #파일을 삭제
                        self.mainModel.remove(file) #QListView에서 파일을 삭제
                    except OSError: #파일을 삭제하는데 실패하면
                        print("failed to delete: " + filePath) #삭제 실패 메시지 출력
                        pass
                else: #파일이 존재하지 않으면
                    self.mainModel.remove(file) #QListView에서 파일을 삭제
    def changeView(self, view): #상단바의 View의 List, Icons, Details를 클릭시, QListView, QTableView의 모드를 변경하는 메소드
        if(view == "List"): #List를 클릭하면
            if type(self.mainExplorer) is not QListView: #QListView가 아니면
                self.mainExplorer = QListView() #QListView로 변경

            self.mainExplorer.setViewMode(QListView.ListMode) #QListView의 모드를 ListMode로 변경
            self.mainExplorer.setIconSize(QSize(64, 64)) #QListView의 아이콘 크기를 변경
        elif(view == "Icons"): #Icons를 클릭하면
            if type(self.mainExplorer) is not QListView: #QListView가 아니면
                self.mainExplorer = QListView() #QListView로 변경

            self.mainExplorer.setViewMode(QListView.IconMode) #QListView의 모드를 IconMode로 변경
            self.mainExplorer.setWordWrap(True) #QListView의 아이콘을 자동으로 줄바꿈
            self.mainExplorer.setIconSize(QSize(64, 80)) #QListView의 아이콘 크기를 변경
            self.mainExplorer.setUniformItemSizes(True) #QListView의 아이콘 크기를 균일하게 변경
        elif(view == "Details"): #Details를 클릭하면
            self.mainExplorer = QTableView() #QTableView로 변경
            self.mainExplorer.setSelectionBehavior(QAbstractItemView.SelectRows) #QTableView의 선택 모드를 행 단위로 변경
            self.mainExplorer.setSelectionMode(QAbstractItemView.ExtendedSelection) #QTableView의 선택 모드를 다중 선택으로 변경

            self.mainExplorer.verticalHeader().hide() #QTableView의 세로 헤더를 숨김
            self.mainExplorer.setShowGrid(False) #QTableView의 그리드를 숨김
            self.mainExplorer.horizontalHeader().setSectionsMovable(True) #QTableView의 헤더를 이동 가능하게 변경
            self.mainExplorer.horizontalHeader().setHighlightSections(False) #QTableView의 헤더를 선택시 하이라이트를 표시하지 않게 변경
            self.mainExplorer.setFrameStyle(QFrame.NoFrame) #QTableView의 테두리를 숨김
            self.mainExplorer.setSortingEnabled(True) #QTableView의 정렬을 활성화
            self.mainExplorer.setEditTriggers(QAbstractItemView.EditKeyPressed) #QTableView의 편집을 키보드로 활성화

        # Common
        self.mainExplorer.doubleClicked.connect(self.onDoubleClick) #QListView, QTableView의 더블 클릭 이벤트를 처리하는 함수를 연결
        self.mainExplorer.setContextMenuPolicy(Qt.CustomContextMenu) #QListView, QTableView의 컨텍스트 메뉴를 커스텀으로 변경
        self.mainExplorer.customContextMenuRequested.connect(self.contextItemMenu) #QListView, QTableView의 컨텍스트 메뉴 이벤트를 처리하는 함수를 연결
        self.mainExplorer.setModel(self.mainModel) #QListView, QTableView의 모델을 설정

        if hasattr(self, "explorerSplitter"): #explorerSplitter가 존재하면
            self.explorerSplitter.replaceWidget(1, self.mainExplorer) #explorerSplitter의 1번째 위젯을 QListView, QTableView로 변경
            self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir)) #QListView, QTableView의 루트 경로를 설정


    def updateStatus(self, path): #하단바의 상태를 업데이트하는 메소드
        status = str(self.mainModel.rowCount(self.mainModel.index(path))) + " elements" #현재 폴더의 파일 개수를 가져옴 #QListView, QTableView의 파일 개수를 가져옴
        selectedCount = len(self.mainExplorer.selectionModel().selectedIndexes()) #선택된 파일 개수를 가져옴 #QListView, QTableView의 선택된 파일 개수를 가져옴
        if selectedCount > 0:     #선택된 파일이 있으면
            status += " | " + str(selectedCount) + " elements selected" #선택된 파일 개수를 상태에 추가
        
        self.statusBar().showMessage(status) #하단바의 상태를 업데이트 #상태바에 상태를 출력
    def onKeyPress(self, key): #키보드 이벤트 처리
        if key.key() == Qt.Key_Delete: #Delete키를 눌렀을 때
            self.deleteFiles(None) #deleteFiles함수 호출
    def onDoubleClick(self, event): #더블클릭 이벤트 처리
        itemPath = self.mainModel.fileInfo(event) #더블클릭한 파일의 경로를 가져옴
        itemPath_str = str(itemPath.absoluteFilePath())  # QFileInfo 객체로부터 절대 경로를 얻고 문자열로 변환
        if isdir(itemPath): #더블클릭한 파일이 폴더일 경우
            self.navigate(event) #navigate함수 호출 #폴더를 열어줌
            if os.path.isdir(itemPath_str + "/.git"):  # os.path.isdir() : 디렉토리가 존재하는지 확인하는 함수
                status_str = subprocess.check_output(["git", "status"], universal_newlines=True)
                # 현재 경로에 있는 모든 파일에 대해 mainExplorer의 update_git_status() 함수를 이용해 Git Status를  업데이트 -  "messege"는 임시로 넣은 값, 이곳에 업데이트 할 내용을 넣으면 됨.
                for item in os.listdir(itemPath_str):
                    item_str = itemPath_str + "/" + item
                    self.mainModel.update_git_status(item_str, "messege")
        elif isfile(itemPath): #더블클릭한 파일이 파일일 경우
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', itemPath)) #open 명령어를 이용하여 파일을 열어줌
            elif platform.system() == 'Windows':    # Windows
                os.startfile(itemPath) #startfile 명령어를 이용하여 파일을 열어줌
            else:                                   # linux variants
                subprocess.call(('xdg-open', itemPath)) #xdg-open 명령어를 이용하여 파일을 열어줌
    def contextItemMenu(self, position): #컨텍스트 메뉴 이벤트 처리
        index = self.mainExplorer.indexAt(position) #커서가 위치한 곳의 인덱스를 가져옴
        if (index.isValid()): #인덱스가 유효하다면
            menu = QMenu() #메뉴 생성
            cutAction = menu.addAction("Cut") #메뉴에 Cut 액션 추가
            cutAction.triggered.connect(self.cutFiles) #액션에 cutFiles함수를 연결

            deleteAction = menu.addAction("Delete") #메뉴에 Delete 액션 추가
            deleteAction.triggered.connect(self.deleteFiles) #액션에 deleteFiles함수를 연결
            
            renameAction = menu.addAction("Rename") #메뉴에 Rename 액션 추가
            renameAction.triggered.connect(self.renameFile) #액션에 renameFile함수를 연결

            copyAction = menu.addAction("Copy") #메뉴에 Copy 액션 추가
            copyAction.triggered.connect(self.copyFiles) #액션에 copyFiles함수를 연결
            menu.addSeparator() #메뉴에 구분선 추가
            action = menu.exec_(QCursor.pos()) #메뉴를 실행
        else: #인덱스가 유효하지 않다면
            menu = QMenu() #메뉴 생성
            menu.addAction("Refresh").triggered.connect(self.refresh) #메뉴에 Refresh 액션 추가
            menu.addSeparator() #메뉴에 구분선 추가
            pasteAction = menu.addAction("Paste") #메뉴에 Paste 액션 추가
            pasteAction.triggered.connect(self.pasteFiles) #액션에 pasteFiles함수를 연결

            action = menu.exec_(QCursor.pos()) #메뉴를 실행
    def refresh(self, event):#새로고침 이벤트 처리
        print("refresh")
        self.mainModel.setRootPath(self.currentDir)
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))

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
        selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes(); #선택된 파일들의 인덱스를 받아옴
        for file in selectedIndexes: #선택된 파일들의 인덱스를 하나씩 돌면서
            fileName = self.mainModel.itemData(file)[0] #선택된 파일의 이름을 받아옴
            filePath = join(self.currentDir, fileName) #선택된 파일의 경로를 받아 옴
            if os.path.exists(filePath): #선택된 파일이 존재한다면
                self.mainExplorer.edit(file) #선택된 파일의 이름을 바꿔줌
                self.mainExplorer.edit(file) #선택된 파일의 이름을 바꿔줌

    def createTopMenu(self):
        # Add menus
        menuBar = self.menuBar()  # 상단 메뉴바

        fileMenu = menuBar.addMenu('&File')  # 메뉴바에 File Edit View Git Help 추가
        editMenu = menuBar.addMenu("&Edit")
        viewMenu = menuBar.addMenu("&View")
        gitMenu = menuBar.addMenu("&Git")
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
        iconsViewAction.setStatusTip('Change view as Icon only')  # 상단 메뉴바의 View를 클릭하면 Icons매뉴가 보이도록
        iconsViewAction.triggered.connect(
            lambda checked: self.changeView("Icons"))  # iconsViewAction이 triggger될경우  self.changeView("Icons")실행

        listViewAction = QAction('&List', self)
        listViewAction.setStatusTip('Change view as File name only')  # 상단 메뉴바의 View를 클릭하면 List매뉴가 보이도록
        listViewAction.triggered.connect(
            lambda checked: self.changeView("List"))  # listViewAction이 triggger될경우  self.changeView("List")실행

        detailViewAction = QAction('&Details', self)
        detailViewAction.setStatusTip('Change view as Details (default)')  # 상단 메뉴바의 View를 클릭하면 Details매뉴가 보이도록
        detailViewAction.triggered.connect(
            lambda checked: self.changeView("Details"))  # detailViewAction이 triggger될경우  self.changeView("Details")실행

        viewMenu.addAction(iconsViewAction)  # viewMenu에 Qaction들 추가
        viewMenu.addAction(listViewAction)
        viewMenu.addAction(detailViewAction)

        # Git
        gitInitAction = QAction('&Git Init', self) # 상단 메뉴바의 Git을 클릭하면 Repository Create매뉴가 보이도록
        gitInitAction.setStatusTip('Execute <git init> command') # 하단 메뉴바에 해당 메뉴에 대한 설명 표시
        gitInitAction.triggered.connect(self.GitInit)  # gitInitAction이 triggger될경우  self.GitInit

        gitAddAction = QAction('&Add', self)
        gitAddAction.setStatusTip('Execute <git add [selected]> command')
        gitAddAction.triggered.connect(self.GitAdd)

        gitRestoreAction = QAction('&Restore', self)
        gitRestoreAction.setStatusTip('Execute <git restore [selected]> or <git restore --staged [selected]> command')
        gitRestoreAction.triggered.connect(self.GitRestore)
        
        gitRmDeleteAction = QAction('&Rm(Delete file)', self)
        gitRmDeleteAction.setStatusTip('Execute <git rm --cached [selected]> command')
        gitRmDeleteAction.triggered.connect(self.GitRmDelete)

        gitRmUntrackAction = QAction('&Rm(Untrack file)', self)
        gitRmUntrackAction.setStatusTip('Execute <git rm [selected]> command')
        #gitRmUntrackAction.triggered.connect(self.gitRmUntrack)

        gitCommitAction = QAction('&Commit', self)
        gitCommitAction.setStatusTip('Confirm about staged files and Execute <git commit -m [message]> command')
        #gitCommitAction.triggered.connect(self.GitCommit)

        gitMenu.addAction(gitInitAction)  # gitMenu(menuBar.addMenu("&Git"))에 Qaction추가
        gitMenu.addAction(gitAddAction)
        gitMenu.addAction(gitRestoreAction)
        gitMenu.addAction(gitRmDeleteAction)
        gitMenu.addAction(gitRmUntrackAction)
        gitMenu.addAction(gitCommitAction)
        # About
        aboutAction = QAction('&About', self)
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.about)  # aboutAction이 triggger될경우  self.about실행//안내메시지 창 띄움

        helpMenu.addAction(aboutAction)  # helpMenu(menuBar.addMenu("&Help"))에 Qaction추가
if __name__ == '__main__': #프로그램 실행시 실행되는 부분
    app = QApplication(sys.argv) #QApplication생성
    ex = App(Path.home()) #App생성 #Path.home()은 사용자의 홈디렉토리를 의미 - 홈디렉토리는 윈도우 11 기준 사용자 폴더 #ex는 App객체
    sys.exit(app.exec_()) #프로그램 종료시까지 실행 #app.exec_()는 이벤트 루프를 실행시키는 함수 #sys.exit()는 프로그램 종료
