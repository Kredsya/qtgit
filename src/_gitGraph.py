import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout ,QHBoxLayout , QListWidget, QTextEdit, QLabel, QListWidgetItem
import re
import subprocess
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize, Qt
from ansi2html import Ansi2HTMLConverter
from bs4 import BeautifulSoup
def extract_changed_file(input_str):
    pattern = re.compile(r'diff --git a/(.*?) b/')
    matches = pattern.findall(input_str)
    if '(.*?)' in matches:
        matches.remove('(.*?)')
    return matches
def remove_html_css(content):
    soup = BeautifulSoup(content, "html.parser")

    # Remove all style (css) tags
    for style in soup("style"):
        style.decompose()

    # Get the text property of the soup object
    text = soup.get_text(separator=" ")

    # Use regular expressions to further clean up, remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    return text
def convert_ansi_to_html(ansi_str):
    conv = Ansi2HTMLConverter()
    html = conv.convert(ansi_str)
    return html

def remove_ansi_color_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
class ClickableQLabel(QLabel):
    def __init__(self, text=None, parent=None):
        QLabel.__init__(self, text, parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.parent().parent().parent().on_itemClicked(remove_html_css(self.text()))

class FileNameQLabel(QLabel):
    def __init__(self, text=None, parent=None):
        QLabel.__init__(self, text, parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.parent().parent().parent().on_itemClicked(self.text(), False)
class GitLogViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.FileChanged = dict()

    def initUI(self):
        self.setGeometry(100, 100, 1800, 1000)
        self.setWindowTitle('Git Log')

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.listWidget = QListWidget()
        self.listWidget.setFont(QFont('Courier New', 10))

        self.textEdit1 = QTextEdit()
        self.textEdit1.setReadOnly(True)

        self.textEdit2 = QTextEdit()
        self.textEdit2.setReadOnly(True)

        self.listWidget2 = QListWidget()
        self.listWidget2.setFont(QFont('Courier New', 10))
        self.textEdit3 = QTextEdit()

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.listWidget2)
        self.hbox.addWidget(self.textEdit3)

        self.vbox.addWidget(self.listWidget)
        self.vbox.addWidget(self.textEdit1)
        self.vbox.addWidget(self.textEdit2)
        self.vbox.addLayout(self.hbox)

        # 높이 비율 설정
        self.vbox.setStretch(0, 40)
        self.vbox.setStretch(1, 1)
        self.vbox.setStretch(2, 1)
        self.vbox.setStretch(3, 58)

        # 너비 비율 설정
        self.hbox.setStretch(0, 1)
        self.hbox.setStretch(1, 5)

        self.load_git_log()

    def load_git_log(self):
        output = subprocess.check_output(['git', 'log', '--all', '--decorate', '--color', '--oneline', '--graph', '--date-order'],
                                         encoding='utf8')
        logs = output.split('\n')

        for log in logs:
            html_str = convert_ansi_to_html(log)
            label = ClickableQLabel(html_str.replace('*', '●'), self.listWidget)
            label.setTextFormat(Qt.RichText)
            item = QListWidgetItem()
            item.setSizeHint(QSize(100, 18))
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, label)

    def on_itemClicked(self, log, is_commit=True):
        if is_commit:
            self.FileChanged.clear()
            # log에서 '\','●','|','/','_'를 제거
            log = log.replace('\\', '')
            log = log.replace('●', '')
            log = log.replace('|', '')
            log = log.replace('/', '')
            log = log.replace('_', '')
            # log에서 commit hash만 추출
            commit_hash = log.split(' ')
            while '' in commit_hash:
                commit_hash.remove('')
            if len(commit_hash) == 0:
                self.textEdit1.setPlainText("커밋오브젝트가 아닙니다.")
                self.listWidget2.clear()
                self.textEdit2.setPlainText("")
                self.textEdit3.setPlainText("")
                return
            commit_hash = commit_hash[0]

            details = subprocess.check_output(['git', 'show', '--pretty=format:%ci%n%an%n%d', commit_hash],
                                              encoding='utf8')

            # details에서 변경된 파일 추출
            changed_files = extract_changed_file(details)
            self.listWidget2.clear()
            for file in changed_files:
                item = QListWidgetItem()
                item.setSizeHint(QSize(100, 20))
                self.listWidget2.addItem(item)
                self.listWidget2.setItemWidget(item, FileNameQLabel(file))

                # git show 명령어 실행
                command = 'git show --pretty=format: ' + commit_hash + ' -- ' + file
                result = subprocess.run(command, capture_output=True, text=True, shell=True, encoding='utf8')
                gitdiff = result.stdout
                #gitdiff의 앞두줄 자르기
                gitdiff = gitdiff.split('\n')
                gitdiff = gitdiff[2:]
                gitdiff = '\n'.join(gitdiff)
                self.FileChanged[file] = gitdiff

            # details에서 시간, 이름을 추출
            tmp = details.split('\n')
            commit_time = tmp[0]
            commit_author = tmp[1]

            commit_time = commit_time.split()
            commit_time = "날짜 : " + commit_time[0] + "\n시간 : " + commit_time[1] + "(" + commit_time[2] + ")"
            # git show 명령어 실행
            command = ["git", "show", "--format=%an <%ae>", commit_hash]
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            author_email = result.stdout.strip().split('<')[1].split('>')[0]
            commit_author = "이름 : " + commit_author + "\n이메일 : " + author_email

            if "index" in details:
                details = "왼쪽에서 파일을 선택하시면 해당 파일의 변경사항을 볼 수 있습니다."
            else:
                details = log.lstrip()
            self.textEdit1.setPlainText(commit_time)
            self.textEdit2.setPlainText(commit_author)
            self.textEdit3.setPlainText(details)
        else:
            self.textEdit3.setPlainText(self.FileChanged[log])
