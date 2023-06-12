import os
import subprocess
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from utility import is_gitrepo

class branchAction():
    def BranchCreate(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())
        path = path.rsplit('/', 1)[0]
        if is_gitrepo(path):
            branch, ok = QInputDialog.getText(self, 'Create Branch', 'Enter the branch name to create')
            if ok:
                statusResult = os.popen("git branch " + branch).read()
                print(statusResult)
                if "already exists" in statusResult:
                    QMessageBox.warning(self, "Warning", statusResult, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", branch + " branch is created", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid branch name", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def BranchDelete(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())
        path = path.rsplit('/', 1)[0]
        if is_gitrepo(path):
            branch_list = subprocess.check_output(['git', 'branch', '-a']).decode('utf-8').split('\n')
            branch_list.remove('')
            branch_list_str = ""
            for i in range(len(branch_list)):
                branch_list_str += branch_list[i].lstrip() + '\n'
            branch, ok = QInputDialog.getText(self, 'Delete Branch', branch_list_str + '\nEnter the branch name to delete')
            if ok:
                statusResult = os.popen("git branch -D " + branch).read()
                statusResultFirstWord = statusResult.split()[0]
                print(statusResult)
                if statusResultFirstWord != "Deleted":
                    QMessageBox.warning(self, "Warning", statusResult, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", branch + " branch is deleted", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid branch name", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)
    
    def BranchRename(self):
        path = self.mainModel.filePath(self.mainExplorer.currentIndex())
        path = path.rsplit('/', 1)[0]
        if is_gitrepo(path):
            branch_list = subprocess.check_output(['git', 'branch', '-a']).decode('utf-8').split('\n')
            branch_list.remove('')
            branch_list_str = ""
            for i in range(len(branch_list)):
                branch_list_str += branch_list[i].lstrip() + '\n'
            old_branch, ok1 = QInputDialog.getText(self, 'Rename Branch', branch_list_str + '\nEnter the branch name to rename')
            new_branch, ok2 = QInputDialog.getText(self, 'Rename Branch', old_branch + " to what name? Enter the new branch name")
            if ok1 and ok2:
                statusResult = os.popen("git branch -m " + old_branch + " " + new_branch).read()
                print(statusResult)
                if statusResult != "":
                    QMessageBox.warning(self, "Warning", statusResult, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", old_branch + " branch is renamed as " + "new_branch", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid branch name", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)
    
    def BranchCheckout(self):
        print("tmp")