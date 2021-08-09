import random

from Executors_helpers.bfs import bfs, get_min_path
from  executor import Executor

class BehaviorBaseExecutor(Executor):

    def __init__(self):
        super(BehaviorBaseExecutor, self).__init__()
        self.sp_graph = {}
        self.graph = {}
        self.find_ball = False


    def initialize(self, services):
        self.services = services
        self.number_of_objects = len(self.services.parser.objects)
        self.generate_graph(self.services.parser.domain_name)
        # find the interesting balls and  init the state (False = not in goal)
        # goals = self.get_goals(self.services.goal_tracking.uncompleted_goals[0])
        goals = self.get_goals(self.services.goal_tracking.uncompleted_goals[0])

        if self.services.parser.domain_name == 'simple-football':
            start_point = list(self.services.parser.initial_state['at-robby'])[0][0]
            self.current_goals = self.check_best_goals_football(goals, start_point)
            self.interesting_balls = map(lambda b: (b.args, self.find_shortest_path(b.args[1])), self.current_goals)
            self.find_closest_ball()
        else:
            persons = list(self.services.parser.initial_state['at'])
            self.current_goals = self.check_best_goals_maze(goals, persons)
            self.sp_graph = self.find_shortest_path(self.current_goals[0].args[1])
            self.current_person = self.current_goals[0].args

        self.uncompleted_goals = len(self.current_goals)

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            return None
        options = self.services.valid_actions.get()
        if len(options) == 0:
            return None
        return self.pick_best_option(options, self.services.parser.domain_name)

    def get_goals(self, parent_goal):
        goals = []
        if type(parent_goal).__name__ == "Conjunction":
            for goal in parent_goal.parts:
                if type(goal).__name__ == "Disjunction":
                    if len(goals) == 0:
                        for sub_goal in goal.parts:
                            goals.append([sub_goal])
                    else:
                        first_goals = goals[:]
                        goals = []
                        for this_goal in first_goals:
                            for sub_goal in goal.parts:
                                temp_goal = this_goal[:]
                                temp_goal.append(sub_goal)
                                goals.append(temp_goal)

                elif type(goal).__name__ == "Literal":
                    if len(goals) == 0:
                        goals.append([goal])
                    else:
                        first_goals = goals[:]
                        goals = []
                        for this_goal in first_goals:
                            temp_goal = this_goal[:]
                            temp_goal.append(goal)
                            goals.append(temp_goal)
                else:
                    if len(goals) == 0:

                        goals.append(goal.parts[:])
                    else:
                        for this_goal in goals:
                            this_goal += goal.parts


        elif type(parent_goal).__name__ == "Disjunction":
            for goal in parent_goal.parts:
                if type(goal).__name__ == "Conjunction":
                    new_goal = []
                    for sub_goal in goal.parts:
                        new_goal.append(sub_goal)
                    goals.append(new_goal)
                elif type(goal).__name__ == "Literal":
                    goals.append([goal])
                else:
                    for sub_goal in goal.parts:
                        goals.append([sub_goal])
        return goals

    def check_validation(self, goal):
        zip_objects = [(i.args[0],i.args[1]) for i in goal]
        objects,goal_locations = zip(*zip_objects)
        # check the number of goals and number of unique objects in goals, if there is less objects then galls ->
        # the goal can not be met

        if len(set(objects)) == len(goal):
            return True
        else:
            # index function return the first occurrence, if the current goal different from the first occurrence goal->
            # the goal can not be met
            for i in range(len(objects)):
                if objects.count(objects[i]) > 1:
                    if goal_locations[i] != goal_locations[objects.index(objects[i])]:
                        return False
        return True

    def remove_duplicated_goals(self,goal):
        objects = [(i.args[0]) for i in goal]

        for object in objects:
            i = objects.index(object)
            if objects.count(object) > 1:
                goal.pop(i)
                objects.pop(i)
        return goal


    def check_best_goals_football(self, goals, start):
        min_weight = float('inf')
        min_goal = goals[0]
        pred, dist = bfs(start, self.graph)
        for goal in goals:
            weight = 0
            if self.check_validation(goal):
                for sub_goal in goal:
                    weight += dist[sub_goal.args[1]]
                if min_weight > weight:
                    min_weight = weight
                    min_goal = goal
        min_goal = self.remove_duplicated_goals(min_goal)
        return min_goal

    def check_best_goals_maze(self, goals, persons):
        min_weight = float('inf')
        min_goal = goals[0]
        for goal in goals:
            weight = 0
            if self.check_validation(goal):
                for person in persons:
                    if person[0] in [g.args[0] for g in goal]:
                        start = person[1]
                        pred, dist = bfs(start, self.graph)
                        for sub_goal in goal:
                            weight += dist[sub_goal.args[1]]
                        if min_weight > weight:
                            min_weight = weight
                            min_goal = goal

        return min_goal

    def generate_graph(self, domain_name):
        if domain_name == 'maze':
            self.maze_generate_graph()
        else:
            self.football_generate_graph()

    def pick_best_option(self, options, domain_name):
        if domain_name == "maze":
            return self.maze_best_option(options)
        return self.football_best_option(options)

    def football_best_option(self, options):
        for ball in self.services.perception.state['at-ball']:
            for interesting_ball in self.interesting_balls:
                if ball[0] == interesting_ball[0][0] and ball[1] == interesting_ball[0][1]:
                    self.interesting_balls.remove(interesting_ball)
                    self.find_ball = False
                    self.find_closest_ball()
                    return self.football_best_option(options)

        valid_actions = []
        for s_move in options:
            move = s_move[1:-1].split()
            if move[0] == 'kick':
                valid_actions.append(
                    {'name': move[0], 'ball': move[1], 'from': move[2], 'to': move[3], 'error': move[4]})
                if not self.find_ball:
                    interesting_balls_names = [i[0][0] for i in self.interesting_balls]
                    if move[1] in interesting_balls_names:
                        self.find_ball = True
                        self.sp_graph = self.find_shortest_path(self.interesting_balls[interesting_balls_names.index(move[1])][0][1])
            else:
                valid_actions.append({'name': move[0], 'from': move[1], 'to': move[2]})

        weights = []
        for action in valid_actions:
            path = self.sp_graph[action['to']]
            error_path = None
            for i in self.interesting_balls:
                if action['name'] == 'kick' and i[0][0] == action['ball']:
                    path = i[1][action['to']]
                    error_path = i[1][action['error']]


            # check the exceptions and threat them as necessary
            if len(path) == 0 or (error_path is None and action['name'] == 'kick') \
                    or (error_path is not None and len(error_path) == 0):
                weight = 0

            else:
                weight = (self.number_of_balls_in_path(path)) * (1.0 / len(path))
                if action['name'] == 'kick':
                    error_weight = (self.number_of_balls_in_path(error_path)) * (0.2 / len(error_path))
                    weight += error_weight
                    weight *= self.number_of_objects
                    if action['ball'] not in [i[0][0] for i in self.interesting_balls]:
                        weight = 0
            weights.append(weight)

        return options[weights.index(max(weights))]

    def maze_best_option(self, options):
        persons = {i[0]: i[1] for i in self.services.perception.state['at']}
        for goal in self.current_goals:
            if (goal.args[0] in persons):
                if goal.args[1] == persons[goal.args[0]]:
                    self.current_goals.remove(goal)
                    self.current_person = random.choice(self.current_goals).args
                    self.sp_graph = self.find_shortest_path(self.current_person[1])

        valid_moves = []
        i = 0
        for s_move in options:
            move = s_move[1:-1].split()
            if move[1] == self.current_person[0]:
                prob = float(self.services.parser.actions[move[0]].prob_list[0])
            else:
                prob = 0
            valid_moves.append({'person': move[1], 'from': move[2], 'to': move[3], 'prob': prob})
            i += 1
        weights = []
        for move in valid_moves:
            path = self.sp_graph[move['to']]
            if len(path) == 0 or move['from'] in path:
                weight = 0
            else:
                weight =(move['prob']/len(path))
            weights.append(weight)
        return options[weights.index(max(weights))]

    def maze_generate_graph(self):
        states = ['west', 'south', 'north', 'east']
        for v in self.services.parser.objects:
            if v not in map(lambda b: b[0], self.services.parser.initial_state['person']):
                self.graph[v] = []
        for initial_states_name in self.services.parser.initial_state:
            if initial_states_name in states:
                state = self.services.parser.initial_state[initial_states_name]
                if len(state) != 0:
                    for e in state:
                        self.graph[e[0]].append(e[1])

    def find_shortest_path(self, dest):
        sp_graph = {}
        for v in self.graph:
            pred, dist = bfs(v, self.graph)
            sp_graph[v] = get_min_path(pred, dest)
            if v != dest and len(sp_graph[v]) == 1:
                sp_graph[v] = []
        return sp_graph

    def football_generate_graph(self):
        for v in self.services.parser.objects:
            if v not in map(lambda b: b[0], self.services.parser.initial_state['ball']):
                self.graph[v] = []

        for e in self.services.parser.initial_state['connected']:
            self.graph[e[0]].append(e[1])

    def number_of_balls_in_path(self, path):
        number_of_balls = 0
        for ball in map(lambda b: b, self.services.perception.state['at-ball']):
            for interesting_ball in self.interesting_balls:
                if ball[0] == interesting_ball[0][0]:
                    robby_location = list(self.services.perception.state['at-robby'])[0][0]
                    if ball[1] in path or ball[1] == robby_location:
                        number_of_balls += 1
        return number_of_balls

    def find_closest_ball(self):
        closest_place = None
        closest_distance = float('inf')
        pred, dist = bfs(list(self.services.perception.state['at-robby'])[0][0], self.graph)
        # find the interesting balls and  init the state (False = not in goal)

        for place in map(lambda b: b, self.services.perception.state['at-ball']):

            if place[0] in [i[0][0] for i in self.interesting_balls]:
                if dist[place[1]] < closest_distance:
                    closest_distance = dist[place[1]]
                    closest_place = place[1]
        self.sp_graph = self.find_shortest_path(closest_place)

