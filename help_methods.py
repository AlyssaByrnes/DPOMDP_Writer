def get_action_from_str(action_string):
    action = action_string.split("-")
    # print(action)
    return action


def get_state_from_str(state_str):
    state_array = state_str.split("-")
    scenario_int = string_to_int(state_array[0])
    state_array[0] = scenario_int
    return state_array


def eq_arrays(array1, array2):
    for idx in range(len(array1)):
        if array1[idx] != array2[idx]:
            return False
    return True


def get_data_from_trans_str(entry):
    # print(entry)
    entry_array = entry.split(' ')
    # print(entry_array)
    human_action = get_action_from_str(entry_array[1])
    machine_action = get_action_from_str(entry_array[2])
    start_state = get_state_from_str(entry_array[4])
    next_state = get_state_from_str(entry_array[6])
    prob = entry_array[8]
    prob = float(prob[:-1])
    data = [human_action, machine_action, start_state, next_state, prob]
    # print data
    return data

def get_entry_index(entry, table):
    test_array = get_data_from_trans_str(entry)
    for idx in range(len(table)):
        temp_array = get_data_from_trans_str(table[idx])
        if eq_arrays(test_array, temp_array):
            return [True, idx]
    return [False, -1]

def same_transition(entry1,entry2):
    data1 = get_data_from_trans_str(entry1)
    data2 = get_data_from_trans_str(entry2)
    same_trans = eq_arrays(data1[:-1],data2[:-1])
    return same_trans

def combine_entries(entry1,entry2):
    data1 = get_data_from_trans_str(entry1)
    data2 = get_data_from_trans_str(entry2)
    prob1 = data1[-1]
    prob2 = data2[-1]
    new_prob = prob1 + prob2
    entry_array = entry1.split(' ')
    len_array = len(entry_array)
    new_string = ""
    for idx in range(len_array-1):
        new_string += entry_array[idx] + " "
    new_string += str(new_prob) + "\n"
    #print("new entry: ")
    #print(new_string)
    return new_string


def remove_entry_from_table(entry, table):
    [in_table, idx] = get_entry_index(entry, table)
    if in_table:
        new_table = []
        new_table += table[:idx]
        new_table += table [idx+1:]
        return new_table
    else:
        print("ERROR! Not in table!")
        print(entry)
        print_table(table)
        return table

def print_table(table):
    for elem in table:
        print(elem)

def get_duplicates(entry, table, entry_idx):
    duplicates = []
    num_elem = len(table)
    for idx in range(num_elem):
        elem = table[idx]
        if same_transition(entry,elem):
            if idx != entry_idx:
                duplicates.append(elem)
    return duplicates

def combine_duplicates(table):
    upper_bound = len(table)
    idx = 0
    while idx < upper_bound:
        #print(table)
        test_entry = table[idx]
        duplicates = get_duplicates(test_entry, table, idx)
        num_duplicates = len(duplicates)
        if num_duplicates > 0:
            #print("Duplicates")
            #print(duplicates)
            table = remove_entry_from_table(test_entry,table)
            for duplicate in duplicates:
                test_entry = combine_entries(test_entry,duplicate)
                table = remove_entry_from_table(duplicate,table)
            upper_bound -= 1
            upper_bound -= num_duplicates
            table.append(test_entry)
        else:
            idx += 1
    return table

def int_to_string(inp_number):
    if inp_number == 1:
        return "one"
    if inp_number == 2:
        return "two"
    if inp_number == 3:
        return "three"
    if inp_number == 4:
        return "four"
    if inp_number == 5:
        return "five"
    if inp_number == 6:
        return "six"
    if inp_number == 7:
        return "seven"
    if inp_number == 8:
        return "eight"

def string_to_int(inp_string):
    if inp_string == "one":
        return 1
    if inp_string == "two":
        return 2
    if inp_string == "three":
        return 3
    if inp_string == "four":
        return 4
    if inp_string == "five":
        return 5
    if inp_string == "six":
        return 6
    if inp_string == "seven":
        return 7
    if inp_string == "eight":
        return 8




