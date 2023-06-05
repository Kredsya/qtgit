import sys
from PyQt5.QtWidgets import QWidget, QApplication
class GitLogViewer(QWidget):
    def __init__(self):
        super().__init__()
        #self.initUI()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GitLogViewer()
    ex.show()
    sys.exit(app.exec_())