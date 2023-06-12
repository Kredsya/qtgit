# Documentation

## User guide

### File explorer

The file explorer starts from the home directory.

### Initialization of a Git repository

Go to the folder you want and click Git - Git Init.

### Version control of a Git repository

To run git add command, click Git - Add. To run git restore command, click Git - Restore. To run git commit command, click Git - Commit. To run git rm command, click Git - Rm(Delete file). To run git rm --cached command, click Git - Rm(Untrack file).

### Branch management of a Git repository

If it is a Git repository, the branch name is displayed next to the folder name in the title of the window. To create a branch, click Branch - Create, enter the branch name you want, and click the OK button. To delete a branch, click Branch - Delete, select the branch name you want, and click the OK button. To rename a branch, click Branch - Rename, select a branch to rename, enter the branch name you want, and click the OK button. To checkout a branch, click Branch - Checkout, select the branch name you want, and click the OK button. To merge a branch, click Branch - Merge, select the branch name you want, and click the OK button.

### Commit history of a Git repository

Go to the folder you want and click Git - Log Graph.

### Cloning the Git repository

Enter the web URL in Git - Clone and click the Clone button. If it is a private repository, you will need to provide the GitHub username and personal access token. If you have never set up a credential before, a window will automatically pop up allowing you to enter and save these. If you want to change to a different credential, you can do so in Git - Credential.

## Internally used Git commands

### git init

Create an empty Git repository or reinitialize an existing one

### git add

Add file contents to the index

### git restore

Restore working tree files

**--staged**: Specify the restore location. If neither option is specified, by default the working tree is restored. Specifying --staged will only restore the index. Specifying both restores both.

### git rm

Remove files from the working tree and from the index

### git mv

Move or rename a file, a directory, or a symlink

### git commit

Record changes to the repository
