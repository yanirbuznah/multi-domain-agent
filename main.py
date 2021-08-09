from pddlsim.local_simulator import LocalSimulator

from Executors.planning_executor import PlanDispatcher
from file_compare import find_current_files
import sys
import pandas as pd
from Executors.football_and_maze_executor import BehaviorBaseExecutor
import pickle

def get_executor(domain,problem):
    df = pd.read_pickle("knowledge_table.pkl")
    with open(domain) as f:
        if 'probabilistic' not in f.read():
            return PlanDispatcher

    t = find_current_files(domain=domain,problem=problem)
    if (t["new_domain"] == True and t["new_problem"] == True):
        pass
        #TODO: RMAX ?
    if(t["new_domain"] == False):
        row_index = df.index[df['domain'] == t["domain_name"]].tolist()
        if(t["new_problem"] == True):
            row = df.loc[row_index[0]]
            df = df.append(row,ignore_index=True)
            df.at[row_index[0],'problem'] = t['problem_name']
            df.to_pickle("knowledge_table.pkl")

        return df.at[row_index[0],"type"]



def add_executor():
    d = {'domain': ['domain_1628530125.pddl','domain_1628534691.pddl'], 'problem': ['domain_1628530125.pddl','problem_1628534691.pddl'],'type':[BehaviorBaseExecutor,BehaviorBaseExecutor],'config_file':[None,None],'policyfile':[None,None]}
    df = pd.DataFrame(data=d)
    df.to_pickle("knowledge_table.pkl")



if __name__ == '__main__':
    add_executor()
    domain = sys.argv[1]
    problem = sys.argv[2]
    executor = get_executor(domain,problem)
    print LocalSimulator().run(domain,problem,executor())




#
#
#
# if (t["new_domain"] == True or t["new_problem"] == True ):
#     print LocalSimulator().run(domain,problem,PlanDispatcher())


