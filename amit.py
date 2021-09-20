# Amit Sharabi 323784298
import json
import os
import random
import sys
import time

from pddlsim.executors.executor import Executor
from pddlsim.local_simulator import LocalSimulator
from pddlsim.parser_independent import ProbabilisticAction

# read arguments
flag = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]

is_failed = False
start_time = time.time()
it = 0
hidden_exist = False
reach_hidden = False

algorithms = ["--search \"astar(lmcut())\"", "--search \"astar(ipdb())\"", "--search \"astar(blind())\"",
              "--evaluator \"hff=ff()\" --evaluator \"hcea=cea()\" --search \"lazy_greedy([hff, hcea], preferred=[hff, hcea])\"",
              "--evaluator \"hff=ff()\" --search \"lazy_greedy([hff], preferred=[hff])\"",
              "--evaluator \"hcea=cea()\" --search \"lazy_greedy([hcea], preferred=[hcea])\""]

random.shuffle(algorithms)


def decode_dict_vals(dict):
    if dict is None:
        return
    new_dict = {}
    for key in dict.keys():
        value = []
        temp = []
        for item in dict[key]:
            if not isinstance(item, list):
                value.append(str(item))
            else:
                temp = []
                for x in item:
                    temp.append(str(x))
                value.append(temp)
        new_dict[str(key)] = value
    return new_dict


def create_string_from_tuple(data):
    if isinstance(data[0], tuple):
        left = create_string_from_tuple(data[0])
    else:
        left = str(data[0])
    if len(data) == 1:
        return left
    if isinstance(data[1], tuple):
        right = create_string_from_tuple(data[1])
    else:
        right = str(data[1])
    return left + " " + right


