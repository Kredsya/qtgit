import os, subprocess
from utility import parse_git_status, is_gitrepo, parse_git_current_branch

class navigator():
    def navigate(self, index): #QListView클래스의 setRootIndex함수 이용.
        self.currentDir = self.mainModel.fileInfo(index).absoluteFilePath() #현재 디렉토리를 설정
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir)) #QListView의 디렉토리를 설정
        if self.currentBranch == "":
            self.setWindowTitle(os.path.basename(self.currentDir))
        else:
            self.setWindowTitle(os.path.basename(self.currentDir) + f' ({self.currentBranch})') #QMainWindow의 타이틀을 현재 디렉토리로 설정
        self.addressBar.setText(self.currentDir) #현재 디렉토리를 표시하는 위젯에 현재 디렉토리를 설정

    def navigateUp(self, event): #상위 디렉토리로 가는 메소드
        self.currentDir = os.path.dirname(self.currentDir) #현재 디렉토리의 상위 디렉토리를 설정
        self.navigate(self.mainModel.setRootPath(self.currentDir)) #QListView의 디렉토리를 설정
        path = self.mainModel.setRootPath(self.currentDir)
        path_str = self.mainModel.filePath(path)
        print(f'###path = {path_str}')
        if is_gitrepo(path_str):
            os.chdir(self.currentDir)
            try:
                statuses_str = subprocess.check_output(['git', 'status'], shell=True, stderr=subprocess.STDOUT).decode('utf-8')
            except Exception as e:
                statuses_str = e.output.decode()
            git_statuses = parse_git_status(statuses_str)
            self.git_status_column_update(self.currentDir, git_statuses)
            self.currentBranch = parse_git_current_branch(statuses_str)
        else:
            self.currentBranch = ""
        self.navigate(path)