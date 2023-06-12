import os
import subprocess
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from _refreshAction import refreshAction
from utility import is_gitrepo, make_branch_list, parse_unmerged_paths

class branchAction(refreshAction):
    def BranchCreate(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            old_branch_list = make_branch_list()
            branch, ok = QInputDialog.getText(self, 'Create Branch', 'Enter the branch name to create')
            if ok:
                try:
                    statusResult = subprocess.check_output(['git', 'branch', branch], shell=True, stderr=subprocess.STDOUT).decode('utf-8').split('\n')[0]
                except Exception as e:
                    statusResult = e.output.decode()
                new_branch_list = make_branch_list()
                if old_branch_list == new_branch_list:
                    QMessageBox.warning(self, "Warning", statusResult, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", f"{branch} branch is created", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid branch name", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def BranchDelete(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            branch_list = make_branch_list()
            branch, ok = QInputDialog.getItem(self, 'Delete Branch', 'What branch do you want to delete?', branch_list)
            if ok:
                try:
                    statusResult = subprocess.check_output(['git', 'branch', '-D', branch], shell=True, stderr=subprocess.STDOUT).decode('utf-8').split('\n')[0]
                except Exception as e:
                    statusResult = e.output.decode()
                new_branch_list = make_branch_list()
                if branch_list == new_branch_list:
                    QMessageBox.warning(self, "Warning", statusResult, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", f"{branch} branch is deleted", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid branch name", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)
    
    def BranchRename(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            branch_list = make_branch_list()
            old_branch, ok1 = QInputDialog.getItem(self, 'Rename Branch', 'What branch do you want to rename?', branch_list)
            new_branch, ok2 = QInputDialog.getText(self, 'Rename Branch', f"{old_branch} to what name? Enter the new branch name")
            if ok1 and ok2:
                try:
                    statusResult = subprocess.check_output(['git', 'branch', '-m', old_branch, new_branch], shell=True, stderr=subprocess.STDOUT).decode('utf-8').split('\n')[0]
                except Exception as e:
                    statusResult = e.output.decode()
                new_branch_list = make_branch_list()
                if branch_list == new_branch_list:
                    QMessageBox.warning(self, "Warning", statusResult, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", f"{old_branch} branch is renamed as {new_branch}", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid branch name", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)
    
    def BranchCheckout(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            branch_list = make_branch_list()
            branch, ok = QInputDialog.getItem(self, 'Checkout Branch', 'What branch do you want to checkout?', branch_list)
            if ok:
                errorFlag = False
                try:
                    statusResult = subprocess.check_output(['git', 'checkout', branch], shell=True, stderr=subprocess.STDOUT).decode('utf-8').split('\n')[0]
                except Exception as e:
                    statusResult = e.output.decode()
                    errorFlag = True
                if errorFlag:
                    QMessageBox.warning(self, "Warning", statusResult, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", f"Switched to branch {branch}", QMessageBox.Ok)
                    self.refresh()
            else:
                QMessageBox.warning(self, "Warning", "Error : unvalid branch name", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)
    
    def BranchMerge(self):
        path = self.mainModel.rootPath()
        if is_gitrepo(path):
            branch_list = make_branch_list()
            print(branch_list)
            branch_list.remove(self.currentBranch)
            branch, ok = QInputDialog.getItem(self, 'Merge Branch', f'Select target branch\nbase:{self.currentBranch} <- compare:[target_branch]', branch_list)
            if ok:
                errorFlag = False
                try:
                    statusResult = subprocess.check_output(['git', 'merge', branch], shell=True, stderr=subprocess.STDOUT).decode('utf-8').split('\n')[0]
                except Exception as e:
                    statusResult = e.output.decode()
                    errorFlag = True
                if "CONFLICT" in statusResult:
                    try:
                        statusResult = subprocess.check_output(['git', 'status'], shell=True, stderr=subprocess.STDOUT).decode('utf-8')
                    except Exception as e:
                        statusResult = e.output.decode()
                    unmergedPaths = parse_unmerged_paths(statusResult)
                    unmergedPathsStr = ""
                    for path in unmergedPaths:
                        unmergedPathsStr += path + '\n'
                    print(f'===unmergedPath = {unmergedPaths}===')
                    QMessageBox.warning(self, "Warning", unmergedPathsStr + "\nMerge conflict.", QMessageBox.Ok)
                    subprocess.run(['git', 'merge', '--abort'], shell=True)
                elif errorFlag or "fatal" in statusResult:
                    QMessageBox.warning(self, "Warning", "Unexpected error while merging.", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Result", f"base:{self.currentBranch} <- compare:{branch}\nSuccessfully merged.", QMessageBox.Ok)
        else:
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)