import os
from _gitAction import gitAction, parse_git_status
from _eventController import eventController

class refreshAction(gitAction, eventController):
    def refresh(self, event):#새로고침 이벤트 처리
        print("refresh")
        self.mainModel.setRootPath(self.currentDir)
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))
        path = self.mainModel.setRootPath(self.currentDir)
        if self.is_gitrepo(self.currentDir):
            os.chdir(self.currentDir)
            statuses_str = os.popen("git status").read()
            git_statuses = parse_git_status(statuses_str)
            self.git_status_column_update(self.currentDir, git_statuses)
        self.navigate(path)