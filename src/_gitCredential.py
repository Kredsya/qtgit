import sys
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
    QMessageBox,
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

        self.textEdit_github_username = QTextEdit()
        self.vbox.addWidget(self.textEdit_github_username)

        self.label = QLabel("Personal access token")
        self.vbox.addWidget(self.label)

        self.textEdit_personal_access_token = QTextEdit()
        self.vbox.addWidget(self.textEdit_personal_access_token)

        self.button = QPushButton("Save", self)
        self.vbox.addWidget(self.button)
        self.button.clicked.connect(self.save_git_credential)

    def save_git_credential(self):
        file_path = "C:/QtGit/git_credential.txt"
        try:
            with open(file_path, "w") as file:
                file.write(self.textEdit_github_username.toPlainText() + "\n")
                file.write(self.textEdit_personal_access_token.toPlainText() + "\n")
            QMessageBox.information(self, "Save Git Credential", "Saved successfully!")
        except IOError:
            QMessageBox.warning(self, "Save Git Credential", "Cannot write to file.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GitCredential()
    ex.show()
    sys.exit(app.exec_())
