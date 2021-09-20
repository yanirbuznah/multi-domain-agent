import cPickle
import os
import sys
from timeit import default_timer as timer

from pddlsim.fd_parser import FDParser
from pddlsim.local_simulator import LocalSimulator
from pddlsim.services.simulator_services import SimulatorServices
from pddlsim.simulator import Simulator

from Executors.Executors_helpers.goals_parser_helpers import get_goal_index_in_list
from Executors.executive import Executive
from Executors.learner_executor import Learner
from Executors.learning_from_plan_executor import LearningFromPlanExecutor
from probabilistic_to_determenistic_parser import parser


class MyExecutive():
    def __init__(self, flag, domain, problem):
        self.flag = flag
        self.domain = domain
        self.problem = problem
        self.services = self.get_services()
        self.init_data('my_executive_data' + self.domain + self.problem)
        self.pre_process()

    def get_services(self):
        parser = FDParser(self.domain, self.problem)
        sim = Simulator(parser)
        service_parser = parser
        return SimulatorServices(
            service_parser, sim.perceive_state, None)

    def init_data(self, data_path):
        if os.path.exists(data_path) and os.stat(data_path).st_size != 0:
            self.first_learning = False
            with open(data_path) as file:
                self.data = cPickle.load(file)
            self.data['count'] += 1
            self.model_index = get_goal_index_in_list(self.data['goals'], self.services.parser.goals[0])

        else:
            self.data = {'count': 0, 'goals': [self.services.parser.goals[0]], 'planning_success': False}
            self.model_index = 0

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

    def run(self):
        if self.flag == '-E':
            if self.data['count'] == 0 or self.data['planning_success']:
                executor = LocalSimulator().run(domain, problem,
                                                LearningFromPlanExecutor(self.deterministic_domain, "policy_maze"))
                if executor.success:
                    print executor
                    return True

            executor = LocalSimulator().run(domain, problem, Executive("policy_maze"))
            if executor.success:
                print executor
                return True
        else:
            if self.data['count'] == 0:
                LocalSimulator().run(domain, problem,
                                     LearningFromPlanExecutor(self.deterministic_domain, "policy_maze"))
            for i in range(10):
                LocalSimulator().run(domain, problem, Learner("policy_maze"))

    def planning(self):
        planning = LocalSimulator(print_actions=False).run(domain, problem,
                                                           LearningFromPlanExecutor(self.deterministic_domain,
                                                                                    "policy_maze"))
        self.data['planning_success'] = planning.success
        self.data['count'] += 1

    def pre_process(self):
        self.is_deterministic = self.deterministic()
        self.has_hidden_objects = self.check_hidden_objects()
        self.deterministic_domain = self.create_deterministic_domain()




if __name__ == '__main__':
    flag = sys.argv[1]
    domain = sys.argv[2]
    problem = sys.argv[3]
    my_executive = MyExecutive(flag, domain, problem)
    my_executive.planning()
    my_executive.run()

    # deterministic_domain = my_executive.create_deterministic_domain()
    # z = LocalSimulator(print_actions=False).run(domain,problem,LearningFromPlanExecutor(deterministic_domain,"policy_maze"))
    #
    # print(z.success)
    # sleep(10)
    # #print LocalSimulator().run(domain,problem,RLExecutor("-L","x"))
    # total_execute_times = []
    # total_execute_actions = []
    # if flag == "-L":
    #     for j in range(5):
    #
    #         total_actions = []
    #         total_times = []
    #         for i in range(10):
    #             x = LocalSimulator().run(domain,problem,Learner("policy_maze"))
    #             total_actions.append(x.total_actions)
    #             total_times.append(float(x.total_time)/60)
    #             print x
    #             print "i:", i , "j:", j
    #             sleep(5)
    #         print "Total actions:", total_actions
    #         print "Total times:", total_times
    # else:
    #     x = LocalSimulator().run(domain,problem,Executive("policy_maze"))
    #     total_execute_actions.append(x.total_actions)
    #     total_execute_times.append(float(x.total_time)/60)
    #     print x
    #     sleep(10)
    #
    #
    #
    # print "Total execute actions:", total_execute_actions
    # print "Total execute times:", total_execute_times
    # data = {"tea" :total_execute_actions,"tet": total_execute_times}
    # a_file = open("result", "w")
    # cPickle.dump(data, a_file)
    # a_file.close()
    # pre_process(domain,problem)
    #
