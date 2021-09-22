import cPickle
import multiprocessing
import os
import sys
from time import sleep
from timeit import default_timer as timer

from pddlsim.fd_parser import FDParser
from pddlsim.local_simulator import LocalSimulator
from pddlsim.services.simulator_services import SimulatorServices
from pddlsim.simulator import Simulator

from Executors.Executors_helpers.goals_parser_helpers import get_goal_index_in_list
from Executors.Executors_helpers.probabilistic_to_determenistic_parser import parser
from Executors.executive import Executive
from Executors.learner_executor import Learner
from Executors.learning_from_plan_executor import LearningFromPlanExecutor


class MyExecutive():
    def __init__(self, flag, domain, problem):
        self.flag = flag
        self.domain = domain
        self.problem = problem
        self.problem_name = problem.split('/')[-1][:-5]
        self.services = self.get_services()
        self.data_path = os.path.join(os.getcwd(), os.path.join("meta_data_files"),
                                      'my_executive_data_' +  self.problem_name.split('-')[0])
        self.init_data()
        self.pre_process()
        #The problem name will be composed of two parts: "<env>-<task>"
        self.policy_file = "policy_file_" + self.problem_name.split('-')[0]

    def get_services(self):
        parser = FDParser(self.domain, self.problem)
        sim = Simulator(parser)
        service_parser = parser
        return SimulatorServices(
            service_parser, sim.perceive_state, None)

    def init_data(self):
        if os.path.exists(self.data_path) and os.stat(self.data_path).st_size != 0:
            self.first_learning = False
            with open(self.data_path) as file:
                self.data = cPickle.load(file)
            self.model_index = get_goal_index_in_list(self.data['goals'], self.services.parser.goals[0])
            try:
                self.data['count'][self.model_index]+=1
            except:
                self.data['count'].append(0)
                self.data['planning_success'].append(False)
                self.data['bests'].append(sys.maxint)

        else:
            self.data = {'count': [0], 'goals': [self.services.parser.goals[0]], 'planning_success': [False], 'bests':[sys.maxint]}
            self.model_index = 0


    def save_data(self):
        a_file = open(self.data_path, "w")
        start = timer()
        cPickle.dump(self.data, a_file)
        a_file.close()
        print "time to save file: ", timer() - start, "seconds"
        print "size of the file:", float(os.stat(self.data_path).st_size) / 1048576, "MB"

    def deterministic(self):
        with open(self.domain) as f:
            content = f.read()
            return not "probabilistic" in content

    def check_hidden_objects(self):
        with open(self.problem) as f:
            content = f.read()
            return ":reveal" in content

    def create_deterministic_domain(self):
        lines = parser(self.domain)
        deterministic_domain_name = self.domain[:-5] + "_deterministic" + ".pddl"
        with open(deterministic_domain_name, 'w') as f:
            f.writelines(lines)
        return deterministic_domain_name

    def run_specific_executor(self, return_dict,executor):
        if executor == 'LearningFromPlanExecutor':
            return_dict['s'] = LocalSimulator().run(domain, problem,
                                                LearningFromPlanExecutor(self.deterministic_domain, self.policy_file))
        else:
            return_dict['s'] = LocalSimulator().run(domain, problem, Executive(self.policy_file))


    def run_executors(self,return_dict,executor):
        p = multiprocessing.Process(target=self.run_specific_executor, args=(return_dict, executor))
        p.start()
        p.join(600)
        if p.is_alive():
            p.terminate()
            p.join()
            print "\nIts take to much time. trying with Executive!\n"
            sleep(1)
        if 's' in return_dict.keys():
            p.terminate()
            return return_dict['s'].success
        return False

    def run(self):
        if self.flag == '-E':
            if self.data['count'][self.model_index] == 0 or self.data['planning_success'][self.model_index]:
                manager = multiprocessing.Manager()
                return_dict = manager.dict()

                if self.run_executors(return_dict,'LearningFromPlanExecutor'):
                    return return_dict['s']
                if self.run_executors(return_dict,'executiveFromPlan'):
                    return return_dict['s']


            executor = LocalSimulator().run(domain, problem, Executive(self.policy_file+'_learner'))
            if executor.success:
                return executor

        else:
            if self.data['count'][self.model_index] < 50:
                for i in range(20):
                    self.planning()
            else:
                for i in range(5):
                    self.learning()
                    # TODO: remove sleep
                    sleep(5)

    def planning(self):
        planning = LocalSimulator(print_actions=False).run(domain, problem,
                                                           LearningFromPlanExecutor(self.deterministic_domain,
                                                                                    self.policy_file))
        self.data['planning_success'][self.model_index] = planning.success
        self.data['count'][self.model_index] += 1
        self.data['bests'][self.model_index] = min(planning.total_actions,self.data['bests'][self.model_index])

        self.save_data()

    def learning(self):
        learning = LocalSimulator().run(domain, problem, Learner(self.policy_file+'_learner',self.data['bests'][self.model_index]))
        self.data['count'][self.model_index] += 1
        self.data['bests'][self.model_index] = min(learning.total_actions,self.data['bests'][self.model_index])
        self.save_data()

    def pre_process(self):
        self.is_deterministic = self.deterministic()
        self.has_hidden_objects = self.check_hidden_objects()
        if self.is_deterministic:
            self.deterministic_domain = self.domain
        else:
            self.deterministic_domain = self.create_deterministic_domain()


if __name__ == '__main__':
    flag = sys.argv[1]
    domain = sys.argv[2]
    problem = sys.argv[3]
    my_executive = MyExecutive(flag, domain, problem)
    # TODO: Remove for loop
    for i in range(3):
        print my_executive.run()
    my_executive.flag = "-E"
    print my_executive.run()
