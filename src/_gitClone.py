import os
import sys
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
    QCheckBox,
    QMessageBox,
)
from _gitCredential import *


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

        self.button = QPushButton("Clone", self)
        self.vbox.addWidget(self.button)
        self.button.clicked.connect(self.exec_git_clone)

    def exec_git_clone(self):
        if self.checkbox.isChecked():
            file_path = "C:/QtGit/git_credential.txt"
            try:
                with open(file_path, "r") as file:
                    lines = file.readlines()
                os.system(
                    "git clone "
                    + self.textEdit[0:8]
                    + lines[0]
                    + ":"
                    + lines[1]
                    + "@"
                    + self.textEdit[8:]
                )
                QMessageBox.information(
                    self, "Execute Git Clone", "Cloned successfully!"
                )
            except FileNotFoundError:
                self.git_credential_window = GitCredential()
                self.git_credential_window.show()
                QMessageBox.warning(self, "Execute Git Clone", "Credential not found.")
            except IOError:
                QMessageBox.warning(self, "Execute Git Clone", "Cannot read file.")
        else:
            os.system("git clone " + self.textEdit)
            QMessageBox.information(self, "Execute Git Clone", "Cloned successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GitClone()
    ex.show()
    sys.exit(app.exec_())
