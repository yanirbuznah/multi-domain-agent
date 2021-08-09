import random
from executor import Executor
from Executors_helpers.customized_valid_actions import CustomizedValidActions


class LookahedExecutor(Executor):

    def __init__(self, k):
        super(LookahedExecutor, self).__init__()
        self.k = k

    def initialize(self, services):
        self.services = services

    def pick_random_option(self, options):
        i = random.randint(0, len(options))
        return options[i]

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            return None
        options = self.services.valid_actions.get()
        if len(options) == 0:
            return None
        if len(options) == 1:
            return options[0]
        return self.pick_best_option(options)

    def pick_best_option(self, options):
        current_state = self.services.perception.get_state()
        best_option = self.get_random_option(options)
        state = self.services.parser.copy_state(current_state)
        min_distance = self.get_heuristic_distance(state, best_option)
        best_option_depth = self.k

        for option in options:
            state = self.services.parser.copy_state(current_state)
            self.services.parser.apply_action_to_state(option, state, check_preconditions=False)
            if state != current_state:
                state = self.services.parser.copy_state(current_state)
                current_distance,depth = self.get_K_actions_distance(self.k, option, state)
                if min_distance > current_distance or (current_distance == min_distance and depth > best_option_depth):
                    min_distance = current_distance
                    best_option = option
                    best_option_depth = depth

        return best_option

    def get_heuristic_distance(self, state, action):
        distance = len(self.services.goal_tracking.uncompleted_goals)

        for goal in self.services.goal_tracking.uncompleted_goals:
            if self.services.parser.test_condition(goal, state):
                distance -= 1
                continue
            tested_state = self.services.parser.copy_state(state)
            self.services.parser.apply_action_to_state(action, tested_state, check_preconditions=False)
            sub_goals_distance = len(goal.parts)
            for sub_goals in goal.parts:
                if self.services.parser.test_condition(sub_goals, tested_state):
                    sub_goals_distance -= 1
            distance += sub_goals_distance
        return distance

    def get_K_actions_distance(self, k_distance, action, state):
        tested_state = self.services.parser.copy_state(state)
        if k_distance == 1:
            return self.get_heuristic_distance(tested_state, action), k_distance
        valid_actions = CustomizedValidActions(self.services.parser, self.services.perception)
        actions = valid_actions.get(tested_state)
        if len(actions) == 0:
            return self.get_heuristic_distance(tested_state, action), k_distance
        min_distance = self.get_heuristic_distance(tested_state, actions[0])
        min_depth = k_distance
        for valid_action in valid_actions.get(tested_state):
            tested_state = self.services.parser.copy_state(state)
            distance, depth = self.get_K_actions_distance(k_distance - 1, valid_action, tested_state)
            if distance == self.get_heuristic_distance(tested_state,valid_action):
                depth = k_distance
            if distance < min_distance or (distance == min_distance and min_depth < depth):
                min_distance = distance
                min_depth = depth

        return min_distance, min_depth

    def get_random_option(self, options):
        i = random.randint(0, len(options) - 1)
        return options[i]

