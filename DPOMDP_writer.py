from StateTransitions import DecPOMDP
import itertools
import copy
from help_methods import *

class DPOMDPWriter:

    def __init__(self,mach_comm_acts, mach_move_acts,hum_comm_acts,hum_move_acts,scenarios,modes,prob_dict,mach_obs,hum_obs,cost_dict):
        self.states = list(itertools.product(scenarios,modes,[True, False]))
        self.human_actions = list(itertools.product(hum_move_acts, hum_comm_acts))
        self.machine_actions = list(itertools.product(mach_move_acts, mach_comm_acts))
        self.decpomdp = DecPOMDP(mach_comm_acts, mach_move_acts,hum_comm_acts,hum_move_acts,scenarios,prob_dict,modes)
        self.machine_observations = mach_obs
        self.human_observations = hum_obs
        self.costs = cost_dict

    def state_to_str(self,state):
        #print(state)
        [scenario, mode, safety] = state
        if safety:
            safe_state = "safe"
        else:
            safe_state = "unsafe"
        name = int_to_string(scenario)+"-"+mode+"-"+safe_state
        return name

    def all_states_to_str(self):
        state_str = "states:"
        for state in self.states:
            state_str += " " + self.state_to_str(state)
        #print(state_str)
        return state_str

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
            if elem != "none":
                elem = self.state_to_str(elem)
            output_str += elem + " "
        return output_str[:-1]

    def get_cost(self, next_state, human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        [scenario,mode,safety] = next_state
        cost = 0
        #cost for human to move
        if hum_mvmt != "none":
            cost += self.costs["human movement"]
        #cost for unsafe state
        if ~safety:
            cost += self.costs["unsafe"]
        #cost of machine updating the interface
        if mach_comm == "communicate":
            cost += self.costs["machine communication"]
        return cost

    def get_reward_string(self, start_state, human_action, machine_action):
        #Sample str: R: switch-ctrl down : loc23-rmap2-ctrlM : * : * : 95
        rew_str = "R: " + self.action_to_str(human_action) + " " + self.action_to_str(machine_action) + " : "
        rew_str += self.state_to_str(start_state) + " : * : * : "
        rew_str += str(self.get_cost_from_start_state(start_state,human_action,machine_action)) + "\n"
        return rew_str


    def get_observation(self,next_state,human_action, machine_action):
        [hum_mvmt, hum_comm] = human_action
        [mach_mvmt, mach_comm] = machine_action
        [scenario, mode, safety] = next_state
        machine_obs = self.state_to_str(next_state)
        if (mach_comm == "communicate") | (hum_comm == "pushbutton"):
            human_obs = self.state_to_str(next_state)
        else:
            human_obs = "none"
        return [human_obs, machine_obs]

    def get_observation_string(self, start_state, human_action, machine_action):
        #sample string: O: right comm : loc31-rmap2-ctrlH : obs2 obs2: 1
        obs_str = "O: " + self.action_to_str(human_action) + " " + self.action_to_str(machine_action) + " : "
        next_state = self.decpomdp.transition(start_state,human_action,machine_action)
        [human_obs, machine_obs] = self.get_observation(next_state,human_action,machine_action)
        obs_str += self.state_to_str(start_state) + " : " + human_obs + " " + machine_obs + " : 1\n"
        return obs_str



    def new_trans_string(self, prefix, next_state, prob) :
        prefix += self.state_to_str(next_state) + " : " + str(prob) + "\n"
        return prefix

    def get_cost_from_start_state(self, start_state, hum_action, mach_action):
        next_state = self.decpomdp.transition(start_state,hum_action,mach_action)
        return self.get_cost(next_state,hum_action,mach_action)

    def get_transition_strings(self, state, human_action, machine_action):
        #Gets Transition strings for the LARGE ACC Model
        #T: right right : loc23-rmap2-ctrlM : loc23-rmap1-ctrlM : .1
        transition_list = []
        prefix = "T: " + self.action_to_str(human_action) + " " + self.action_to_str(machine_action) + " : "
        prefix += self.state_to_str(state) + " : "
        [start_scenario, start_mode, start_safety] = state
        p_hold_exit = self.decpomdp.prob_dict["exit_hold"]
        p_scenario_change = self.decpomdp.prob_dict["scenario_change"]
        p_error = self.decpomdp.prob_dict["error"]
        next_state = self.decpomdp.transition(state, human_action, machine_action)
        [next_scenario, original_next_mode, next_safety] = next_state

        #hold exit : transition from hold to standby
        #error : transition from any state to error
        #scenario change : transition from any scenario to a different one
        other_scenarios = copy.copy(self.decpomdp.scenario_numbers)
        other_scenarios.remove(start_scenario)
        num_scenarios = len(other_scenarios)
        if (start_mode == "hold"):
            # Case 1: Hold Exit, Scenario Change and Error
            likelihood1 = p_hold_exit * p_scenario_change * p_error
            next_mode = "error"

            for scenario in other_scenarios:
                new_state = [scenario, next_mode, next_safety]
                likelihood = likelihood1/num_scenarios
                transition_list += [self.new_trans_string(prefix, new_state, likelihood)]
            # Case 2: Hold Exit, Scenario Change
            likelihood2 = p_hold_exit * p_scenario_change
            next_modes = ["following","speedcontrol"]
            for next_mode in next_modes:
                likelihood = likelihood2/2
                for scenario in other_scenarios:
                    likelihood = likelihood/num_scenarios
                    new_state = [scenario, next_mode, next_safety]
                    transition_list += [self.new_trans_string(prefix,new_state,likelihood)]
            # Case 3: Hold Exit, Error
            likelihood3 = p_hold_exit * p_error
            next_mode = "error"
            new_state = [next_scenario,next_mode,next_safety]
            transition_list += [self.new_trans_string(prefix, new_state, likelihood3)]
            # Case 4: Hold Exit
            likelihood4 = p_hold_exit
            next_modes = ["following","speedcontrol"]
            for next_mode in next_modes:
                likelihood = likelihood4/2
                new_state = [next_scenario,next_mode,next_safety]
                transition_list += [self.new_trans_string(prefix,new_state,likelihood)]
        # Case 5: Scenario Change, Error
        likelihood5 = p_scenario_change * p_error
        likelihood = likelihood5/num_scenarios
        for scenario in other_scenarios:
            new_state = [scenario, "error", next_safety]
            transition_list += [self.new_trans_string(prefix,new_state,likelihood)]
        # Case 6: Error
        likelihood6 = p_error
        new_state = [next_scenario,"error", next_safety]
        transition_list += [self.new_trans_string(prefix,new_state,likelihood6)]
        # Case 7: Scenario Change
        likelihood7 = p_scenario_change
        likelihood = likelihood7/num_scenarios
        for scenario in other_scenarios:
            new_state = [scenario, original_next_mode, next_safety]
            #print("New State")
            #print(new_state)
            transition_list += [self.new_trans_string(prefix, new_state, likelihood)]
        #Base case:
        new_state = next_state
        #print("NEW STATE")
        #print(new_state)
        if start_mode == "hold":
            prob_no_change = 1 - likelihood1 - likelihood2 - likelihood3 - likelihood4 - likelihood5 - likelihood6 - likelihood7
        else:
            prob_no_change = 1 - likelihood5 - likelihood6 - likelihood7
        transition_list += [self.new_trans_string(prefix, new_state, prob_no_change)]
        return combine_duplicates(transition_list)



    def get_transitions(self):
        transitions = []
        observations = []
        rewards = []
        for state in self.states:
            [scenario, mode, safety] = state
            m_actions = self.decpomdp.get_allowed_machine_actions(mode)
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
        print(file_data)
        f = open(filename, "w")
        f.writelines(file_data)
        f.close()
