import shutil
from pathlib import Path
from os.path import isfile, isdir, join
import subprocess, os, platform
from PyQt5.QtWidgets import QApplication, QAbstractItemView, QLineEdit, QTableView, QSplitter, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QMenu, QWidget, QAction,QMessageBox, QFileSystemModel, QTreeView, QListView, QFrame, QLabel, QDialogButtonBox, QDialog, QInputDialog
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QDir, QSize
import sys
from _gitAction import gitAction, parse_git_status
from _appUI import appUI
from _createMenu import createMenu
from _eventController import eventController
from _fileChanger import fileChanger
from _refreshAction import refreshAction

class App(QMainWindow, refreshAction, appUI, gitAction, createMenu, eventController, fileChanger):  # main application window를 위한 클래스
    def __init__(self, initialDir): 
        super().__init__()
        # Variables
        self.currentDir = initialDir  # pathlib모듈의 Path객체를 받음. main함수에서 App객체를 생성할 때에는 home디렉토리(사용자 폴더)를 인자로 넘겨줌
        self.history = {}
        self.mainExplorer = None  # QListView 클래스 객체를 받는 필드. 파일 목록을 리스트로 보여주기 위함
        # App init
        self.initUI()
    
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

if __name__ == '__main__': #프로그램 실행시 실행되는 부분
    app = QApplication(sys.argv) #QApplication생성
    ex = App(Path.home()) #App생성 #Path.home()은 사용자의 홈디렉토리를 의미 - 홈디렉토리는 윈도우 11 기준 사용자 폴더 #ex는 App객체
    sys.exit(app.exec_()) #프로그램 종료시까지 실행 #app.exec_()는 이벤트 루프를 실행시키는 함수 #sys.exit()는 프로그램 종료
