import cPickle
import json
import random
import sys

import numpy as np
from Executors.Executors_helpers.goals_parser_helpers import *
from pddlsim.parser_independent import *
from Executors.Executors_helpers.hasing_states import make_hash_sha256
from executor import Executor
from timeit import default_timer as timer
import os



class Learner(Executor):

    def __init__(self,policy_file):
        super(Learner,self).__init__()
        self.last_state = "dum_state"
        self.last_action = "dum_action"
        self.policy_file = os.path.join(os.getcwd(),os.path.join("policy_files"),policy_file)
        self.initialize_Q_table()
        self.count = 0
        self.gamma = 0.9
        self.learning_rate = 0.9
        self.epsilon = 0.9
        self.kappa = 0.001
        self.last_actions = [self.last_action]*10




    def initialize(self,services):
        self.services = services
        self.actions = {}
        self.num_of_actions = len(self.actions)

        self.data['start'] = make_hash_sha256(self.services.parser.initial_state)
        self.rmax = self.get_rmax(self.services.goal_tracking.uncompleted_goals[0])
        for i in self.services.valid_actions.provider.parser.actions:

            if isinstance(self.services.valid_actions.provider.parser.actions[i],ProbabilisticAction):
                self.actions[i] = [self.services.valid_actions.provider.parser.actions[i].prob_list,self.rmax,1.0]
            else:
                self.actions[i] = [[1],self.rmax,1.0]

        if self.data['count'] == 0:
            self.data['goals'] = [self.services.parser.goals[0]]
        else:
            if not check_if_goal_in_list(self.data['goals'],self.services.parser.goals[0]):
                self.data['goals'].append(self.services.parser.goals[0])



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
        return self.rmax - self.get_number_of_uncompleted_goals(goal,state) - 1

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



            self.model[hash_state] = {'r':1000, 'q':1000,'actions':{},'visited':1}
      #      self.data['finish_states'].add(state)
            self.data['finish_states'][hash_state] = state
            self.update_Q_table(self.last_state,self.last_action,hash_state,1000)
#            self.save_Q_table_to_file(finish = True, finial_state = hash_state)

            self.save_Q_table_to_file()
            return None
        if len(options) == 0:
            return None

        if self.count == 1:
            self.data['start'] = hash_state
        if self.count % 5000 == 0:
            self.save_Q_table_to_file()

        if hash_state not in self.model:
            reward = q_reward = self.get_reward(self.services.goal_tracking.uncompleted_goals[0],state)
            self.model[hash_state] = {'r':reward, 'q':q_reward, 'actions':{},'visited':1}
        else:
            q_reward = self.model[hash_state]['q']
            reward = self.model[hash_state]['r']
            self.model[hash_state]['visited']+=1

        self.update_Q_table(self.last_state,self.last_action,hash_state,reward)
        self.last_action = self.change_repeated_action(self.pick_best_option(options,hash_state,reward),options,hash_state)
    #self.last_action = self.change_repeated_action(self.pick_best_option(options,hash_state,reward),options,hash_state)
        self.last_last_state = self.last_state
        self.last_state = hash_state
        if self.count > 100:
            self.planning_step()
        return self.last_action

    def repeated_action(self,action):
        return self.last_actions.count(action)>2

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
        x =0
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
       # optimistic over uncertancy
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

    def pick_best_option(self,options,hash_state,reward,count = 0):
        if self.epsilon**self.model[hash_state]['visited'] < random.uniform(0,1) and len(self.model[hash_state]['actions']) > 0:
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
        #     if count < 10:
        #         return self.pick_best_option(options,hash_state,reward,count+1)
        #     else:
        #         option = self.pick_random_action(options)
        # try:
        #     self.update_policy(reward,probs_per_states['q'],action)
        #     #self.update_policy(reward,probs_per_states['r'],action)
        # except:
        #     x = 2
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


    def planning_step(self):
        for _ in range(5):
            action = ""
            while action == "":
                state1 = random.choice(list(self.model))
                if len(self.model[state1]['actions']) != 0:
                    action = random.choice(list(self.model[state1]['actions']))
            for state in self.model[state1]['actions'][action]:
                if state != 'r' and state != 'q' and state!= 'tau':
                    try:
                        r = self.model[state]['r'] + self.kappa * np.sqrt(self.model[state1]['actions'][action]['tau'])
                        self.update_Q_table(state1,action,state,r)
                    except:
                        pass

    #
    # def save_Q_table_to_file(self, finish = False,finial_state ):
    #     if finish:
    #         for q in self.model:
    #             if len(self.model[q]['actions']) == 0:
    #                 if q not in self.data['finish_states'].keys():
    #                     x=5
    #
    #
    #     self.data['model'] = self.model
    #     a_file = open(self.policy_file, "w")
    #     start = timer()
    #     cPickle.dump(self.data, a_file)
    #     a_file.close()
    #     print "time to save file: " ,timer() - start , "seconds"
    #     print "size of the file:" ,float(os.stat(self.policy_file).st_size)/1048576, "MB"

    def save_Q_table_to_file(self):
        self.data['model'] = self.model
        a_file = open(self.policy_file, "w")
        start = timer()
        cPickle.dump(self.data, a_file)
        a_file.close()
        print "time to save file: " ,timer() - start , "seconds"
        print "size of the file:" ,float(os.stat(self.policy_file).st_size)/1048576, "MB"



    def initialize_Q_table(self):
        if os.path.exists(self.policy_file) and os.stat(self.policy_file).st_size != 0:
            self.first_learning = False
            with open(self.policy_file) as file:
                self.data = cPickle.load(file)
                self.data['count']+=1
                self.model = self.data['model']

        else:
            self.first_learning = True
            self.data = {'count':0, 'finish_states':{},'goals':[]}
            self.model = {self.last_state:{'r':0,'q':0,'actions':{self.last_action:{'tau':1,'r':0,'q':0}},'visited':1}}


