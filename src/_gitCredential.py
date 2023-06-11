import sys
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
)


class GitCredential(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 50)
        self.setWindowTitle("Git Credential")

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.label = QLabel(
            "Provide the GitHub username and personal access token in order to access private repositories."
        )
        self.vbox.addWidget(self.label)

        self.label = QLabel("GitHub username")
        self.vbox.addWidget(self.label)

        self.textEdit = QTextEdit()
        self.vbox.addWidget(self.textEdit)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GitCredential()
    ex.show()
    sys.exit(app.exec_())
