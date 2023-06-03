from isTarget import *
from os.path import isfile, isdir
import os
from PyQt5.QtWidgets import QMessageBox, QInputDialog

def parse_git_status(status):
    lines = status.split('\n')

    stages = {
        'Changes to be committed:': [],
        'Changes not staged for commit:': [],
        'Untracked files:': [],
    }

    current_section = None
    for line in lines:
        line = line.strip()
        if line in stages:
            current_section = line
        elif line.startswith(('modified:', 'new file:', 'deleted:', 'renamed:')):
            if current_section:
                filename = line.split(':   ')[-1]
                if not '"' in filename and not "'" in filename and not "*" in filename and not "'" in filename and not "?" in filename and not "<" in filename and not ">" in filename and not "|" in filename:
                    stages[current_section].append(filename)
        elif current_section == 'Untracked files:' and line and line != '(use "git add <file>..." to include in what will be committed)' and line != 'no changes added to commit (use "git add" and/or "git commit -a")':
            if not '"' in line and not "'" in line and not "*" in line and not "'" in line and not "?" in line and not "<" in line and not ">" in line and not "|" in line:
                stages[current_section].append(line)

    # Rename keys for clarity
    stages['staged'] = stages.pop('Changes to be committed:')
    stages['modified'] = stages.pop('Changes not staged for commit:')
    stages['untracked'] = stages.pop('Untracked files:')
    return stages

class gitAction():
    def is_gitrepo(self, dir):
        if not os.path.exists(dir):
            return False
        original_path = os.getcwd()
        os.chdir(dir)
        result = os.popen("git status").read()
        os.chdir(original_path)

        if "not a git" in result:
            return False
        return True
    
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

    def GitAdd(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        print(path)
        if self.is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(self.currentDir) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                print(f"fileGitState = {fileGitState}")
                addResult = ""
                if os.path.exists(filePath) and isTargetOfAdd(fileGitState):
                    os.system("git add " + fileName)
                    addResult += fileName + '\n'
            QMessageBox.information(self, "Result", addResult, QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitRestore(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        if self.is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(self.currentDir) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                restoreResult = ""
                if os.path.exists(filePath) and isTargetOfRestore(fileGitState):
                    if fileGitState == "unmodified" or fileGitState == "modified & staged":
                        os.system("git restore " + fileName)
                    elif fileGitState == "staged" or fileGitState == "untracked":
                        os.system("git restore --staged " + fileName)
                    restoreResult += fileName + '\n'
            QMessageBox.information(self, "Result", restoreResult, QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitRmDelete(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        if self.is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(self.currentDir) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                rmDeleteResult = ""
                if os.path.exists(filePath) and isTargetOfRmDelete(fileGitState):
                    if fileGitState == "modified & staged":
                        os.system("git rm -f " + fileName)
                    else:
                        os.system("git rm " + fileName)
                    rmDeleteResult += fileName + '\n'
            QMessageBox.information(self, "Result", rmDeleteResult, QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def GitRmUntrack(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        if self.is_gitrepo(path):
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes()
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                filePath = str(self.currentDir) + '/' + str(fileName)
                if not (isdir(filePath) or isfile(filePath)):
                    continue
                fileGitState = self.mainModel.git_statuses[filePath]
                rmUntrackResult = ""
                if os.path.exists(filePath) and isTargetOfUntrack(fileGitState):
                    if fileGitState == "modified & staged":
                        os.system("git rm --cached -f " + fileName)
                    else:
                        os.system("git rm --cached " + fileName)
                    rmUntrackResult += fileName + '\n'
            QMessageBox.information(self, "Result", rmUntrackResult, QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    # unused function
    def GitCommit(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())  # QFileSystemModel의 현재 디렉토리의 경로를 반환하는 함수
        path = path.rsplit('/', 1)[0]
        if self.is_gitrepo(path):
            text, ok = QInputDialog.getText(self, 'Commit Message', 'Enter commit message')
            if ok:
                os.system('git commit -m "' + text + '"')
                QMessageBox.information(self, "Result", "Commit is done", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid commit message", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)