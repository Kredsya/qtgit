import os
from utility import parse_git_status, is_gitrepo, parse_git_current_branch

class navigator():
    def navigate(self, index): #QListView클래스의 setRootIndex함수 이용.
        self.currentDir = self.mainModel.fileInfo(index).absoluteFilePath() #현재 디렉토리를 설정
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir)) #QListView의 디렉토리를 설정
        self.setWindowTitle(os.path.basename(self.currentDir) + f' ({self.currentBranch})') #QMainWindow의 타이틀을 현재 디렉토리로 설정
        self.addressBar.setText(self.currentDir) #현재 디렉토리를 표시하는 위젯에 현재 디렉토리를 설정

    def navigateUp(self, event): #상위 디렉토리로 가는 메소드
        self.currentDir = os.path.dirname(self.currentDir) #현재 디렉토리의 상위 디렉토리를 설정
        self.navigate(self.mainModel.setRootPath(self.currentDir)) #QListView의 디렉토리를 설정
        path = self.mainModel.setRootPath(self.currentDir)
        if is_gitrepo(self.currentDir):
            os.chdir(self.currentDir)
            statuses_str = os.popen("git status").read()
            git_statuses = parse_git_status(statuses_str)
            self.git_status_column_update(self.currentDir, git_statuses)
            self.currentBranch = parse_git_current_branch(statuses_str)
        self.navigate(path)