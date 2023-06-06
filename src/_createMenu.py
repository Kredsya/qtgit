from PyQt5.QtWidgets import QAction
from _fileAction import fileAction

class createMenu(fileAction):
    def createTopMenu(self):
        # Add menus
        menuBar = self.menuBar()  # 상단 메뉴바

        fileMenu = menuBar.addMenu('&File')  # 메뉴바에 File Edit View Git Help 추가
        editMenu = menuBar.addMenu("&Edit")
        viewMenu = menuBar.addMenu("&View")
        gitMenu = menuBar.addMenu("&Git")
        branchMenu = menuBar.addMenu("&Branch")

        # File
        # New Exit는 해당 QAction이 trigger되었을때 connect되는 것이 없어서 해당 매뉴를 클릭해도 동작하지 않는 것으로 보임
        newAction = QAction('&New', self)
        newAction.setStatusTip('New')  # 상단 메뉴바의 File을 클릭하면 New매뉴가 보이도록

        exitAction = QAction('&Exit', self)
        exitAction.setStatusTip('Exit')  # 상단 메뉴바의 File을 클릭하면 Exit매뉴가 보이도록

        fileMenu.addAction(newAction)  # editMenu에 Qaction들 추가
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # Edit
        # cut copy paste는 해당 QAction이 trigger되었을때 connect되는 것이 없어서 해당 매뉴를 클릭해도 동작하지 않는 것으로 보임
        cutAction = QAction('&Cut', self)
        cutAction.setStatusTip('Cut')  # 상단 메뉴바의 Edit를 클릭하면 Cut매뉴가 보이도록

        copyAction = QAction('&Copy', self)
        copyAction.setStatusTip('Copy')  # 상단 메뉴바의 Edit를 클릭하면 Copy매뉴가 보이도록

        pasteAction = QAction('&Paste', self)
        pasteAction.setStatusTip('Paste')  # 상단 메뉴바의 Edit를 클릭하면 Paste매뉴가 보이도록

        selectAllAction = QAction('&Select All', self)
        selectAllAction.setStatusTip('Select All')  # 상단 메뉴바의 Edit를 클릭하면 Select All매뉴가 보이도록
        selectAllAction.triggered.connect(self.selectAll)  # selectAllAction이 trigger될 경우 self.selectAll실행

        unselectAllAction = QAction('&Unselect All', self)
        unselectAllAction.setStatusTip('Unselect All')  # 상단 메뉴바의 Edit를 클릭하면 Unselect All매뉴가 보이도록
        unselectAllAction.triggered.connect(self.unselectAll)  # unselectAllAction이 trigger될 경우 self.unselectAll실행

        editMenu.addAction(cutAction)  # editMenu에 Qaction들 추가
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(selectAllAction)
        editMenu.addAction(unselectAllAction)

        # View
        iconsViewAction = QAction('&Icons', self)
        iconsViewAction.setStatusTip('Change view as Icon only')  # 상단 메뉴바의 View를 클릭하면 Icons매뉴가 보이도록
        iconsViewAction.triggered.connect(
            lambda checked: self.changeView("Icons"))  # iconsViewAction이 triggger될경우  self.changeView("Icons")실행

        listViewAction = QAction('&List', self)
        listViewAction.setStatusTip('Change view as File name only')  # 상단 메뉴바의 View를 클릭하면 List매뉴가 보이도록
        listViewAction.triggered.connect(
            lambda checked: self.changeView("List"))  # listViewAction이 triggger될경우  self.changeView("List")실행

        detailViewAction = QAction('&Details', self)
        detailViewAction.setStatusTip('Change view as Details (default)')  # 상단 메뉴바의 View를 클릭하면 Details매뉴가 보이도록
        detailViewAction.triggered.connect(
            lambda checked: self.changeView("Details"))  # detailViewAction이 triggger될경우  self.changeView("Details")실행

        viewMenu.addAction(iconsViewAction)  # viewMenu에 Qaction들 추가
        viewMenu.addAction(listViewAction)
        viewMenu.addAction(detailViewAction)

        # Git
        gitInitAction = QAction('&Git Init', self) # 상단 메뉴바의 Git을 클릭하면 Repository Create매뉴가 보이도록
        gitInitAction.setStatusTip('Execute <git init> command') # 하단 메뉴바에 해당 메뉴에 대한 설명 표시
        gitInitAction.triggered.connect(self.GitInit)  # gitInitAction이 triggger될경우  self.GitInit

        gitAddAction = QAction('&Add', self)
        gitAddAction.setStatusTip('Execute <git add [selected]> command')
        gitAddAction.triggered.connect(self.GitAdd)

        gitRestoreAction = QAction('&Restore', self)
        gitRestoreAction.setStatusTip('Execute <git restore [selected]> or <git restore --staged [selected]> command')
        gitRestoreAction.triggered.connect(self.GitRestore)
        
        gitRmDeleteAction = QAction('&Rm(Delete file)', self)
        gitRmDeleteAction.setStatusTip('Execute <git rm --cached [selected]> command')
        gitRmDeleteAction.triggered.connect(self.GitRmDelete)

        gitRmUntrackAction = QAction('&Rm(Untrack file)', self)
        gitRmUntrackAction.setStatusTip('Execute <git rm [selected]> command')
        gitRmUntrackAction.triggered.connect(self.GitRmUntrack)

        gitCommitAction = QAction('&Commit', self)
        gitCommitAction.setStatusTip('Confirm about staged files and Execute <git commit -m [message]> command')
        gitCommitAction.triggered.connect(self.GitCommit)

        gitMenu.addAction(gitInitAction)  # gitMenu(menuBar.addMenu("&Git"))에 Qaction추가
        gitMenu.addAction(gitAddAction)
        gitMenu.addAction(gitRestoreAction)
        gitMenu.addAction(gitRmDeleteAction)
        gitMenu.addAction(gitRmUntrackAction)
        gitMenu.addAction(gitCommitAction)

        # Branch
        branchCreateAction = QAction('&Create', self)
        branchCreateAction.setStatusTip('Tip')
        branchCreateAction.triggered.connect(self.BranchCreate)

        branchDeleteAction = QAction('&Delete', self)
        branchDeleteAction.setStatusTip('Tip')
        branchDeleteAction.triggered.connect(self.BranchDelete)

        branchRenameAction = QAction('&Rename', self)
        branchRenameAction.setStatusTip('Tip')
        branchRenameAction.triggered.connect(self.BranchRename)

        branchCheckoutAction = QAction('&Checkout', self)
        branchCheckoutAction.setStatusTip('Tip')
        branchCheckoutAction.triggered.connect(self.BranchCheckout)

        branchMenu.addAction(branchCreateAction)
        branchMenu.addAction(branchDeleteAction)
        branchMenu.addAction(branchRenameAction)
        branchMenu.addAction(branchCheckoutAction)