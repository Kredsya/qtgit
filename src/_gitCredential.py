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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GitCredential()
    ex.show()
    sys.exit(app.exec_())
