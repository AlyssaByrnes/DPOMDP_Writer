from builtins import len


class Dlistelem:
    def __init__(self, treelist, fscore):
        self.treelist = treelist
        self.fscore = fscore

    def get_treelist(self):
        return self.treelist

    def get_fscore(self):
        return self.fscore

class Dlist:

    def __init__(self, inplist):
        self.list = inplist

    def removebyscore(self, fscore):
        newlist = []
        oldlist = self.list
        for elem in oldlist:
            if elem.get_fscore() >= fscore:
                newlist.append(elem)
        self.list = newlist

    def get_list(self):
        return self.list

    def print_list(self):
        for elem in self.list:
            tree = elem.get_treelist()
            score = elem.get_fscore()
            print(str(tree) + str(score))

    def add_to_list(self, new_elem):
        self.list.append(new_elem)

    def add_list_to_list(self, inplist):
        for elem in inplist:
            self.list.append(elem)

    def get_max(self):
        temp_list = self.list
        max_elem = temp_list[0]
        max_score = max_elem.get_fscore()
        for elem in temp_list:
            #print(elem)
            if elem.get_fscore() > max_score:
                max_elem = elem
        return max_elem

    def not_empty(self):
        if len(self.list)>0:
            return True
        else:
            return False

    def remove_from_list(self, elem):
        self.list.remove(elem)

    def length(self):
        return len(self.list)

    def print_tree_list(self):
        elem_number = 0
        dlist = self.list
        for elem in dlist:
            print ("SOLUTION " + str(elem_number))
            for tree in elem.get_treelist():
                print(tree.tree_to_str())
            elem_number += 1

    def print_list(self):
        for elem in self.list:
            print(elem.get_treelist())
            print(elem.get_fscore())

    def all_same_score(self):
        #returns true if every element has same fscore
        dlist = self.list
        score = dlist[0].get_fscore()
        ret_val = True
        for elem in self.list:
            truth_val = (elem.get_fscore() == score)
            ret_val = ret_val & truth_val
        return ret_val

    def get_sep_tree_lists(self):
        dlist = self.list
        tlist1 = []
        tlist2 = []
        for elem in dlist:
            [elem1, elem2] = elem.get_treelist()
            tlist1.append(elem1)
            tlist2.append(elem2)
        return [tlist1, tlist2]