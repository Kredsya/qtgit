import sys
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
    QCheckBox,
)


class GitClone(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 50)
        self.setWindowTitle("Git Clone")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GitClone()
    ex.show()
    sys.exit(app.exec_())
