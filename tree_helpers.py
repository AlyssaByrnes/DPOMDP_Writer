def encode_obs(obs):
    if obs == "Information":
        ret_str = "A"
    elif obs == "None":
        ret_str = "B"
    elif obs == "Open":
        ret_str = "C"
    elif obs == "Wait":
        ret_str = "D"
    else:
        print("ERROR! No observation found to match " + obs)
        ret_str = 0
    return ret_str


def encode_action(action):
    if action == "Open":
        ret_str = "C"
    elif action == "Wait":
        ret_str = "D"
    elif action == "Communicate":
        ret_str = "E"
    elif action == "DontCommunicate":
        ret_str = "F"
    else:
        print("ERROR! No action found to match " + action)
        ret_str = 0
    return ret_str


