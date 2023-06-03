import shutil
from os.path import isfile, isdir, join
import os
from PyQt5.QtWidgets import QMessageBox

class fileAction():
    def selectAll(self, event):#상단바의 Edit의 selectAll 클릭시, QListView클래스의 selectAll함수 이용.
        self.mainExplorer.selectAll()

    def unselectAll(self):#상단바의 Edit의 unselectAll 클릭시, QListView클래스의 selectionModel함수 이용.
        self.mainExplorer.selectionModel().clearSelection()

    def deleteFiles(self, event): #상단바의 Edit의 delete 클릭시, 선택된 파일들을 삭제하는 메소드
        reply = QMessageBox.question(self, 'Delete', 'Are you sure you sure you want to delete those elements ?', #삭제 여부를 묻는 메시지 박스
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No) #Yes와 No버튼을 생성
        if  reply == QMessageBox.Yes: #Yes버튼을 누르면
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes(); #선택된 파일들의 인덱스를 가져옴
            for file in selectedIndexes: #선택된 파일들을 삭제
                fileName = self.mainModel.itemData(file)[0] #파일의 이름을 가져옴
                filePath = join(self.currentDir, fileName) #파일의 경로를 가져옴
                if os.path.exists(filePath): #파일이 존재하면
                    try:#파일을 삭제
                        if isdir(filePath): #파일이 디렉토리면
                            shutil.rmtree(filePath) #디렉토리를 삭제
                        elif isfile(filePath):#파일이 파일이면
                            os.remove(filePath) #파일을 삭제
                        self.mainModel.remove(file) #QListView에서 파일을 삭제
                    except OSError: #파일을 삭제하는데 실패하면
                        print("failed to delete: " + filePath) #삭제 실패 메시지 출력
                        pass
                else: #파일이 존재하지 않으면
                    self.mainModel.remove(file) #QListView에서 파일을 삭제