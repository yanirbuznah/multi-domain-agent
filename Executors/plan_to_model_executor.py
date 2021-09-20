from pddlsim.parser_independent import *

from Executors.Executors_helpers.Observable import Observable
from Executors_helpers.hasing_states import *
from executor import Executor


class PlanToModelExecutor(Executor, Observable):
    def __init__(self, steps, model):
        super(PlanToModelExecutor, self).__init__()
        self.steps = steps
        self.model = model
        self.last_action = None
        self.last_state = None
        self._observers = []

    def initialize(self, services):
        self.services = services
        self.rmax = self.get_rmax(self.services.goal_tracking.uncompleted_goals[0])

    def next_action(self):
        state = self.services.perception.get_state()
        hash_state = make_hash_sha256(state)
        r = self.get_reward(self.services.goal_tracking.uncompleted_goals, state)
        q = 1000 / (len(self.steps) + 1)
        if hash_state in self.model:
            self.model[hash_state]['q'] = q
            self.model[hash_state]['visited'] += 1

        else:
            self.model[hash_state] = {'r': r, 'q': q, 'actions': {}, 'visited': 1}
        if self.last_state and self.last_action:
            self.model[self.last_state]['actions'][self.last_action] = {'q': q, 'r': r, hash_state: 1}
        self.last_state = hash_state
        if len(self.steps) > 0:
            self.last_action = self.steps.pop(0).lower()
            return self.last_action
        self.notify_observers(self.model)
        return None

    def get_reward(self, goal, state):
        try:
            return self.rmax - self.get_number_of_uncompleted_goals(goal[0], state) - 1
        except:
            return self.rmax

    def get_rmax(self, goal, r=0.0):
        if isinstance(goal, Literal):
            return 1.0
        if isinstance(goal, Conjunction):
            for i in goal.parts:
                r += self.get_rmax(i)
        elif isinstance(goal, Disjunction):
            max = 0.0
            for i in goal.parts:
                x = self.get_rmax(i)
                if x > max:
                    max = x
            r += max
        return r

    def get_number_of_uncompleted_goals(self, goal, state, r=0):
        if isinstance(goal, Literal):
            if self.services.parser.test_condition(goal, state):
                return 0
            return 1
        if isinstance(goal, Conjunction):
            for i in goal.parts:
                r += self.get_number_of_uncompleted_goals(i, state)
        elif isinstance(goal, Disjunction):
            max = 0
            for i in goal.parts:
                x = self.get_number_of_uncompleted_goals(i, state)
                if x > max:
                    max = x
            r += max
        return r
