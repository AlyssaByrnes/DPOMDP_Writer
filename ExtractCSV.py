import csv

def latex_to_table(filename):
    with open(filename) as csvfile:
        table = []
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            #print(row)
            [start,next,cause] = row
            cause = cause.split(",")
            if len(cause)==1:
                cause = cause[0].split("_")
                if cause[0] == "human":
                    human_action = cause[1]
                    machine_action = ""
                elif cause[0] == "machine":
                    machine_action = cause[1]
                    human_action = "none"
                new_row = [start.split(","), next.split(","), machine_action, human_action]
                #print(new_row)
                table.append(new_row)
        return table




filename = 'FSRATransitionTable.csv'

with open(filename) as csvfile:
    table = ""
    reader = csv.reader(csvfile, delimiter=";")
    for row in reader:
        #print(row)
        [start,next,condition,spec] = row
        table_row = str(start) + " & "
        table_row += str(next) + " & "
        table_row += condition + " \\\\" + "\n"
        table += table_row
    #print(table)

#print(latex_to_table("TransitionLatexClean.csv"))