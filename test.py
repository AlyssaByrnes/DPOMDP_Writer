import itertools
from DPOMDP_writer import DPOMDPWriter
from help_methods import *

modes = ["canceled", "following", "speedcontrol", "hold", "override", "error"]
automated_modes = ["following", "speedcontrol"]
non_automated_modes = ["canceled", "hold", "override","error"]
human_mvmt_actions = ["accel", "decel", "maintainspeed", "none"]
human_comm_actions = ["pushbutton","dontpushbutton"]
human_actions = list(itertools.product(human_mvmt_actions, human_comm_actions))
machine_mvmt_actions = ["accel", "decel", "maintainspeed", "none"]
machine_comm_actions = ["communicate","dontcommunicate"]
machine_actions = list(itertools.product(machine_mvmt_actions, machine_comm_actions))
scenario_numbers = range(1,9)
safety_bools = [True, False]

scenario_change_prob = .01
error_prob = .01
exit_hold_prob = .01

states = list(itertools.product(scenario_numbers, modes, safety_bools))
machine_observations = states
human_observations = states + ["none"]
#print(human_observations)

prob_dict = {"scenario_change": scenario_change_prob, "exit_hold": exit_hold_prob, "error":error_prob}

human_movement_cost = -1
unsafe_cost = -100
comm_cost = -1
cost_dict = {"human movement":human_movement_cost, "unsafe": unsafe_cost, "machine communication": comm_cost}


writer = DPOMDPWriter(machine_comm_actions, machine_mvmt_actions, human_comm_actions, human_mvmt_actions, scenario_numbers, modes,prob_dict, machine_observations,human_observations,cost_dict)

file_name = "test.dpomdp"
test_state = states[0]
#print(test_state)
test_human_action = human_actions[0]
test_machine_action = machine_actions[0]
trans_table = writer.get_transition_strings(test_state,test_human_action,test_machine_action)
test_entry = trans_table[1]
data = get_data_from_trans_str(test_entry)
#print(writer.eq_arrays(data,data))
#print(trans_table)
writer.write_to_file(file_name, test_state)
#print(data)
#print(data[-1])
