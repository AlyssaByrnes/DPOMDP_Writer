
import itertools
import copy
from help_methods import *
from ExtractCSV import latex_to_table

mode_change_table = latex_to_table("TransitionLatexClean.csv")

class DPOMDPWriterMedACC:

    def __init__(self,mach_comm_acts, mach_move_acts,hum_comm_acts,hum_move_acts,modes,prob_dict,cost_dict, scenario_number, human_observations, machine_observations):
        #since this is medium, there is only 1 scenario
        self.states = modes
        self.human_actions = list(itertools.product(hum_move_acts, hum_comm_acts))
        self.machine_comm_actions = mach_comm_acts
        self.machine_actions = list(itertools.product(mach_move_acts, mach_comm_acts))
        #self.decpomdp = DecPOMDP_medium(mach_comm_acts, mach_move_acts,hum_comm_acts,hum_move_acts,prob_dict,modes,scenario_number, cost_dict)
        self.costs = cost_dict
        self.scenario = scenario_number
        self.prob_dict = prob_dict
        self.scenario_number = scenario_number
        self.human_observations = human_observations
        self.machine_observations = machine_observations


    def get_allowed_machine_actions(self,mode):
        sc = (mode == "speedcontrol")
        follow = (mode == "following")
        if sc | follow :
            allowed_mvmts = ["accel", "decel", "maintainspeed"]
        else:
            allowed_mvmts = ["none"]
        return list(itertools.product(allowed_mvmts,self.machine_comm_actions))

    def all_states_to_str(self):
        state_str = "states:"
        for state in self.states:
            state_str += " " + state
        #print(state_str)
        return state_str

    def state_to_str(self, state):
        return state

    def action_to_str(self,action):
        [mvmt, comm] = action
        return mvmt + "-" + comm

    def action_list_to_str(self, action_list):
        action_str = ""
        for act in action_list:
            action_str += self.action_to_str(act) + " "
        return action_str[:-1]

    def list_to_str(self, inp_list):
        output_str = ""
        for elem in inp_list:
            output_str += elem + " "
        return output_str[:-1]

    def get_safety(self,human_action, machine_action):
        #input PHYSICAL MOVEMENT actions as human_action and machine_action
        scenario = self.scenario
        anti_decel = ["accel", "maintainspeed"]
        anti_accel = ["decel"]
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

    def get_cost(self, start_state, human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        safety = self.get_safety(hum_mvmt, mach_mvmt)
        cost = 0
        # cost for human to move
        if hum_mvmt != "none":
            cost += self.costs["human movement"]
        # cost for unsafe state
        if safety == False:
            cost += self.costs["unsafe"]
        # cost of machine updating the interface
        if mach_comm == "communicate":
            cost += self.costs["machine communication"]
        return cost


    def get_reward_string(self, start_state, human_action, machine_action):
        #Sample str: R: switch-ctrl down : loc23-rmap2-ctrlM : * : * : 95
        rew_str = "R: " + self.action_to_str(human_action) + " " + self.action_to_str(machine_action) + " : "
        rew_str += self.state_to_str(start_state) + " : * : * : "
        rew_str += str(self.get_cost(start_state,human_action,machine_action)) + "\n"
        return rew_str


    def get_observation(self,next_state,human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        machine_obs = self.state_to_str(next_state)
        if (mach_comm == "communicate") | (hum_comm == "pushbutton"):
            human_obs = self.state_to_str(next_state)
        else:
            human_obs = "none"
        return [human_obs, machine_obs]

    def has_array_match(self, array1, array2):
        #just a helper method for the following method
        [comp1, comp2] = array2
        for elem in array1:
            [temp1, temp2] = elem
            if (temp1 == comp1) & (temp2 == comp2):
                return True
        return False

    def get_observation_string(self, start_state, human_action, machine_action):
        #sample string: O: right comm : loc31-rmap2-ctrlH : obs2 obs2: 1
        obs_str = ""
        prefix = "O: " + self.action_to_str(human_action) + " " + self.action_to_str(machine_action) + " : "
        prefix += self.state_to_str(start_state) + " : "
        transitions = self.get_possible_transitions(start_state, human_action, machine_action)
        if len(transitions) == 0:
            #state stays the same
            next_state = start_state
            [human_obs, machine_obs] = self.get_observation(next_state,human_action,machine_action)
            obs_str += prefix + self.state_to_str(next_state) + " : " + human_obs + " " + machine_obs + " : 1\n"
        else:
            explored_transitions = []
            for t in transitions:
                [cause, next_state] = t
                start_end_pair = [start_state, next_state]
                #this check prevents repeats if multiples of the same transition can happen from different causes
                check = self.has_array_match(explored_transitions,start_end_pair)
                if (check == False):
                    explored_transitions.append(start_end_pair)
                    [human_obs, machine_obs] = self.get_observation(next_state,human_action,machine_action)
                    obs_str += prefix + self.state_to_str(next_state) + " : " + human_obs + " " + machine_obs + " : 1\n"
        return obs_str



    def new_trans_string(self, prefix, next_state, prob) :
        prefix += self.state_to_str(next_state) + " : " + str(prob) + "\n"
        return prefix

    def get_cost_from_start_state(self, start_state, hum_action, mach_action):
        next_state = self.decpomdp.transition(start_state,hum_action,mach_action)
        return self.decpomdp.get_cost(next_state,hum_action,mach_action)

    def get_possible_transitions(self, start_state, hum_action, mach_action):
        #returns a list of transitions of the form [cause, end_state]
        #print("start state: " + self.state_to_str(start_state) + "actions: " + self.action_to_str(hum_action) + " " + self.action_to_str(mach_action))
        transitions = []
        [hum_phys, hum_comm] = hum_action
        [mach_phys, mach_comm] = mach_action
        for row in mode_change_table:
            [starts, ends, cause] = row
            if start_state in starts:
                if cause[0] == "event":
                    #this means an event occurred
                    trans = [[cause, ends[0]]]
                    transitions += trans
                else:
                    if cause[0] == "human":
                        #this means it was a human action
                        if (cause[1] == hum_phys) | (cause[2] == hum_comm):
                            for end_state in ends:
                                trans = [[cause, end_state]]
                                transitions += trans
                    elif cause[0] == "machine":
                        #this means it was a machine action
                        if (cause[1] == mach_phys) | (cause[2] == mach_comm):
                            for end_state in ends:
                                trans = [[cause, end_state]]
                                transitions += trans
        #print("TRANSITIONS:" + str(transitions))
        return transitions
                                            




    def get_transition_strings(self, state, human_action, machine_action):
        #Gets Transition strings for the LARGE ACC Model
        #T: right right : loc23-rmap2-ctrlM : loc23-rmap1-ctrlM : .1
        transition_list = []
        prefix = "T: " + self.action_to_str(human_action) + " " + self.action_to_str(machine_action) + " : "
        prefix += self.state_to_str(state) + " : "
        p_error = self.prob_dict["error"]
        p_hold_exit = self.prob_dict["exithold"]

        possible_transitions = self.get_possible_transitions(state, human_action, machine_action)
        if len(possible_transitions)>0:
            num_transitions = float(len(possible_transitions))
            remaining_prob = float(1/num_transitions)
            if (state == "following")|(state == "speedcontrol")|(state=="hold"):
                prob_error = float(p_error/num_transitions)
                num_transitions = num_transitions - 1
                if num_transitions > 0:
                    remaining_prob = float((1 - prob_error)/num_transitions)
            if state == "hold":
                prob_hold = p_hold_exit/num_transitions
                num_transitions = num_transitions - 1
                if num_transitions > 0:
                    remaining_prob = float((1 - prob_hold - prob_error)/num_transitions)
            for transition in possible_transitions:
                [cause, end_state] = transition
                if cause[1] == "error":
                    trans_line = prefix +  " : " + self.state_to_str(end_state) + " : " + str(prob_error) + "\n"
                elif cause[1] == "exit": 
                    trans_line = prefix +  " : " + self.state_to_str(end_state) + " : " + str(prob_hold) + "\n"
                else:
                    trans_line = prefix +   " : " + self.state_to_str(end_state) + " : " + str(remaining_prob) + "\n"
                transition_list += trans_line
        else:
            trans_line = trans_line = prefix +  " : " + state + " : 1 \n"
            transition_list += trans_line
        return transition_list
        


    def get_transitions(self):
        transitions = []
        observations = []
        rewards = []
        for state in self.states:
            mode= state
            m_actions = self.get_allowed_machine_actions(mode)
            for h_action in self.human_actions:
                for m_action in m_actions:
                    transitions += self.get_transition_strings(state,h_action,m_action)
                    observations.append(self.get_observation_string(state,h_action,m_action))
                    rewards.append(self.get_reward_string(state,h_action,m_action))
        return [transitions, observations, rewards]

    def write_to_file(self, filename, start_state):
        file_data = []
        file_data.append("agents: 2" + "\n")
        file_data.append("discount: 1" + "\n")
        file_data.append("values: reward" + "\n")
        file_data.append(self.all_states_to_str() + "\n")
        start_str = "start include: " + self.state_to_str(start_state) + "\n"
        file_data.append(start_str)
        file_data.append("actions:\n")
        file_data.append(self.action_list_to_str(self.human_actions) + "\n")
        file_data.append(self.action_list_to_str(self.machine_actions) + "\n")
        file_data.append("observations:\n")
        file_data.append(self.list_to_str(self.human_observations) + "\n")
        file_data.append(self.list_to_str(self.machine_observations) + "\n")
        [transitions, observations, rewards] = self.get_transitions()
        file_data += transitions
        file_data += observations
        file_data += rewards
        #print(file_data)
        f = open(filename, "w")
        f.writelines(file_data)
        f.close()
