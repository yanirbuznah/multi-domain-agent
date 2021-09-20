import cPickle
import json
import random
import sys

import numpy as np

from pddlsim.parser_independent import *
from Executors.Executors_helpers.hasing_states import make_hash_sha256
from executor import Executor
from Executors_helpers.customized_valid_actions import CustomizedValidActions
import os

from Executors.Executors_helpers.goals_parser_helpers import *

class Executive(Executor):

    def __init__(self,policy_file):
        super(Executive,self).__init__()
        self.last_state = "dum_state"
        self.last_action = "dum_action"
        self.policy_file = os.path.join(os.getcwd(),os.path.join("policy_files"),policy_file)

        self.count = 0
        self.gamma = 0.9
        self.learning_rate = 0.9
        self.epsilon = 0.9
        self.kappa = 0.001
        self.last_actions = [self.last_action]*10




    def initialize(self,services):
        self.services = services
        self.initialize_Q_table()
        self.actions = {}
        self.num_of_actions = len(self.actions)
        self.rmax = self.get_rmax(self.services.goal_tracking.uncompleted_goals[0])
        self.finish_states = self.data['finish_states']
        for state in list(self.finish_states.keys()):
            if self.get_number_of_uncompleted_goals(self.services.goal_tracking.uncompleted_goals[0], self.finish_states[state]) >0:
                del self.finish_states[state]
        self.cheese_moved = len(self.finish_states) == 0


        for i in self.services.valid_actions.provider.parser.actions:

            if isinstance(self.services.valid_actions.provider.parser.actions[i],ProbabilisticAction):
                self.actions[i] = [self.services.valid_actions.provider.parser.actions[i].prob_list,self.rmax,1.0]
            #  x = [i,self.services.valid_actions.provider.parser.actions[i].prob_list,self.rmax]
            else:
                self.actions[i] = [[1],self.rmax,1.0]
            # x = [i,[1],self.rmax]

    #      self.actions.append(x)



    def get_rmax(self,goal,r = 0.0):
        if isinstance(goal,Literal):
            return 1.0
        if isinstance(goal,Conjunction):
            for i in goal.parts:
                r += self.get_rmax(i)
        elif isinstance(goal,Disjunction):
            max = 0.0
            for i in goal.parts:
                x = self.get_rmax(i)
                if x > max:
                    max = x
            r += max
        return r


    def get_reward (self,goal,state):
        # -1 for every additional step
        return self.rmax - self.get_number_of_uncompleted_goals(goal,state)

    def get_number_of_uncompleted_goals(self,goal,state,r = 0):
        if isinstance(goal,Literal):
            if self.services.parser.test_condition(goal, state):
                return 0
            return 1
        if isinstance(goal,Conjunction):
            for i in goal.parts:
                r += self.get_number_of_uncompleted_goals(i,state)
        elif isinstance(goal,Disjunction):
            max = 0
            for i in goal.parts:
                x = self.get_number_of_uncompleted_goals(i,state)
                if x > max:
                    max = x
            r += max
        return r

    def update_tau(self):
        try:
            if 'tau' in self.model[self.last_state]['actions'][self.last_action]:
                self.model[self.last_state]['actions'][self.last_action]['tau']+=1
            else:
                self.model[self.last_state]['actions'][self.last_action]['tau'] = 1
        except:
            pass


    def next_action(self):
        self.count+=1
        state = self.services.perception.get_state()
        options = self.services.valid_actions.get()
        hash_state = make_hash_sha256(state)
        if self.services.goal_tracking.reached_all_goals():
            return None
        if len(options) == 0:
            return None

        if self.count == 1:
            self.data['start'] = hash_state

        if hash_state not in self.model:
            reward = q_reward = self.get_reward(self.services.goal_tracking.uncompleted_goals[0],state)
            self.model[hash_state] = {'r':reward, 'q':q_reward, 'actions':{},'visited':1}
        else:
            q_reward = self.model[hash_state]['q']
            reward = self.model[hash_state]['r']
            self.model[hash_state]['visited']+=1

        self.last_action = self.change_repeated_action(self.pick_best_option(options,hash_state,reward),options,hash_state)
        self.last_last_state = self.last_state
        self.last_state = hash_state
        return self.last_action

    def repeated_action(self,action):
        return self.last_actions.count(action) > 2

    def update_last_actions(self,action):
        self.last_actions.pop(0)
        self.last_actions.append(action)

    def change_repeated_action(self,g_action,options,hash_state):
        if self.repeated_action(g_action):
            g_action = self.pick_random_action(options)
        self.update_last_actions(g_action)
        if g_action not in self.model[hash_state]['actions']:
            action = self.get_action_from_grounded_action(g_action)
            probs =self.get_probs_from_option(action)
            probs_per_states = self.get_probabilistic_per_state(g_action,probs,{})
            self.model[hash_state]['actions'][g_action] = probs_per_states
        return g_action

    def semi_softmax(self,x):
        #return [1.0/len(x)]*len(x)
        min_x = min(x)
        normalize_x = [xi+2*abs(min_x) for xi in x ]
        sum_x = sum(normalize_x)
        if sum_x == 0:
            return [1.0/len(x)]*len(x)
        return [i/sum_x for i in normalize_x]

    def get_probs_from_option(self,action):
        return self.actions[action][0]

    def get_probabilistic_per_action(self,actions):
        lst = np.array([i[2] for i in self.actions])
        y = self.semi_softmax(lst)
        r = random.uniform(0, 1)
        x =0
        for i in range(self.num_of_actions):
            x+=y[i]
            if (x > r):
                return i

    def get_probabilistic_per_rewards(self,rewards):
        num_of_rewards = len(rewards)
        y = self.semi_softmax(rewards)
        r = random.uniform(0, 1)
        x = 0
        for i in range(num_of_rewards):
            x+=y[i]
            if (x > r):
                return i

    def check_effect(self,state,option):
        log = open("myprog.log", "w+")
        stdout = sys.stdout
        sys.stdout = log
        self.services.parser.apply_action_to_state(option, state, check_preconditions=False)
        self.services.parser.apply_revealable_predicates(state)
        log.seek(14)
        try:
            index = int(log.read(1))
            return index
        except:
            return None
        finally:
            log.close()
            sys.stdout = stdout
            del log


    def get_probabilistic_per_state(self,option,probs, states_and_probs):
        current_state = self.services.perception.get_state()
        self.services.parser.apply_revealable_predicates(current_state)
        if probs[0] == 1:
            state = self.services.parser.copy_state(current_state)
            self.services.parser.apply_action_to_state(option, state, check_preconditions=False)
            self.services.parser.apply_revealable_predicates(state)
            states_and_probs[make_hash_sha256(state)] = 1
            states_and_probs['r'] = states_and_probs['q'] = self.get_reward(self.services.goal_tracking.uncompleted_goals[0],state)
            return states_and_probs
        states_from_probs = [False] * len(probs)
        # optimistic over uncertainty
        reward_from_actions = [i * self.rmax for i in probs]
        for i in range(10):
            state = self.services.parser.copy_state(current_state)
            index = self.check_effect(state,option)
            if states_from_probs[index] == False:
                states_from_probs[index] = True
                reward_from_actions[index] = probs[index]* self.get_reward(self.services.goal_tracking.uncompleted_goals[0],state)
                hash_state = make_hash_sha256(state)
                if hash_state not in states_and_probs:
                    states_and_probs[hash_state] = probs[index]
                if all(states_from_probs):
                    break
        states_and_probs['r'] = states_and_probs['q'] = sum(reward_from_actions)

        return states_and_probs

    def pick_random_action_with_reward_calc(self,options):
        options_types_number = []
        last_option_name = options[0].split(" ")[0][1:]
        rewards = [self.actions[last_option_name][1]]
        for i in range(len(options)):
            if options[i][1:len(last_option_name)+1] != last_option_name:
                options_types_number.append(i-1)
                last_option_name = options[i].split(" ")[0][1:]
                rewards.append(self.actions[last_option_name][1])

        options_types_number.append(len(options)-1)
        index = self.get_probabilistic_per_rewards(rewards)
        if index == 0:
            return options[random.randint(0,options_types_number[0])]
        return options[random.randint(options_types_number[index-1]+1,options_types_number[index])]


    # normalize the types of actions probs and take one of them
    def pick_random_action(self,options):
        options_types_number = []
        last_option_name = options[0].split(" ")[0]
        for i in range(len(options)):
            if options[i][:len(last_option_name)] != last_option_name:
                options_types_number.append(i-1)
                last_option_name = options[i].split(" ")[0]
        options_types_number.append(len(options)-1)
        index = random.randint(0,len(options_types_number)-1)
        if index == 0:
            return options[random.randint(0,options_types_number[0])]
        return options[random.randint(options_types_number[index-1],options_types_number[index])]

    def get_index_of_action(self,option):
        for i in range(len(self.actions)):
            if self.actions[i][0] in option:
                return i

    def get_action_from_grounded_action(self,action):
        return action.split(" ")[0][1:]


    def look_ahed(self,state,k,t,valid_action):
        options = valid_action.get(state)
        r = self.get_reward(self.services.goal_tracking.uncompleted_goals[0],state)
        if k == 0 or len(options) == 0:
            return [r]
        hash_state = make_hash_sha256(state)
        if hash_state not in self.model:
            self.model[hash_state] = {'r':r, 'q':r, 'actions':{},'visited':1}

        state_rewards = []
        for i in range(t):
            option = self.pick_random_action_with_reward_calc(options)
            action = self.get_action_from_grounded_action(option)
            probs =self.get_probs_from_option(action)
            probs_per_states = self.get_probabilistic_per_state(option,probs,{})
            self.model[hash_state]['actions'][option] = probs_per_states
            tested_state = self.services.parser.copy_state(state)
            log = open("myprog.log", "w+")
            stdout = sys.stdout
            sys.stdout = log
            self.services.parser.apply_action_to_state(option,tested_state,check_preconditions=False)
            self.services.parser.apply_revealable_predicates(tested_state)
            log.close()
            sys.stdout = stdout
            del log
            state_rewards += self.look_ahed(tested_state,k-1,t,valid_action)
        self.model[hash_state]['v'] = sum(state_rewards)/t
        return state_rewards

    def pick_random_action_from_model(self,hash_state):
        actions = self.model[hash_state]['actions']
        return random.choice(actions.keys())



    def mc_control(self,hash_state,k,t):
        if hash_state not in self.model:
            self.model[hash_state] = {'r': 0, 'q': 0, 'actions': {}, 'visited': 1}
        if k == 0 or len(self.model[hash_state]['actions']) == 0:
            return [self.model[hash_state]['r']]
        state_rewards = []
        for i in range(t):
            option = self.pick_random_action_from_model(hash_state)
            state_rewards += self.mc_control(self.get_state_from_action(self.model[hash_state]['actions'][option]),k-1,t)
        self.model[hash_state]['v'] = sum(state_rewards)/(t*k)
        return state_rewards

    def get_state_from_action(self,action):
        state = ""
        prob_state = 0
        for a in action:
            if a != 'q' and a!= 'r':
                if action[a] > prob_state:
                    prob_state = action[a]
                    state = a
        return state

    def pick_best_option(self,options,hash_state,reward):

        if self.cheese_moved:
            x = self.look_ahed(self.services.perception.get_state(), 2, 5,
                               CustomizedValidActions(self.services.parser, self.services.perception))

        else:
            x = self.mc_control(hash_state,4,4)
            fd =2


        if len(self.model[hash_state]['actions']) > 0:
            max_option = self.get_best_action(hash_state)
            return max_option
        #option = self.pick_random_action(options)
        option = self.pick_random_action_with_reward_calc(options)
        action = self.get_action_from_grounded_action(option)
        probs =self.get_probs_from_option(action)


        # update model
        if option not in self.model[hash_state]['actions']:
            probs_per_states = self.get_probabilistic_per_state(option,probs,{})
            self.model[hash_state]['actions'][option] = probs_per_states
        if len(self.model[hash_state]['actions'][option]) < len(probs) + 2:
            probs_per_states = self.get_probabilistic_per_state(option,probs,self.model[hash_state]['actions'][option])
            self.model[hash_state]['actions'][option] = probs_per_states
        else:
            probs_per_states = self.model[hash_state]['actions'][option]
            self.update_policy(reward,probs_per_states['r'],action)
        return option

    def update_policy(self,prev_r,reward,action):
        # self.actions[action][1] = avg
        #  self.actions[action][2] = count
        self.actions[action][2]+=1
        self.actions[action][1] += ((reward-prev_r) - self.actions[action][1] )/ self.actions[action][2]


    def update_Q_table(self,last_state,last_action,state,reward):
        if last_state and last_action :
            if len(self.model[state]['actions']) == 0:
                max_option = 0
            else:
                max_option =self.get_best_reward(state)
            self.model[last_state]['actions'][last_action]['q'] += self.learning_rate * (reward + self.gamma * max_option - self.model[last_state]['actions'][last_action]['q'])
            q_actions = [self.model[last_state]['actions'][action]['q'] for action in self.model[last_state]['actions']]
            self.model[last_state]['q'] = sum(q_actions)/len(q_actions)


    def get_best_action(self,state):
        max_option_reward = 0
        max_action = None
        for i in self.model[state]['actions']:

            if self.model[state]['actions'][i]['q']> max_option_reward or max_action is None:
                max_option_reward = self.model[state]['actions'][i]['q']
                max_action = i
        return max_action

    def get_best_reward(self,state):
        max_option_reward = 0
        max_action = None
        for i in self.model[state]['actions']:

            if self.model[state]['actions'][i]['r']> max_option_reward or max_action is None:
                #max_option_reward = self.model[state]['q']
                max_option_reward = self.model[state]['actions'][i]['r']
                max_action = i
        return max_option_reward


    def initialize_Q_table(self):
            if os.path.exists(self.policy_file) and os.stat(self.policy_file).st_size != 0:
                self.first_learning = False
                with open(self.policy_file) as file:
                    self.data = cPickle.load(file)
                self.data['count'] += 1
                self.model_index = get_goal_index_from_correlation(self.data['goals'], self.services.parser.goals[0])

            else:
                self.first_learning = True
                self.model = {
                    self.last_state: {'r': 0, 'q': 0, 'actions': {self.last_action: {'tau': 1, 'r': 0, 'q': 0}},
                                      'visited': 1}}
                self.data = {'count': 0, 'finish_states': {}, 'goals': [], 'models': []}
                self.data['goals'] = [self.services.parser.goals[0]]
                self.model_index = 0
            try:
                self.model = self.data['models'][self.model_index]
            except:
                self.model = {
                    self.last_state: {'r': 0, 'q': 0, 'actions': {self.last_action: {'tau': 1, 'r': 0, 'q': 0}},
                                      'visited': 1}}
                self.data['models'].append(self.model)

            self.data['start'] = make_hash_sha256(self.services.parser.initial_state)



