import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QListWidget, QTextEdit
import re
import subprocess
from PyQt5.QtGui import QFont
def remove_ansi_color_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class GitLogViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        def initUI(self):
            self.setGeometry(300, 300, 1400, 1000)
            self.setWindowTitle('Git Log')

            self.vbox = QVBoxLayout()
            self.setLayout(self.vbox)

            self.listWidget = QListWidget()
            self.listWidget.setFont(QFont('Courier New', 10))  # Set the font

            self.textEdit1 = QTextEdit()
            self.textEdit1.setReadOnly(True)

            self.textEdit2 = QTextEdit()
            self.textEdit2.setReadOnly(True)
            self.textEdit3 = QTextEdit()
            self.textEdit3.setReadOnly(True)

            self.vbox.addWidget(self.listWidget)
            self.vbox.addWidget(self.textEdit1)
            self.vbox.addWidget(self.textEdit2)
            self.vbox.addWidget(self.textEdit3)

            # 높이 비율 설정
            self.vbox.setStretch(0, 100)
            self.vbox.setStretch(1, 1)
            self.vbox.setStretch(2, 1)
            self.vbox.setStretch(3, 100)

            self.listWidget.itemClicked.connect(self.on_itemClicked)

            self.load_git_log()

    def load_git_log(self):
        output = subprocess.check_output(['git', 'log', '--all', '--decorate', '--color', '--oneline', '--graph'],
                                         encoding='utf8')
        logs = output.split('\n')

        for log in logs:
            self.log_except_color[log] = remove_ansi_color_codes(log)
            self.listWidget.addItem(log)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GitLogViewer()
    ex.show()
    sys.exit(app.exec_())