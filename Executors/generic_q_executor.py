import base64
import hashlib
import json
import pickle

import numpy as np
from executor import Executor
from Executors_helpers.config_file import *
from Executors_helpers.hasing_states import *
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
        if not self.first_learning and self.learning and self.data['count'] >= len(self.data)/5:
            exit(128)
        if K_EPSILON < 0:
            self.k_epslion = 1-(1/(float(len(self.data))))
        else:
            self.k_epslion = K_EPSILON


    def next_action(self):
        options = self.services.valid_actions.get()
        s = self.services.perception.get_state()
        current_state = make_hash_sha256(s)
        if self.learning:
            self.update_Q_table(options,current_state)
        if self.services.goal_tracking.reached_all_goals():
            if self.learning:
                self.data[self.last_state]['actions'][0][self.last_option] = 100000
                self.save_Q_table_to_file(current_state)
            return None

        if len(options) == 0:
            return None

        self.last_state = current_state
        option = self.pick_best_option(options)
        self.last_option = option

        return option

    def get_reward(self, options):
        # if self.data[]
        # directions = [0,0,0,0]
        # for action in options:
        #     if "pick-food" in action:
        #         return 10000
        #     if 'north' in action:
        #         directions[0] +=1
        #     if 'south' in action:
        #         directions[1] += 1
        #     if 'east' in action:
        #         directions[2] += 1
        #     if 'west' in action:
        #         directions[3] +=1
        #
        # filtered_directions = filter(lambda x: x>0,directions)
        # if len(filtered_directions) == 1:
        #     return -50
        return -1


    def pick_best_option(self, options):
      #  [{self.action:{'r':self.num_of_steps-len(self.steps),'s':""}},1]
        if self.last_state not in self.data:
            #self.data[self.last_state] = {'actions':[dict([i,0] for i in options),1]}
            option = self.get_random_option(options)
            self.data[self.last_state] = {'actions':[{option:{'r':0,'s':""}},1]}
            return option
            #return self.get_random_option(options)

        if self.learning:
            if PERSONAL_EPSILON:
                if np.random.uniform()<self.data[self.last_state]['actions'][1]:
                    self.data[self.last_state]['actions'][1]*=self.k_epslion
                    option = self.get_random_option(options)
                    if option not in self.data[self.last_state]['actions'][0]:
                        self.data[self.last_state]['actions'][0][option]['r'] = 0
                    return option
            else:
                if np.random.uniform() < self.epsilon_greedy:
                    self.epsilon_greedy*=self.k_epslion
                    option = self.get_random_option(options)
                    if option not in self.data[self.last_state]['actions'][0]:
                        self.data[self.last_state]['actions'][0][option]['r'] = 0
                    return option
        max_wight = 0
        max_option = self.get_random_option(options)
        for option in self.data[self.last_state]['actions'][0]:
            x = self.data[self.last_state]['actions'][0][option]
            if x['r'] > max_wight or max_option is None:
                max_wight = x['r']
                max_option = option
        if max_option not in self.data[self.last_state]['actions'][0]:
            self.data[self.last_state]['actions'][0][max_option]={'r':0,'s':''}
        return max_option


    def get_random_option(self, options):
        i = np.random.randint(0, len(options))
        return options[i]


    def update_Q_table(self,options,state):
        if self.last_option:
            if state in self.data:
                max_option = max([self.data[state]['actions'][0][i] for i in self.data[state]['actions'][0]['r']])
            else:
                max_option = 0

            x = self.data[self.last_state]['actions'][0][self.last_option]['r']
            y = self.learning_rate * (self.get_reward(options)+ self.gamma*max_option - x)
            self.data[self.last_state]['actions'][0][self.last_option]['r'] =x+ y


    def save_Q_table_to_file(self,current_state):
        self.data['final_state'] = current_state
        states = self.data.keys()
        for state in states:
            if state != 'final_state' and state != 'count':
                x= self.data[state]['actions'][0].keys()
                for action in x:
                    if action in self.data[state]['actions'][0] and self.data[state]['actions'][0][action] == -LEARNING_RATE:
                        del self.data[state]['actions'][0][action]
                if len(self.data[state]['actions'][0]) == 0:
                    del self.data[state]

        a_file = open(self.policy_file, "w")
        json.dump(self.data, a_file)
        a_file.close()


    def initialize_Q_table(self):

        if os.path.exists(self.policy_file) and os.stat(self.policy_file).st_size != 0:
            self.first_learning = False
            with open(self.policy_file) as json_file:
                data = json_file.read().decode("ascii")
                self.data = json.loads(data)
                #self.data = json.load(json_file,encoding="ascii")
                self.data['count']+=1
        else:
            self.first_learning = True
            self.data = {'count':0}

