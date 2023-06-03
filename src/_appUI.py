from PyQt5.QtWidgets import QLineEdit, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QWidget, QFileSystemModel, QTreeView, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt,QDir

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
        try: #만약 git status명령의 출력값을 파싱하는 과정에서 파일 이름이 아니라 다른 메시지가 포함되었으면 그냥 패스하도록.
            self.data(self.index(file_path), Qt.DisplayRole)
        except:
            pass

class appUI():
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
        self.move(100, 100)
        self.resize(1200, 800)  # QMainWindow의 크기를 설정
        self.show()  # QMainWindow를 보여줌

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