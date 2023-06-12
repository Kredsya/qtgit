import os
import subprocess
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
            "This clones the repository in your home directory. Only a HTTPS URL is supported. A SSH URL is not supported."
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
            web_url = self.textEdit.toPlainText()
            home_directory = os.path.expanduser("~")

            try:
                with open(file_path, "r") as file:
                    lines = file.readlines()

                github_username = lines[0].strip()
                personal_access_token = lines[1].strip()
                web_url_with_credential = web_url.replace(
                    "https://", f"https://{github_username}:{personal_access_token}@"
                )

                try:
                    subprocess.run(
                        ["git", "clone", web_url_with_credential],
                        cwd=home_directory,
                        check=True,
                    )
                    QMessageBox.information(
                        self, "Execute Git Clone", "Cloned successfully!"
                    )
                except subprocess.CalledProcessError:
                    QMessageBox.warning(
                        self,
                        "Execute Git Clone",
                        "Git clone failed. The credential is incorrect or the repository has already been cloned.",
                    )
            except FileNotFoundError:
                self.git_credential_window = GitCredential()
                self.git_credential_window.show()
                QMessageBox.warning(self, "Execute Git Clone", "Credential not found.")
            except IOError:
                QMessageBox.warning(self, "Execute Git Clone", "Cannot read file.")
        else:
            try:
                subprocess.run(
                    ["git", "clone", web_url], cwd=home_directory, check=True
                )
                QMessageBox.information(
                    self, "Execute Git Clone", "Cloned successfully!"
                )
            except subprocess.CalledProcessError:
                QMessageBox.warning(
                    self,
                    "Execute Git Clone",
                    "Git clone failed. The credential is incorrect or the repository has already been cloned.",
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GitClone()
    ex.show()
    sys.exit(app.exec_())
