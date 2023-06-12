import os, subprocess

def parse_git_status(status):
    lines = status.split('\n')

    stages = {
        'Changes to be committed:': [],
        'Changes not staged for commit:': [],
        'Untracked files:': [],
    }

    current_section = None
    for line in lines:
        line = line.strip()
        if line in stages:
            current_section = line
        elif line.startswith(('modified:', 'new file:', 'deleted:', 'renamed:')):
            if current_section:
                filename = line.split(':   ')[-1]
                if not '"' in filename and not "'" in filename and not "*" in filename and not "'" in filename and not "?" in filename and not "<" in filename and not ">" in filename and not "|" in filename:
                    stages[current_section].append(filename)
        elif current_section == 'Untracked files:' and line and line != '(use "git add <file>..." to include in what will be committed)' and line != 'no changes added to commit (use "git add" and/or "git commit -a")':
            if not '"' in line and not "'" in line and not "*" in line and not "'" in line and not "?" in line and not "<" in line and not ">" in line and not "|" in line:
                stages[current_section].append(line)

    # Rename keys for clarity
    stages['staged'] = stages.pop('Changes to be committed:')
    stages['modified'] = stages.pop('Changes not staged for commit:')
    stages['untracked'] = stages.pop('Untracked files:')
    return stages

def parse_staged_files(status):
    statusResult = status.split('\n')
    stagedFiles = []
    flag = False
    for line in statusResult:
        line = line.strip()
        if line.startswith("(use"):
            flag = True
            continue
        elif flag and line == '':
            break
        
        if flag:
            stagedFiles.append(line)
    return stagedFiles

def parse_git_current_branch(status):
    if status == "":
        return ""
    statusResult = (status.split('\n')[0]).split()[-1]
    return " (" + statusResult + ")"

def make_branch_list():
    ret_list = subprocess.check_output(['git', 'branch', '-l']).decode('utf-8').split('\n')
    ret_list.remove('')
    for i in range(len(ret_list)):
        if ret_list[i][0] == '*':
            ret_list[i].replace('*', '')
        ret_list[i] = ret_list[i].lstrip().split()[-1]
    return ret_list

def is_gitrepo(dir):
    if not os.path.exists(dir):
        return False
    original_path = os.getcwd()
    os.chdir(dir)
    result = os.popen("git status").read()
    os.chdir(original_path)

    if "not a git" in result:
        return False
    return True

def isTargetOfAdd(gitState):
    if gitState == "modified" or gitState == "untracked":
        return True
    elif gitState == "modified & staged":
        return True
    else:
        return False
    
def isTargetOfRestore(gitState):
    if gitState == "unmodified" or gitState == "staged" or gitState == "untracked" or gitState == "modified & staged":
        return True
    else:
        return False

def isTargetOfRmDelete(gitState):
    if gitState != "untracked":
        return True
    else:
        return False

def isTargetOfUntrack(gitState):
    if gitState != "untracked":
        return True
    else:
        return False

'''
# This function is not used
def isTargetOfCommit(self, gitState):
    if gitState == "staged":
        return True
    else:
        return False
'''