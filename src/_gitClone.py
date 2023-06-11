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

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.label = QLabel(
            "Only an HTTPS URL is supported. An SSH URL is not supported."
        )
        self.vbox.addWidget(self.label)

        self.label = QLabel("Provide the web URL")
        self.vbox.addWidget(self.label)

        self.textEdit = QTextEdit()
        self.vbox.addWidget(self.textEdit)

        self.checkbox = QCheckBox("Is this repository private?")
        self.vbox.addWidget(self.checkbox)

        self.button = QPushButton("Clone")
        self.vbox.addWidget(self.button)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GitClone()
    ex.show()
    sys.exit(app.exec_())
