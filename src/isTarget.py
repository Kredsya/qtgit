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