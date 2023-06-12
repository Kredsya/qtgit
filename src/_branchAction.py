import os
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
            print("git init을 먼저 하세요.")
            QMessageBox.warning(self, "Warning", "git init을 먼저 하세요.", QMessageBox.Ok)

    def BranchDelete(self):
        print("hello")
    
    def BranchRename(self):
        print("HeLLo")
    
    def BranchCheckout(self):
        print("tmp")