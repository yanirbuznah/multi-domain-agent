import cPickle
import os
import random
import sys
from timeit import default_timer as timer

import pddlsim.planner as planner
from pddlsim.local_simulator import LocalSimulator

from Executors.Executors_helpers.Observer import Observer
from Executors.Executors_helpers.goals_parser_helpers import get_goal_index_in_list
from Executors_helpers.hasing_states import *
from executor import Executor
from plan_to_model_executor import PlanToModelExecutor


class LearningFromPlanExecutor(Executor, Observer):
    def __init__(self, deterministic_domain, policy_file):
        super(LearningFromPlanExecutor, self).__init__()
        self.policy_file = os.path.join(os.getcwd(), os.path.join("policy_files"), policy_file)
        self.last_state = "dum_state"
        self.last_action = "dum_action"
        self.steps = []
        self.data = {'count': 0}
        self.data_list = []
        self.deterministic_domain = deterministic_domain

    def initialize(self, services):
        self.num_of_steps = len(self.steps)
        self.services = services
        self.initialize_Q_table()
        self.solve_deterministic_and_update_model()


    def solve_deterministic_and_update_model(self):
        state = self.apply_revealable_predicates(self.services.perception.get_state())
        steps = self.steps
        self.services.parser.generate_problem("problem.pddl", state, self.services.goal_tracking.uncompleted_goals[0])
        self.make_plan()
        planning_observable = PlanToModelExecutor(steps, self.model)
        planning_observable.subscribe(self)
        LocalSimulator(print_actions=False, hide_fails=True).run(self.deterministic_domain, 'problem.pddl',
                                                                 planning_observable)

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            self.save_Q_table_to_file()
            return None
        options = self.services.valid_actions.get()
        if len(self.steps) > 0:
            if self.steps[0].lower() not in options:
                self.solve_deterministic_and_update_model()
            self.action = self.steps.pop(0).lower()
            return self.action
        if len(self.steps) == 0 and len(options) != 0:
            self.solve_deterministic_and_update_model()
            if len(self.steps) == 0:
                return random.choice(options)
            else:
                return self.steps.pop(0).lower()

        return None

    def make_plan(self):
        log = open("myprog.log", "w")
        stdout = sys.stdout
        sys.stdout = log
        self.steps = planner.make_plan(self.deterministic_domain, "problem.pddl")
        log.close()
        sys.stdout = stdout

    def apply_revealable_predicates(self, state):
        for revealable_predicate in self.services.parser.revealable_predicates:
            for (predicate_name, entry) in revealable_predicate.effects:
                state[predicate_name].add(entry)
        return state

    def save_Q_table_to_file(self):
        self.data['models'][self.model_index] = self.model
        a_file = open(self.policy_file, "w")
        start = timer()
        cPickle.dump(self.data, a_file)
        a_file.close()
        print "time to save file: ", timer() - start, "seconds"
        print "size of the file:", float(os.stat(self.policy_file).st_size) / 1048576, "MB"

    def initialize_Q_table(self):
        if os.path.exists(self.policy_file) and os.stat(self.policy_file).st_size != 0:
            self.first_learning = False
            with open(self.policy_file) as file:
                self.data = cPickle.load(file)
            self.data['count'] += 1
            self.model_index = get_goal_index_in_list(self.data['goals'], self.services.parser.goals[0])

        else:
            self.first_learning = True
            self.model = {self.last_state: {'r': 0, 'q': 0, 'actions': {self.last_action: {'tau': 1, 'r': 0, 'q': 0}},
                                            'visited': 1}}
            self.data = {'count': 0, 'finish_states': {}, 'goals': [], 'models': []}
            self.data['goals'] = [self.services.parser.goals[0]]
            self.model_index = 0
        try:
            self.model = self.data['models'][self.model_index]
        except:
            self.model = {self.last_state: {'r': 0, 'q': 0, 'actions': {self.last_action: {'tau': 1, 'r': 0, 'q': 0}},
                                            'visited': 1}}
            self.data['models'].append(self.model)

        self.data['start'] = make_hash_sha256(self.services.parser.initial_state)

    def notify(self, observable, args):
        self.model = args
