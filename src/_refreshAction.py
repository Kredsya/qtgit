import os, subprocess
from utility import parse_git_status, is_gitrepo, parse_git_current_branch
from _eventController import eventController

class refreshAction(eventController):
    def refresh(self):#새로고침 이벤트 처리
        print("refresh")
        self.mainModel.setRootPath(self.currentDir)
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))
        path = self.mainModel.setRootPath(self.currentDir)
        if is_gitrepo(self.currentDir):
            os.chdir(self.currentDir)
            try:
                statuses_str = subprocess.check_output(['git', 'status'], shell=True, stderr=subprocess.STDOUT).decode('utf-8')
            except Exception as e:
                statuses_str = e.output.decode()
            git_statuses = parse_git_status(statuses_str)
            self.git_status_column_update(self.currentDir, git_statuses)
            self.currentBranch = parse_git_current_branch(statuses_str)
        self.navigate(path)