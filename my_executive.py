import cPickle
import sys
from probabilistic_to_determenistic_parser import parser
from time import sleep
from timeit import default_timer as timer
from pddlsim.local_simulator import LocalSimulator
from Executors.planning_executor import PlanDispatcher
from Executors.generic_q_executor import RLExecutor
from Executors.learning_executor import LearningExecutor
from Executors.learner_executor import Learner
from Executors.executive import  Executive

def deterministic(domain):
    with open(domain) as f:
        content = f.read()
        return not "probabilistic" in content


def check_hidden_objects(problem):
    with open(problem) as f:
        content = f.read()
        return ":reveal" in content

def create_deterministic_domain(domain):
    lines = parser(domain)
    deterministic_domain_name = domain[:-5] +"_deterministic"+".pddl"
    with open(deterministic_domain_name,'w') as f:
        f.writelines(lines)
    return deterministic_domain_name

def pre_process(domain,problem):
    #TODO:REMOVE
    start = timer()
    it_deterministic = deterministic(domain)
    hidden_objects = check_hidden_objects(problem)
    if deterministic and not hidden_objects:
        return "PLANNER"

    elif not deterministic and hidden_objects:
        print LocalSimulator().run(domain,problem,RLExecutor('-L',"policy_json_satellite"))
        # TODO: MAKE Q-learning
    elif not deterministic and not hidden_objects:
        pass
        # TODO: RMAX
    else:
        pass
        # deterministic and hidden objects
        # TODO: Q-learning?

    deterministic_domain = create_deterministic_domain(domain)
    #print LocalSimulator().run(domain,problem,RLExecutor('-L',"polic"))
    # for i in range(20):
    #     print LocalSimulator().run(domain,problem,RLExecutor('-L',"poli"))
    end = timer()
    print (end - start) , "\nTODO:REMOVE"



if __name__ == '__main__':

    flag = sys.argv[1]
    domain = sys.argv[2]
    problem= sys.argv[3]
#    print LocalSimulator().run(domain,problem,PlanDispatcher())
  #  print LocalSimulator().run(domain,problem,Learner("POLICY_Learner_working"))
    #deterministic_domain = create_deterministic_domain(domain)
    deterministic_domain = create_deterministic_domain(domain)
    #print LocalSimulator().run(domain,problem,LearningExecutor(deterministic_domain))
    #print LocalSimulator().run(domain,problem,RLExecutor("-L","x"))
    total_execute_times = []
    total_execute_actions = []
    if flag == "-L":
        for j in range(1):

            total_actions = []
            total_times = []
            for i in range(1):
                x = LocalSimulator().run(domain,problem,Learner("policy_maze"))
                total_actions.append(x.total_actions)
                total_times.append(float(x.total_time)/60)
                print x
                print "i:", i , "j:", j
                sleep(10)
            print "Total actions:", total_actions
            print "Total times:", total_times
    else:
        x = LocalSimulator().run(domain,problem,Executive("policy_maze"))
        total_execute_actions.append(x.total_actions)
        total_execute_times.append(float(x.total_time)/60)
        print x
        sleep(10)



        print "Total execute actions:", total_execute_actions
        print "Total execute times:", total_execute_times
        data = {"tea" :total_execute_actions,"tet": total_execute_times}
        a_file = open("result", "w")
        cPickle.dump(data, a_file)
        a_file.close()
    pre_process(domain,problem)

