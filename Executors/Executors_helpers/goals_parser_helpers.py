
from pddlsim.parser_independent import *

def literal_correlation(goal1,goal2):
    return int(goal1.args == goal2.args)

def disjunction_correlation(goal1,goal2):
    for i in goal1.parts:
        for j in goal2.parts:
            if (literal_correlation(i,j) == 1):
                return 1
    return 0

def conjunction_correlation(goal1,goal2):
    count =0
    for i in goal1.parts:
        for j in goal2.parts:
            if (literal_correlation(i, j) == 1):
                 count += 1
    return count/len(goal1.parts)


def get_correlation(goal1,goal2):
    if isinstance(goal1,Conjunction):
        return conjunction_correlation(goal1,goal2)
    if isinstance(goal1,Disjunction):
        return disjunction_correlation(goal1,goal2)
    return None

def check_equality(goal1,goal2):
    if type(goal1) == type(goal2):
        if isinstance(goal1,Literal):
            return goal1.args == goal2.args
        if len(goal1.parts) == len(goal2.parts):
            for i in range (len(goal1.parts)):
                if not check_equality(goal1.parts[i], goal2.parts[i]):
                    return False
            return True
    return False

def check_if_goal_in_list(list_of_goals,goal):
    for g in list_of_goals:
        if check_equality(g,goal):
            return True
    return False