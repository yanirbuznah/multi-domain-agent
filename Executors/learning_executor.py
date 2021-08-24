import json
import os
import sys

from pddlsim.local_simulator import LocalSimulator

from executor import Executor
import pddlsim.planner as planner
from pddlsim.services.problem_generator import *
import random
from Executors_helpers.hasing_states import *

class LearningExecutor(Executor):
    def __init__(self,deterministic_domain):
        super(LearningExecutor,self).__init__()
        self.steps = []
        self.data = {'count':0}
        self.last_state = ""
        #self.policy = os.path.join(os.getcwd(),os.path.join("policy_files"),policy_file)
        self.data_list = []
        self.deterministic_domain = deterministic_domain

    def initialize(self,services):

        self.num_of_steps = len(self.steps)
        self.services = services

        state = self.apply_revealable_predicates(self.services.perception.get_state())
        self.services.parser.generate_problem("problem.pddl",state,self.services.goal_tracking.uncompleted_goals[0])
        self.make_plan()

        #self.apply_revealable_predicates(self.services.)

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            return None
        options = self.services.valid_actions.get()
        if len(self.steps) > 0:
            if self.steps[0].lower() not in options:
                state = self.apply_revealable_predicates(self.services.perception.get_state())
                self.services.parser.generate_problem("problem.pddl",state,self.services.goal_tracking.uncompleted_goals[0])
                self.make_plan()
            self.action = self.steps.pop(0).lower()
            return self.action
        if len(self.steps) == 0 and len(options)!= 0:
            self.make_plan()
            if len(self.steps) == 0:
                return random.choice(options)
            else:
                return self.steps.pop(0).lower()
        #self.save_Q_table_to_file()
        return None

    def make_plan(self):
        log = open("myprog.log", "w")
        stdout = sys.stdout
        sys.stdout = log
        self.steps = planner.make_plan(self.deterministic_domain,"problem.pddl")
        log.close()
        sys.stdout = stdout

    def apply_revealable_predicates(self, state):
        for revealable_predicate in self.services.parser.revealable_predicates:
            for (predicate_name, entry) in revealable_predicate.effects:
                state[predicate_name].add(entry)
        return state

    def save_Q_table_to_file(self):
        a_file = open(self.policy, "w")
        json.dump(self.data, a_file,encoding="ascii")
        a_file.close()
        a_file = open('vvvv', "w")
        json.dump(self.data_list, a_file)
        a_file.close()


    def local(self,domain_path, problem_path, out_path='tmp.ipc'):
        planner_path = "\"" + \
                       os.path.join(
                           os.path.dirname(sys.modules[__name__].__file__), 'external/siw-then-bfsf') + "\""


        os.system(planner_path + ' --domain ' + domain_path +
                  ' --problem ' + problem_path + ' --output ' + out_path)
        with open(out_path) as f:
            return [line for line in f.read().split('\n') if line.rstrip()]

