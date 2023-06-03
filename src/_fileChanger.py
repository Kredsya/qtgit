import shutil
from os.path import join
import os

class fileChanger():
    def cutFiles(self, event):#관련 QAction이 trigger되었을때 connect되도록 되어있지 않아 무쓸모
        self.selectedFiles = self.mainExplorer.selectionModel().selectedIndexes()
    def copyFiles(self, event):#관련 QAction이 trigger되었을때 connect되도록 되어있지 않아 무쓸모
        self.selectedFiles = self.mainExplorer.selectionModel().selectedIndexes()
    def pasteFiles(self, event):#관련 QAction이 trigger되었을때 connect되도록 되어있지 않아 무쓸모
        for file in self.selectedFiles:
            fileName = self.mainModel.itemData(file)[0]
            filePath = join(self.currentDir, fileName)
            if os.path.exists(filePath):
                try:
                    shutil.copy(filePath, self.currentDir)
                    # self.mainModel.remove(file)
                except OSError:
                    print("failed to copy: " + filePath)
                    pass
            else:
                self.mainModel.remove(file)
    def renameFile(self, event):#선택된 파일을 mainExplorer.selectionModel().selectedIndexes()로 받아와서 이름을 바꿔줌
        selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes(); #선택된 파일들의 인덱스를 받아옴
        for file in selectedIndexes: #선택된 파일들의 인덱스를 하나씩 돌면서
            fileName = self.mainModel.itemData(file)[0] #선택된 파일의 이름을 받아옴
            filePath = join(self.currentDir, fileName) #선택된 파일의 경로를 받아 옴
            if os.path.exists(filePath): #선택된 파일이 존재한다면
                self.mainExplorer.edit(file) #선택된 파일의 이름을 바꿔줌
                self.mainExplorer.edit(file) #선택된 파일의 이름을 바꿔줌