class LearningExecutor(Executor):
    def __init__(self):
        super(LearningExecutor, self).__init__()
        self.expected_state = None
        self.plan = []
        self.path = []
        self.domain_plans = {}  # {problem name: [path, best_alg, [algorithm1, algorithm2,..] ], ...}
        self.algorithm = ""
        self.last_state = None
        self.last_action = None

    def initialize(self, services):
        self.services = services
        self.create_plans()
        self.run_planner(False)

    def reveal_predicates(self):
        preds = ""
        for cond in self.services.parser.revealable_predicates:
            preds += "(" + cond.condition.predicate + " "
            preds += create_string_from_tuple(cond.condition.args) + ") "
        return preds

    def add_reveal(self, lines):
        global hidden_exist
        i = 0
        for line in lines:
            if "(:reveal" in line:
                hidden_exist = True
                for j in range(i, len(lines)):
                    if "(:goal" not in lines[j]:
                        lines[j] = ""
                    else:
                        break
                break
            i += 1
        if i == len(lines):
            return lines
        after = False
        for k in range(j, len(lines)):
            if "(and " in lines[k]:
                after = True
                index = lines[k].find("(and ")
                new_goal = lines[k][:index + 5]
                new_goal += self.reveal_predicates()
                new_goal += ")"
                lines[k] = new_goal[:]
            else:
                if after:
                    lines[k] = ""
        lines[len(lines) - 1] = "))"
        return lines

    # CONVERTING THE FILE CONTENT TO DICTIONARY AND INITIALIZE THE TABLE IF NEEDED
    def create_plans(self):
        global algorithms
        global flag
        path = os.getcwd() + "/" + self.services.parser.domain_name
        if os.path.exists(path):
            f = open(self.services.parser.domain_name)
            if os.stat(self.services.parser.domain_name).st_size != 0:
                self.domain_plans = json.load(f)
                self.domain_plans = decode_dict_vals(self.domain_plans)
            f.close()
            if self.services.parser.problem_name in self.domain_plans:
                if flag == '-L':
                    algs = self.domain_plans[self.services.parser.problem_name][3]
                    for alg in algorithms:
                        if alg not in algs:
                            self.algorithm = alg
                            break
                    if self.algorithm == "":
                        self.algorithm = self.domain_plans[self.services.parser.problem_name][1]
                elif flag == '-E':
                    self.algorithm = self.domain_plans[self.services.parser.problem_name][1]
                    self.plan = self.domain_plans[self.services.parser.problem_name][0]
            else:
                self.algorithm = random.choice(algorithms)
        else:
            self.algorithm = random.choice(algorithms)

    def get_effect_string_from_action(self, action):
        global is_failed
        st = "(and "
        max_prob = -1
        max_index = 0
        i = 0
        if not is_failed:
            for prob in self.services.parser.actions[action].prob_list:
                if prob > max_prob:
                    if self.services.parser.actions[action].addlists[i] != [] and \
                            self.services.parser.actions[action].dellists[i] != []:
                        max_prob = prob
                        max_index = i
                i += 1
        else:
            max_index = random.randint(0, len(self.services.parser.actions[action].prob_list) - 1)
            while self.services.parser.actions[action].addlists[max_index] == [] or \
                    self.services.parser.actions[action].dellists[max_index] == []:
                max_index = random.randint(0, len(self.services.parser.actions[action].prob_list) - 1)
        for item in self.services.parser.actions[action].addlists[max_index]:
            st += "(" + create_string_from_tuple(item) + ") "
        st += "(not "
        for item in self.services.parser.actions[action].dellists[max_index]:
            st += "(" + create_string_from_tuple(item) + ")"
        st += "))\n"
        return st

    def change_action(self, action, lines):
        flag = False
        i = 0
        for line in lines:
            if "(:action " + action in line:
                flag = True
                i += 1
                continue
            if flag:
                if "probabilistic" in line:
                    stack = []
                    for j in range(i, len(lines)):
                        for c in lines[j]:
                            if c == '(':
                                stack.append(c)
                            elif c == ')':
                                stack.pop()
                        if len(stack) != 0:
                            lines[j] = ""
                        else:
                            lines[j] = self.get_effect_string_from_action(action)
                            break
                    break
            i += 1
        return lines

    @staticmethod
    def get_initial_state_string(state):
        initial_string = "(:init\n"
        for pred in state:
            if pred != "=":
                for tup in state[pred]:
                    initial_string += "\t(" + pred + " " + create_string_from_tuple(tup) + ")\n"
        initial_string += ")\n"
        return initial_string

    def change_initial_state(self, lines):
        i = 0
        for line in lines:
            if "init" in line:
                new_state = self.get_initial_state_string(self.services.perception.state)
                lines[i] = new_state[:]
                for j in range(i + 1, len(lines)):
                    if "(:goal" not in lines[j]:
                        lines[j] = ""
                    else:
                        break
                break
            i += 1
        return lines

    # THE FUNCTION PARSE AND CREATE THE PDDL FILES IN THE CORRECT LOCATION
    def create_files(self, replan):
        global reach_hidden
        complete_path = os.getcwd() + '/problems/'  # + "/downward/domains_and_problems/"
        if os.path.exists(complete_path + domain_path):
            os.remove(complete_path + domain_path)
        temp_domain = open(complete_path + domain_path, "w")
        domain_file = open(domain_path)
        domain = domain_file.readlines()
        domain_file.close()

        for action in self.services.parser.actions:
            if isinstance(self.services.parser.actions[action], ProbabilisticAction):
                domain = self.change_action(action, domain)

        domain = list(filter(("").__ne__, domain))

        temp_domain.writelines(domain)
        temp_domain.close()

        if os.path.exists(complete_path + problem_path):
            os.remove(complete_path + problem_path)
        temp_problem = open(complete_path + problem_path, "w")
        problem_file = open(problem_path)
        problem = problem_file.readlines()
        problem_file.close()

        if not reach_hidden:
            problem = self.add_reveal(problem)

        if replan:
            problem = self.change_initial_state(problem)
        problem = list(filter(("").__ne__, problem))
        temp_problem.writelines(problem)
        temp_problem.close()

    def run_planner(self, replan):
        global flag
        if self.plan:
            return
        self.create_files(replan)

        os.system(
            "./downward/fast-downward.py " + "downward/domains_and_problems/" + domain_path + " downward/domains_and_problems/" + problem_path + " " + self.algorithm + " > downward/output.txt")
        self.get_actions_from_planner()

    def get_actions_from_planner(self):
        global is_failed
        global algorithms
        output_file = open("downward/output.txt")
        output = output_file.readlines()
        output_file.close()

        exit_code = 0
        for i in range(len(output)):
            if "exit code:" in output[i]:
                temp = int(output[i].split("exit code: ")[1])
                if temp != 0:
                    exit_code = temp

        if exit_code != 0:
            is_failed = True
            return

        for i in range(len(output)):
            if "Actual search time:" in output[i]:
                output = output[i + 1:]
                break

        for i in range(len(output)):
            if "t=" in output[i]:
                output = output[:i]
                break

        for line in output:
            self.plan.append(line.split(" (1)")[0])

    def is_reveal_in_state(self):
        reveal = self.reveal_predicates()
        reveal = reveal.strip("() ").split(" ")
        pred_name = reveal[0]
        if len(reveal) == 2:
            pred = (reveal[1],)
        else:
            pred = (reveal[1], reveal[2])
        for tup in self.services.perception.state[pred_name]:
            if tup == pred:
                return True
        return False

    def next_action(self):
        global start_time
        global it
        global algorithms
        global hidden_exist
        global reach_hidden
        if self.services.goal_tracking.reached_all_goals():
            return None

        current_state = self.services.perception.state
        options = self.services.valid_actions.get()

        if hidden_exist:
            if self.is_reveal_in_state():
                reach_hidden = True
                self.run_planner(True)

        if not self.plan:
            if time.time() >= start_time + 5 * 60:
                if it <= 500:
                    it += 1
                    if len(options) == 0:
                        return None
                    return random.choice(options)
                self.algorithm = random.choice(algorithms)
        if current_state == self.last_state:
            self.path.append(self.last_action)
            return self.last_action

        if len(options) == 0:
            return None
        best_action = self.pick_best_option(options)
        self.expected_state = self.services.parser.copy_state(current_state)
        self.services.parser.apply_action_to_state(best_action, self.expected_state, check_preconditions=False)
        self.path.append(best_action)
        self.last_action = best_action
        self.last_state = current_state
        return best_action

    def pick_best_option(self, options):
        for action in self.plan:
            action_n = action.strip("()")
            for option in options:
                if "(" + action_n + ")" == option:
                    i = self.plan.index(action)
                    self.plan = self.plan[i + 1:]
                    return option
        self.plan = []
        self.run_planner(True)
        if not self.plan:
            return random.choice(options)
        return "(" + self.plan.pop(0) + ")"


agent = LearningExecutor()
# RUN THE AGENT
x = LocalSimulator().run(domain_path, problem_path, agent)

# UPDATE PATH TO GOAL FOR THIS PROBLEM
problem_name = agent.services.parser.problem_name
if problem_name not in agent.domain_plans:
    agent.domain_plans[problem_name] = [agent.path, agent.algorithm, float(x.total_time), [agent.algorithm]]
else:
    if len(agent.path) < len(agent.domain_plans[problem_name][0]) or (float(x.total_time) < float(
            agent.domain_plans[problem_name][2]) and len(agent.path) == len(agent.domain_plans[problem_name][0])):
        agent.domain_plans[problem_name][3].append(agent.algorithm)
        agent.domain_plans[problem_name][0] = agent.path
        agent.domain_plans[problem_name][1] = agent.algorithm
        agent.domain_plans[problem_name][2] = x.total_time
    else:
        if agent.algorithm not in agent.domain_plans[problem_name][3]:
            agent.domain_plans[problem_name][3].append(agent.algorithm)
# SAVE CURRENT PATH TO GOAL IN FILE
with open(agent.services.parser.domain_name, "w") as outfile:
    json.dump(agent.domain_plans, outfile)

# PRINT RESULT
print x
