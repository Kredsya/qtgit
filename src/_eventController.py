from os.path import isfile, isdir
import subprocess, os, platform
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QCursor
from utility import parse_git_status, is_gitrepo, parse_git_branch
from PyQt5.QtCore import Qt

class eventController():
    def onDoubleClick(self, event): #더블클릭 이벤트 처리
        itemPath = self.mainModel.fileInfo(event) #더블클릭한 파일의 경로를 가져옴
        itemPath_str = str(itemPath.absoluteFilePath())  # QFileInfo 객체로부터 절대 경로를 얻고 문자열로 변환
        print(f"onDoubleClick : {itemPath_str}")
        if isdir(itemPath): #더블클릭한 파일이 폴더일 경우
            if is_gitrepo(itemPath_str):
                os.chdir(itemPath_str)
                statuses_str = os.popen("git status").read()
                git_statuses = parse_git_status(statuses_str)
                self.git_status_column_update(itemPath_str, git_statuses)
                self.currentBranch = parse_git_branch(statuses_str)
            self.navigate(event) #navigate함수 호출 #폴더를 열어줌

        elif isfile(itemPath): #더블클릭한 파일이 파일일 경우
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', itemPath)) #open 명령어를 이용하여 파일을 열어줌
            elif platform.system() == 'Windows':    # Windows
                os.startfile(itemPath) #startfile 명령어를 이용하여 파일을 열어줌
            else:                                   # linux variants
                subprocess.call(('xdg-open', itemPath)) #xdg-open 명령어를 이용하여 파일을 열어줌

    def git_status_column_update(self, itemPath_str, git_statuses):
        self.mainModel.git_statuses = {}
        # Git Status출력값을 바탕으로 업데이트
        for untracked_item in git_statuses['untracked']:
            if itemPath_str + "/" + untracked_item in self.mainModel.git_statuses:
                self.mainModel.update_git_status(itemPath_str + "/" + untracked_item, self.mainModel.git_statuses[itemPath_str + "/" + untracked_item] + " & untracked")
            else:
                self.mainModel.update_git_status(itemPath_str + "/" + untracked_item, "untracked")

            if '/' in untracked_item:
                tmp_item = untracked_item.split('/')[0]
                self.mainModel.update_git_status(itemPath_str + "/" + tmp_item, "untracked")

        for modified_item in git_statuses['modified']:
            if itemPath_str + "/" + modified_item in self.mainModel.git_statuses:
                self.mainModel.update_git_status(itemPath_str + "/" + modified_item, self.mainModel.git_statuses[itemPath_str + "/" + modified_item] + " & modified")
            else:
                self.mainModel.update_git_status(itemPath_str + "/" + modified_item, "modified")

            if '/' in modified_item:
                tmp_item = modified_item.split('/')[0]
                self.mainModel.update_git_status(itemPath_str + "/" + tmp_item, "modified")

        for staged_item in git_statuses['staged']:
            if itemPath_str + "/" + staged_item in self.mainModel.git_statuses:
                self.mainModel.update_git_status(itemPath_str + "/" + staged_item, self.mainModel.git_statuses[itemPath_str + "/" + staged_item] + " & staged")
            else:
                self.mainModel.update_git_status(itemPath_str + "/" + staged_item, "staged")

            if '/' in staged_item:
                tmp_item = staged_item.split('/')[0]
                self.mainModel.update_git_status(itemPath_str + "/" + tmp_item, "staged")

        #itemPath_str의 모든 파일, 폴더들을 순회 - unmodified처리
        for item in os.listdir(itemPath_str):
            if not(itemPath_str + "/" + item in self.mainModel.git_statuses) and item != ".git":
                self.mainModel.update_git_status(itemPath_str + "/" + item, "unmodified")
        
        print(itemPath_str)
        print(git_statuses)


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
    
    def onKeyPress(self, key): #키보드 이벤트 처리
        if key.key() == Qt.Key_Delete: #Delete키를 눌렀을 때
            self.deleteFiles(None) #deleteFiles함수 호출