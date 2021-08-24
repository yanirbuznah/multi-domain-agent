import json

import numpy as np
from executor import Executor
from Executors_helpers.config_file import *
import os

class RLExecutor(Executor):

    def __init__(self, flag, policy_file):
        super(RLExecutor, self).__init__()
        self.policy_file = os.path.join(os.getcwd(),os.path.join("policy_files"),policy_file)
        self.visited ={}
        self.learning_rate = LEARNING_RATE
        self.gamma = GAMMA
        self.epsilon_greedy = EPSILON_GREEDY
        self.initialize_Q_table()
        self.last_option= ""
        if flag == "-L":
            self.learning = True
        elif flag == "-E":
            self.learning = False



    def initialize(self, services):
        self.services = services
        for block in self.services.parser.initial_state['empty']:
            if self.first_learning:
                self.data[block[0]] = {}
            self.visited[block[0]] = 0.9
            self.data['cheese'] = []
        if self.learning and self.data['count'] >= len(self.data)/5:
            exit(128)
        if K_EPSILON < 0:
            self.k_epslion = 1-(1/(float(len(self.data))))
        else:
            self.k_epslion = K_EPSILON


    def next_action(self):
        options = self.services.valid_actions.get()

        for state in self.services.perception.state['at']:
            self.location = state[1]
            self.update_Q_table(options)
            break
        if self.services.goal_tracking.reached_all_goals():
            if self.learning:
                self.save_Q_table_to_file(self.location)
            return None

        if len(options) == 0:
            return None

        self.last_tile = self.location
        option = self.pick_best_option(options)
        self.last_option = option

        return option

    def get_reward(self, options):
        directions = [0,0,0,0]
        for action in options:
            if "pick-food" in action:
                return 10000
            if 'north' in action:
                directions[0] +=1
            if 'south' in action:
                directions[1] += 1
            if 'east' in action:
                directions[2] += 1
            if 'west' in action:
                directions[3] +=1

        filtered_directions = filter(lambda x: x>0,directions)
        if len(filtered_directions) == 1:
            return -50
        return -1


    def pick_best_option(self, options):
        if not self.data[self.location]:
            self.data[self.location] = [dict([i,0] for i in options),1]
            return self.get_random_option(options)
        if self.learning:
            if PERSONAL_EPSILON:
                if np.random.uniform()<self.data[self.location][1]:
                    self.data[self.location][1]*=self.k_epslion
                    return self.get_random_option(options)
            else:
                if np.random.uniform() < self.epsilon_greedy:
                    self.epsilon_greedy*=self.k_epslion
                    return self.get_random_option(options)
        max_wight = 0
        max_option = None
        for option in self.data[self.location][0]:
            x = self.data[self.location][0][option]
            if x >= max_wight or max_option is None:
                max_wight = x
                max_option = option
        return max_option


    def get_random_option(self, options):
        i = np.random.randint(0, len(options))
        return options[i]


    def update_Q_table(self,options):
        if self.last_option:
            if len(self.data[self.location]) == 0:
                max_option = 0
            else:
                max_option = max([self.data[self.location][0][i] for i in self.data[self.location][0]])
            self.data[self.last_tile][0][self.last_option] += self.learning_rate * \
                                                              (self.get_reward(options)+ self.gamma*max_option - self.data[self.last_tile][0][self.last_option])


    def save_Q_table_to_file(self,current_tile):
        self.data['cheese'] = current_tile
        a_file = open(self.policy_file, "w")
        json.dump(self.data, a_file)
        a_file.close()


    def initialize_Q_table(self):

        if os.path.exists(self.policy_file) and os.stat(self.policy_file).st_size != 0:
            self.first_learning = False
            with open(self.policy_file) as json_file:
                self.data = json.load(json_file)
                self.data['count']+=1
        else:
            self.first_learning = True
            self.data = {'count':0}

