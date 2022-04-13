import itertools
import copy
import random
from ExtractCSV import latex_to_table
from help_methods import *

mode_change_table = latex_to_table("TransitionLatexClean.csv")

class DecPOMDP:

    def __init__(self, mach_comm_acts, mach_move_acts,hum_comm_acts,hum_move_acts,scenarios,prob_dict,modes):
        self.machine_comm_actions = mach_comm_acts
        self.scenario_numbers = scenarios
        self.modes = modes
        self.human_actions = list(itertools.product(hum_move_acts, hum_comm_acts))
        self.machine_actions = list(itertools.product(mach_move_acts, mach_comm_acts))
        self.prob_dict = prob_dict
        #self.horizon = horizon
        #self.human_knowledge = init_state
        #self.machine_knowledge = init_state
        #self.human_obs = hum_obs
        #self.machine_obs = mach_obs


    def get_allowed_machine_actions(self,mode):
        sc = (mode == "speedcontrol")
        follow = (mode == "following")
        if sc | follow :
            allowed_mvmts = ["accel", "decel", "maintainspeed"]
        else:
            allowed_mvmts = ["none"]
        return list(itertools.product(allowed_mvmts,self.machine_comm_actions))

    def get_safety(self,scenario, safety, human_action, machine_action):
        anti_decel = ["accel", "maintainspeed"]
        anti_accel = ["decel"]
        if ~safety:
            return False
        else:
            if (scenario == 1) | (scenario == 2) | (scenario == 5):
                if (human_action == "decel"):
                    return True
                elif (machine_action == "decel") & ~(human_action in anti_decel):
                    return True
                else:
                    return False
            elif (scenario == 3) | (scenario == 7):
                if (human_action == "decel"):
                    return False
                elif (machine_action == "decel") & ~(human_action in anti_decel):
                    return False
                else:
                    return True
            elif (scenario == 4) | (scenario == 8):
                if human_action == "accel":
                    return True
                elif (machine_action == "accel") & ~(human_action in anti_accel):
                    return True
                else:
                    return False
            elif (scenario == 6):
                return False
            else:
                print("ERROR! Unrecognized scenario!")

    def get_next_scenario(self,start_scenario):
        #scenario_change_prob = self.prob_dict["scenario_change"]
        #scenario_change = random.choices([True, False], weights = (1-scenario_change_prob, scenario_change_prob), k=1)
        #change = scenario_change[0]
        change = False
        if change:
            other_scenarios = copy.copy(self.scenario_numbers)
            other_scenarios.remove(start_scenario)
            next_scenario = random.choices(other_scenarios, k=1)
            return next_scenario[0]
        else:
            return start_scenario

    def check_in_row(self,row, mode, human_action, machine_action):
        [start_mode, next_mode, machine_act, human_act] = row
        if mode in start_mode:
            if human_action == human_act | machine_action == machine_act:
                return [True, next_mode]
        return [False, []]

    def get_mode_change(self,trans_table, curr_mode, machine_action, human_action):
        for row in trans_table:
            #print(row)
            #print([curr_mode, machine_action, human_action])
            [test, next] = self.check_in_row(row, curr_mode, machine_action, human_action)
            #print(test)
            if test:
                return next[0]
        return curr_mode

    def get_next_mode(self, mode, hum_mvmt, mach_mvmt):
        new_mode = self.get_mode_change(mode_change_table, mode, hum_mvmt, mach_mvmt)
        #probabilistic mode changes
        p_error = self.prob_dict["error"]
        p_exit_hold = self.prob_dict["exit_hold"]
        '''
        if mode == "hold":
            decision = random.choices([True, False], weights = (p_exit_hold, 1-p_exit_hold), k=1)
            if decision[0]:
                possible_next_states = ["following", "speed_control"]
                next_state = random.choices(possible_next_states, k=1)
                new_mode = next_state[0]
        error_decision = random.choices([True, False], weights = (p_error, 1-p_error), k=1)
        if error_decision[0]:
            new_mode = "error"
        '''
        return new_mode

    def update_knowledge(self,next_state, human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        self.machine_knowledge = next_state
        if (mach_comm == "communicate") | (hum_comm == "pushbutton"):
            self.human_knowledge = next_state

    def transition(self,start_state, human_action, machine_action):
        [scenario, mode, safety] = start_state
        [mach_mvmt, mach_comm] = machine_action
        [hum_mvmt, hum_comm] = human_action
        new_scenario = self.get_next_scenario(scenario)
        new_mode = self.get_next_mode(mode, hum_mvmt, mach_mvmt)
        new_safety = self.get_safety(scenario, safety, hum_mvmt, mach_mvmt)
        next_state = [new_scenario, new_mode, new_safety]
        return next_state



    '''
    def get_observation(self,next_state,human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        [scenario, mode, safety] = next_state
        machine_obs = ""
        if (mach_comm == "communicate") | (hum_comm == "push_button"):
            human_obs = mode
        else:
            human_obs = "none"
        return [human_obs, machine_obs]
    '''

    def get_cost(self, new_state, human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        #next_state = self.transition(state,human_action,machine_action)
        [scenario, mode, safety] = new_state
        cost = 0
        # cost for human to move
        if hum_mvmt != "none":
            cost += self.costs["human movement"]
        # cost for unsafe state
        if ~safety:
            cost += self.costs["unsafe"]
        # cost of machine updating the interface
        if mach_comm == "communicate":
            cost += self.costs["machine communication"]
        return cost

    def find_obs_in_edges(self, obs, edges):
        index = 0
        for observation in edges:
            if obs == observation:
                return index
            index += 1
        print("OBS NOT FOUND IN EDGES! Edges: " + str(edges) + "Obs: " + str(obs))
        return -1

    def tree_value(self, init_state, human_tree, machine_tree):
        machine_action = machine_tree.get_root().get_action()
        human_action = human_tree.get_root().get_action()
        new_state = self.transition(init_state, human_action, machine_action)
        value = self.get_cost(new_state, human_action, machine_action)
        if human_tree.get_height() == 0:
            return value
        [human_obs, machine_obs] = self.get_observation(new_state,human_action,machine_action)
        edg_idx1 = self.find_obs_in_edges(human_obs, human_tree.root.get_edges())
        edg_idx2 = self.find_obs_in_edges(machine_obs, machine_tree.root.get_edges())
        tree1_ch = human_tree.root.get_children()
        tree2_ch = machine_tree.root.get_children()
        new_human_tree = tree1_ch[edg_idx1]
        new_machine_tree = tree2_ch[edg_idx2]
        return value + self.tree_value(new_state, new_human_tree, new_machine_tree)

class DecPOMDP_medium:
    def __init__(self, mach_comm_acts, mach_move_acts,hum_comm_acts,hum_move_acts,prob_dict,modes,scenario,cost_dict):
        self.machine_comm_actions = mach_comm_acts
        self.scenario_number = scenario
        self.modes = modes
        self.human_actions = list(itertools.product(hum_move_acts, hum_comm_acts))
        self.machine_actions = list(itertools.product(mach_move_acts, mach_comm_acts))
        self.prob_dict = prob_dict
        self.costs = cost_dict
        #self.horizon = horizon
        #self.human_knowledge = init_state
        #self.machine_knowledge = init_state
        #self.human_obs = hum_obs
        #self.machine_obs = mach_obs


    def get_allowed_machine_actions(self,mode):
        sc = (mode == "speedcontrol")
        follow = (mode == "following")
        if sc | follow :
            allowed_mvmts = ["accel", "decel", "maintainspeed"]
        else:
            allowed_mvmts = ["none"]
        return list(itertools.product(allowed_mvmts,self.machine_comm_actions))

    def get_safety(self, human_action, machine_action):
        return self.get_safety_sub(self.scenario_number,True,human_action, machine_action)

    def get_safety_sub(self,scenario, safety, human_action, machine_action):
        anti_decel = ["accel", "maintainspeed"]
        anti_accel = ["decel"]
        if ~safety:
            return False
        else:
            if (scenario == 1) | (scenario == 2) | (scenario == 5):
                if (human_action == "decel"):
                    return True
                elif (machine_action == "decel") & ~(human_action in anti_decel):
                    return True
                else:
                    return False
            elif (scenario == 3) | (scenario == 7):
                if (human_action == "decel"):
                    return False
                elif (machine_action == "decel") & ~(human_action in anti_decel):
                    return False
                else:
                    return True
            elif (scenario == 4) | (scenario == 8):
                if human_action == "accel":
                    return True
                elif (machine_action == "accel") & ~(human_action in anti_accel):
                    return True
                else:
                    return False
            elif (scenario == 6):
                return False
            else:
                print("ERROR! Unrecognized scenario!")


    def check_in_row(self,row, mode, human_action, machine_action):
        [start_mode, next_mode, machine_act, human_act] = row
        if mode in start_mode:
            if (human_action == human_act) | (machine_action == machine_act):
                return [True, next_mode]
        return [False, []]

    def get_mode_change(self,trans_table, curr_mode, machine_action, human_action):
        for row in trans_table:
            #print(row)
            #print([curr_mode, machine_action, human_action])
            [test, next] = self.check_in_row(row, curr_mode, machine_action, human_action)
            #print(test)
            if test:
                return next[0]
        return curr_mode

    def get_next_mode(self, mode, hum_mvmt, mach_mvmt):
        new_mode = self.get_mode_change(mode_change_table, mode, hum_mvmt, mach_mvmt)
        #probabilistic mode changes
        p_error = self.prob_dict["error"]
        p_exit_hold = self.prob_dict["exit_hold"]
        #TODO :Include this block?
        '''
        if mode == "hold":
            decision = random.choices([True, False], weights = (p_exit_hold, 1-p_exit_hold), k=1)
            if decision[0]:
                possible_next_states = ["following", "speed_control"]
                next_state = random.choices(possible_next_states, k=1)
                new_mode = next_state[0]
        error_decision = random.choices([True, False], weights = (p_error, 1-p_error), k=1)
        if error_decision[0]:
            new_mode = "error"
        '''
        return new_mode

    '''
    def update_knowledge(self,next_state, human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        self.machine_knowledge = next_state
        if (mach_comm == "communicate") | (hum_comm == "pushbutton"):
            self.human_knowledge = next_state
    '''

    def transition(self,start_state, human_action, machine_action):
        [mach_mvmt, mach_comm] = machine_action
        [hum_mvmt, hum_comm] = human_action
        new_mode = self.get_next_mode(start_state, hum_mvmt, mach_mvmt)
        next_state = new_mode
        return next_state



    '''
    def get_observation(self,next_state,human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        [scenario, mode, safety] = next_state
        machine_obs = ""
        if (mach_comm == "communicate") | (hum_comm == "push_button"):
            human_obs = mode
        else:
            human_obs = "none"
        return [human_obs, machine_obs]
    '''

    def get_cost(self, mode, human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        #next_state = self.transition(state,human_action,machine_action)
        safety = self.get_safety(human_action, machine_action)
        cost = 0
        # cost for human to move
        if hum_mvmt != "none":
            cost += self.costs["human movement"]
        # cost for unsafe state
        if ~safety:
            cost += self.costs["unsafe"]
        # cost of machine updating the interface
        if mach_comm == "communicate":
            cost += self.costs["machine communication"]
        return cost

    def find_obs_in_edges(self, obs, edges):
        index = 0
        for observation in edges:
            if obs == observation:
                return index
            index += 1
        print("OBS NOT FOUND IN EDGES! Edges: " + str(edges) + "Obs: " + str(obs))
        return -1

    def tree_value(self, init_state, human_tree, machine_tree):
        machine_action = machine_tree.get_root().get_action()
        human_action = human_tree.get_root().get_action()
        new_state = self.transition(init_state, human_action, machine_action)
        value = self.get_cost(new_state, human_action, machine_action)
        if human_tree.get_height() == 0:
            return value
        [human_obs, machine_obs] = self.get_observation(new_state,human_action,machine_action)
        edg_idx1 = self.find_obs_in_edges(human_obs, human_tree.root.get_edges())
        edg_idx2 = self.find_obs_in_edges(machine_obs, machine_tree.root.get_edges())
        tree1_ch = human_tree.root.get_children()
        tree2_ch = machine_tree.root.get_children()
        new_human_tree = tree1_ch[edg_idx1]
        new_machine_tree = tree2_ch[edg_idx2]
        return value + self.tree_value(new_state, new_human_tree, new_machine_tree)