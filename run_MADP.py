import os

filename = "test.dpomdp"

solver_type = ["AM", "CE", "MP", "BnB"]

parameter = ["MAAstar", "FSPC", "kGMAA -k 10", "MAAstarClassic"]

q_heurs = ["QMDP","QPOMDP","QBG", "QMDPc", "QPOMDPav", "QHybrid", "QPOMDPhybrid", "QBGhybrid", "QBGTreeIncPrune", "QBGTreeIncPruneBnB"]

start_bool = True

for solver in solver_type:
    for param in parameter:
        for q in q_heurs:
            command = "GMAA -G " + param
            command += " -B " + solver
            command += " -Q " + q
            command += " -h2 " + filename
            print("Command being run: " + command)
            if start_bool:
                os.system(command)