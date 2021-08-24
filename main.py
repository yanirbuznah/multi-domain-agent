import cPickle
import os

from pddlsim.local_simulator import LocalSimulator

from Executors.planning_executor import PlanDispatcher
from file_compare import find_current_files
import sys
import pandas as pd
from Executors.football_and_maze_executor import BehaviorBaseExecutor
from Executors.maze_q_learning_executor import RLExecutor
from time import time


def get_executor(domain,problem):
    df = pd.read_pickle("knowledge_table.pkl")
    with open(domain) as f:
        if 'probabilistic' not in f.read():
            return PlanDispatcher, None

    t = find_current_files(domain=domain,problem=problem)
    if (t["new_domain"] == True and t["new_problem"] == True):
        exit(113)
        #TODO: RMAX ?
    if(t["new_domain"] == False):
        row_index = df.index[df['domain'] == t["domain_name"]].tolist()
        row = df.loc[row_index[0]]
        executor, policyfile = parse_row(row)
        if issubclass(executor,RLExecutor):
            if(t["new_problem"] == True or policyfile == None):
                now = str(int(time()))
                policyfile ="POLICY"+now
                df.at[row_index[0],'problem'] = t['problem_name']
                df.at[row_index[0],'policyfile'] = policyfile
                df.to_pickle("knowledge_table.pkl")


        elif issubclass(executor,BehaviorBaseExecutor):
            if(t["new_problem"] == True):
                df = df.append(row,ignore_index=True)
                df.at[row_index[0],'problem'] = t['problem_name']
                df.to_pickle("knowledge_table.pkl")

        return executor,policyfile

def parse_row(row):
    return row['type'],row['policyfile']

def add_executor():
    d = {'domain': ['domain_1628610050.pddl','domain_1628610268.pddl','domain_1628610447.pddl'],
         'problem': ['problem_1628610050.pddl','problem_1628610268.pddl','problem_1628610447.pddl'],
         'type':[BehaviorBaseExecutor,BehaviorBaseExecutor,RLExecutor],
         'config_file':[None,None,None],'policyfile':[None,None,None]}
    df = pd.DataFrame(data=d)
    df.to_pickle("knowledge_table.pkl")




if __name__ == '__main__':
    domain = sys.argv[1]
    problem = sys.argv[2]
    flag = sys.argv[3]

    executor,policy = get_executor(domain,problem)
    if policy == None:
        print LocalSimulator().run(domain,problem,executor())
    else:
        for i in range(20):
            print LocalSimulator().run(domain,problem,executor(flag=flag,policy_file=policy))

