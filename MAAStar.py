from builtins import range, isinstance, list
from helper_methods import *
from Dlist import *
from NodeClass import Node
from TreeClass import Tree
import copy
from StateTransitions import DecPOMDP
# from cvxopt import matrix
# from linprogglpk import LinearProg
import random


class Astarsolver:

    def __init__(self, decpomdp):
        self.decpomdp = decpomdp
        self.horizon = self.decpomdp.horizon

    def H(self):
        return 0

    def F(self, delta):
        init_state = self.decpomdp.init_state
        [tree1, tree2] = delta
        return self.H() + self.decpomdp.tree_value(init_state, tree1, tree2)

    def get_new_trees(self, roots, agent):
        new_trees = []

        if agent == "human":
            action_set = self.decpomdp.human_actions
            edges = self.decpomdp.human_obs
        else:
            action_set = self.decpomdp.machine_actions
            edges = self.decpomdp.machine_obs
        num_leaves = len(roots)
        # edges = array_product2(possible_locations, agent.obs_comm)
        print("Finding all possible sets of size " + str(len(edges)) + " of children from set of size " + str(
            len(action_set)) + "...")
        children_not_nodes = all_k_length(action_set, len(edges))
        if agent == "machine":
            children_not_nodes = self.decpomdp.remove_unallowed_pairings(children_not_nodes)
        # print("All action combos: ")
        # print(children_not_nodes)
        all_leaf_assignments = all_k_length(children_not_nodes, num_leaves)
        # print("All leaf assignments: ")
        # print(all_leaf_assignments)
        leaf_assignments = []

        for assignment in all_leaf_assignments:
            condition = False
            leaf_list = []
            for i in range(len(roots)):
                children = assignment[i]
                # print("Children: ")
                # print(children)
                temp_node = copy.deepcopy(roots[i])
                # print(roots)
                # print(roots[i])

                for j in range(len(children)):
                    child = children[j]
                    # print("Child: ")
                    # print(child)
                    edge = edges[j]

                    # print("Edge: ")
                    # print(edge)
                    temp_node.add_child(edge, Tree(Node(child)))
                    if (edge[1] == "None") & (child[1] == "Open"):
                        condition = True
                    # if (edge[1] == "Open") & (child[1]== "Communicate"):
                    # condition = True

                    temp_tree = Tree(temp_node)
                    leaf_list.append(temp_tree)

            if (condition == False):
                leaf_assignments.append(leaf_list)

        print("Number of new trees: " + str(len(leaf_assignments)))
        print("Number of leaves: " + str(len(leaf_assignments[0])))
        new_tree = leaf_assignments[0][0]
        print(new_tree.get_root().get_children())
        return leaf_assignments

    def expand(self, delta):
        print("Expanding Trees")
        # returns a list of trees and their new f scores
        human_tree, machine_tree = delta
        # print(human_tree)
        # print("HUMAN TREE:")
        # print(human_tree.tree_to_str())
        temp_human = copy.deepcopy(human_tree)
        temp_machine = copy.deepcopy(machine_tree)
        #TODO: Replace with [edge, leaf] list
        human_leaves = temp_human.get_leaves()
        machine_leaves = temp_machine.get_leaves()
        human_leaf_assignments = self.get_new_trees(human_leaves, "human")
        machine_leaf_assignments = self.get_new_trees(machine_leaves, "machine")

        # print(delta[0].tree_to_str())
        new_human_trees = []
        new_machine_trees = []
        # TO DO: replace_leaves for each new set of leaves
        for leaves in human_leaf_assignments:
            new_tree = copy.deepcopy(human_tree)
            # print("Tree: ")
            # print(new_tree.tree_to_str())
            # print("Leaves added: ")
            # for leaf in leaves:
            #    print(leaf)
            new_tree.replace_leaves(leaves)
            # print("New Tree: ")
            # print(new_tree.tree_to_str())
            new_human_trees += [new_tree]
        for leaves in machine_leaf_assignments:
            new_tree = copy.deepcopy(machine_tree)
            new_tree.replace_leaves(leaves)
            new_machine_trees += [new_tree]
            # new_tree.tree_to_str()
        # print("Pruning New Trees... ")
        if (len(new_human_trees) < 1000) & (len(new_machine_trees) < 1000):
            [human_pruned, machine_pruned] = [new_human_trees, new_machine_trees]
            # [human_pruned, machine_pruned] = self.prune(new_human_trees, new_machine_trees, human, machine)
        elif (len(new_human_trees) < 1000):
            human_pruned = new_human_trees
            machine_pruned = random.sample(new_machine_trees, 100)
        elif (len(new_machine_trees) < 1000):
            human_pruned = random.sample(new_human_trees, 100)
            machine_pruned = new_machine_trees
        else:
            human_pruned = random.sample(new_human_trees, 100)
            machine_pruned = random.sample(new_machine_trees, 100)
            # [human_pruned, machine_pruned] = self.prune_est(new_human_trees, new_machine_trees, human, machine, 100)
            # [human_pruned, machine_pruned] = [new_human_trees, new_machine_trees]
            '''
            num_human_trees = len(new_human_trees)
            num_machine_trees = len(new_machine_trees)
            #idx1 = int(num_human_trees/4)
            #idx2 = int(num_human_trees/2)
            #idx3 = int(3*num_human_trees/4)
            idx1 = 1000
            idx2 = 2000
            idx3 = 3000
            human_trees0 = new_human_trees[:idx1]
            human_trees1 = new_human_trees[idx1:idx2]
            human_trees2 = new_human_trees[idx2:idx3]
            human_trees3 = new_human_trees[idx3:]
            #idx1 = int(num_machine_trees / 4)
            #idx2 = int(num_machine_trees / 2)
            #idx3 = int(3 * num_machine_trees / 4)
            machine_trees0 = new_machine_trees[:idx1]
            machine_trees1 = new_machine_trees[idx1:idx2]
            machine_trees2 = new_machine_trees[idx2:idx3]
            machine_trees3 = new_machine_trees[idx3:4000]
            print("Prune 1... ")
            [human_pruned0, machine_pruned0] = self.prune(human_trees0, machine_trees0, human, machine)
            print("Prune 2... ")
            [human_pruned1, machine_pruned1] = self.prune(human_trees1, machine_trees1, human, machine)
            print("Prune 3... ")
            [human_pruned2, machine_pruned2] = self.prune(human_trees2, machine_trees2, human, machine)
            print("Prune 4... ")
            [human_pruned3, machine_pruned3] = self.prune(human_trees3, machine_trees3, human, machine)
            human_pruned = human_pruned0 + human_pruned1 + human_pruned2 + human_pruned3
            machine_pruned = machine_pruned0 + machine_pruned1 + machine_pruned2 + machine_pruned3
            '''

        print("Combining " + str(len(human_pruned)) + " human and " + str(len(machine_pruned)) + " machine trees...")
        list_of_deltas = []
        num_combined = 0
        for htree in human_pruned:
            for mtree in machine_pruned:
                num_combined += 1
                # print(str(num_combined) + " combined")
                list_of_deltas += [[htree, mtree]]
        # print(list_of_deltas)
        print("Number of combined trees: " + str(len(list_of_deltas)))
        dlist = []
        for elem in list_of_deltas:
            # print(elem)
            # new_elem = [elem, self.F(elem)]
            # print(len(human_pruned))
            fscore = self.F(elem, human_pruned, machine_pruned)
            dlist.append(Dlistelem(elem, fscore))
        return dlist

    def D_iter(self, D):
        d_star = D.get_max()
        print("D STAR:")
        print(d_star.get_treelist())
        d_star_treelist = d_star.get_treelist()
        tree_height = d_star_treelist[0].get_height()
        if tree_height == self.horizon - 1:
            print("One tree has been fully explored.")
            # D.print_list()
            D.removebyscore(d_star.get_fscore())
            htree, mtree = d_star.get_treelist()
            print(htree.tree_to_str())
            print(mtree.tree_to_str())
            if D.length() <= 1:
                print("SOLVED!")
                htree, mtree = d_star.get_treelist()
                print(htree.tree_to_str())
                print(mtree.tree_to_str())
                return d_star
            if D.all_same_score():
                print("SOLVED! Multiple trees with same score.")
                D.print_tree_list()
                return d_star

            # append d_star to back of list
            D.remove_from_list(d_star)
            D.add_to_list(d_star)

        else:
            D.remove_from_list(d_star)
            d_star_prime_list = self.expand(d_star_treelist)
            D.add_list_to_list(d_star_prime_list)
            for d_star_prime in d_star_prime_list:
                fscore = d_star_prime.get_fscore()
                treelist = d_star_prime.get_treelist()
                if fscore > d_star.get_fscore():
                    D.removebyscore(fscore)
        print("Length of D: " + str(len(D.get_list())))
        return D

    def solve(self):
        human_tree_list = []
        machine_tree_list = []
        init_human_action = [0, "Wait"]
        init_machine_action = [0, "DontCommunicate"]
        human_actions = [init_human_action]
        machine_actions = [init_machine_action]
        for action in human_actions:
            new_root = Node(action)
            new_tree = Tree(new_root)
            human_tree_list.append(new_tree)
        for action in machine_actions:
            new_root = Node(action)
            new_tree = Tree(new_root)
            machine_tree_list.append(new_tree)
        init_set = array_product2(human_tree_list, machine_tree_list)
        print("Inital Tree: " + str(init_set))
        size = len(init_set)
        init_D = [0] * size
        for i in range(len(init_set)):
            elem = init_set[i]
            init_D[i] = (Dlistelem(elem, self.F(elem, human_actions, machine_actions)))
        D = Dlist(init_D)
        print("*****************D initialized*****************")
        while D.not_empty():
            d_star = D.get_max()
            print("D STAR:")
            print(d_star.get_treelist())
            d_star_treelist = d_star.get_treelist()
            tree_height = d_star_treelist[0].get_height()
            if tree_height == self.horizon - 1:
                print("One tree has been fully explored.")
                D.print_list()
                D.removebyscore(d_star.get_fscore())
                htree, mtree = d_star.get_treelist()
                print(htree.tree_to_str())
                print(mtree.tree_to_str())
                if D.length() <= 1:
                    print("SOLVED!")
                    htree, mtree = d_star.get_treelist()
                    print(htree.tree_to_str())
                    print(mtree.tree_to_str())
                    return d_star
                if D.all_same_score():
                    print("SOLVED! Multiple trees with same score.")
                    D.print_tree_list()
                    return d_star

                # append d_star to back of list
                D.remove_from_list(d_star)
                D.add_to_list(d_star)

            else:
                D.remove_from_list(d_star)
                d_star_prime_list = self.expand(d_star_treelist)
                D.add_list_to_list(d_star_prime_list)
                for d_star_prime in d_star_prime_list:
                    fscore = d_star_prime.get_fscore()
                    treelist = d_star_prime.get_treelist()
                    if fscore > d_star.get_fscore():
                        D.removebyscore(fscore)
            print("Length of D: " + str(len(D.get_list())))













