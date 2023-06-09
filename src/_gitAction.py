from utility import *
from os.path import isfile, isdir
import os
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QApplication
from _refreshAction import refreshAction
from _gitGraph import GitLogViewer
from _gitClone import GitClone
from _gitCredential import GitCredential
import sys

class gitAction(refreshAction):
    def GitInit(self):  # 상단바의 Git의 Init을 클릭 시 - git init을 실행하는 메소드(현재 디렉토리에 .git이 없는 디렉토리에서만 git init 실행) - .git이 있을 경우 경고 창
        # 현재 디렉토리 확인
        path = self.mainModel.rootPath()
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
            self.refresh()

    def GitAdd(self):
        path = self.mainModel.rootPath()
        print(path)
        if is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            addResult = ""
            for index in range(0, len(selectedIndexes), 5):
                file = selectedIndexes[index]
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(path) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                if os.path.exists(filePath) and isTargetOfAdd(fileGitState):
                    os.system("git add " + fileName)
                    addResult += fileName + '\n'
            QMessageBox.information(self, "Result", addResult, QMessageBox.Ok)
            self.refresh()
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitRestore(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            restoreResult = ""
            for index in range(0, len(selectedIndexes), 5):
                file = selectedIndexes[index]
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(self.currentDir) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                if os.path.exists(filePath) and isTargetOfRestore(fileGitState):
                    if fileGitState == "unmodified" or fileGitState == "modified & staged":
                        os.system("git restore " + fileName)
                    elif fileGitState == "staged" or fileGitState == "untracked":
                        os.system("git restore --staged " + fileName)
                    restoreResult += fileName + '\n'
            QMessageBox.information(self, "Result", restoreResult, QMessageBox.Ok)
            self.refresh()
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitRmDelete(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            rmDeleteResult = ""
            for index in range(0, len(selectedIndexes), 5):
                file = selectedIndexes[index]
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(self.currentDir) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                if os.path.exists(filePath) and isTargetOfRmDelete(fileGitState):
                    if fileGitState == "modified & staged":
                        os.system("git rm -f " + fileName)
                    else:
                        os.system("git rm " + fileName)
                    rmDeleteResult += fileName + '\n'
            QMessageBox.information(self, "Result", rmDeleteResult, QMessageBox.Ok)
            self.refresh()
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitRmUntrack(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            rmUntrackResult = ""
            for index in range(0, len(selectedIndexes), 5):
                file = selectedIndexes[index]
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(self.currentDir) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                if os.path.exists(filePath) and isTargetOfUntrack(fileGitState):
                    if fileGitState == "modified & staged":
                        os.system("git rm --cached -f " + fileName)
                    else:
                        os.system("git rm --cached " + fileName)
                    rmUntrackResult += fileName + '\n'
            QMessageBox.information(self, "Result", rmUntrackResult, QMessageBox.Ok)
            self.refresh()
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitCommit(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            try:
                statusResult = subprocess.check_output(['git', 'status'], shell=True, stderr=subprocess.STDOUT).decode('utf-8')
            except Exception as e:
                statusResult = e.output.decode()
            stagedFiles = parse_staged_files(statusResult)
            msg = "- Changes to be committed\n"
            for file in stagedFiles:
                msg += file + '\n'
            text, ok = QInputDialog.getText(self, 'Commit Message', msg+'\nEnter commit message')
            if ok:
                os.system('git commit -m "' + text + '"')
                QMessageBox.information(self, "Result", "Commit is done", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid commit message", QMessageBox.Ok)
            self.refresh()
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitLogGraph(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            #_gitGraph.py 사용
            self.gitLogViewer = GitLogViewer()  # self에 참조를 저장하여 객체가 사라지지 않게 합니다.
            self.gitLogViewer.show()
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitCredentialSaver(self):
        self.gitCredentialWindow = GitCredential()
        self.gitCredentialWindow.show()

    def GitCloner(self):
        self.gitCloneWindow = GitClone()
        self.gitCloneWindow.show()
