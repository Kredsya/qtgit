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
            self.listWidget.addItem(log)

    def on_itemClicked(self, item):
        log = remove_ansi_color_codes(item.text())
        # log에서 '\','*','|','/'를 제거
        log = log.replace('\\', '')
        log = log.replace('*', '')
        log = log.replace('|', '')
        log = log.replace('/', '')
        # log에서 commit hash만 추출
        commit_hash = log.split(' ')
        while '' in commit_hash:
            commit_hash.remove('')
        if len(commit_hash) == 0:
            self.textEdit1.setPlainText("커밋오브젝트가 아닙니다.")
            self.textEdit2.setPlainText("")
            self.textEdit3.setPlainText("")
            return
        commit_hash = commit_hash[0]

        details = subprocess.check_output(['git', 'show', '--pretty=format:%ci%n%an%n%d', commit_hash], encoding='utf8')
        tmp = details.split('\n')
        commit_time = tmp[0]
        commit_author = tmp[1]

        commit_time = commit_time.split()
        commit_time = "날짜 : " + commit_time[0] + "\n시간 : " + commit_time[1] + "(" + commit_time[2]+ ")"
        # git show 명령어 실행
        command = ["git", "show", "--format=%an <%ae>", commit_hash]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        author_email = result.stdout.strip().split('<')[1].split('>')[0]
        commit_author = "이름 : " + commit_author + "\n이메일 : " + author_email

        if "index" in details:
            details = details.split("index")[1]
            details = details.split("\n", 1)[1]
            details = "변경사항\n" + details
        else:
            details = log.lstrip()
        self.textEdit1.setPlainText(commit_time)
        self.textEdit2.setPlainText(commit_author)
        self.textEdit3.setPlainText(details)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GitLogViewer()
    ex.show()
    sys.exit(app.exec_())