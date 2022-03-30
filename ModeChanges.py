from ExtractCSV import latex_to_table

#mode_change_table = latex_to_table("TransitionLatexClean.csv")

def check_in_row(row, mode,human_action,machine_action):
    [start_mode,next_mode,machine_act,human_act] = row
    if mode in start_mode:
        if human_action == human_act:
            if (machine_action == machine_act) | (len(machine_action) == 0):
                return [True, next_mode]
    return [False,[]]

def get_mode_change(trans_table,curr_mode,machine_action,human_action):
    for row in trans_table:
        print(row)
        print([curr_mode,machine_action,human_action])
        [test, next] = check_in_row(row,curr_mode,machine_action,human_action)
        print(test)
        if test:
            return next
    return curr_mode


#test_row = mode_change_table[2]
#test_mode = test_row[0][0]
#test_mach_act = test_row[2]
#test_human_act = test_row[3]



#get_mode_change(mode_change_table,test_mode,test_mach_act,test_human_act)
