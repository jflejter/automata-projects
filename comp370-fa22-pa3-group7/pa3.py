# Name: pa3.py
# Author(s): Jared Flejter, Matthew Gloriani
# Date:
# Description:


class InvalidExpression(Exception):
    pass


class RegEx:
    def __init__(self, filename):
        """ 
		Initializes a RegEx object from the specifications
		in the file whose name is filename.
		"""
        file = open(filename, "r")
        self.alph = file.readline().strip("\n")
        self.exp = file.readline().strip("\n").replace(" ", "")
        file.close()
        self.s1 = []  # operands
        self.s2 = [None]  # operators
        self.prev = ""
        for current in self.exp:
            # current = self.exp[i]
            if (
                (current in self.alph)
                or current == "("
                or current == "e"
                or current == "N"
            ):
                if (
                    self.prev != "(" and self.prev != "|" and self.prev != ""
                ):  # implied concat
                    while self.s2[-1] != None and (
                        self.s2[-1] == "*" or self.s2[-1] == "^"
                    ):
                        root = self.subtree()
                        self.s1.append(root)
                    self.s2.append("^")
                if current == "(":
                    self.s2.append(current)
                else:
                    self.s1.append(Node(current))

            elif current == "*" or current == "|":
                if current == "*":
                    while self.s2[-1] != None and self.s2[-1] == "*":
                        self.s1.append(self.subtree())
                if current == "|":
                    while self.s2[-1] != None and (
                        self.s2[-1] == "*" or self.s2[-1] == "^" or self.s2[-1] == "|"
                    ):
                        self.s1.append(self.subtree())
                self.s2.append(current)

            elif (
                current == ")"
            ):  # make its own function to recursively call in case of another ')'
                while self.s2[-1] != "(":
                    self.s1.append(self.subtree())
                self.s2.pop()

            else:
                raise InvalidExpression()

            self.prev = current
        while self.s2[-1] != None:  # making final tree and storing it in s1
            if self.s2[-1] == "(":
                raise InvalidExpression()
            self.s1.append(self.subtree())

        tree = self.s1.pop()
        # start depth first traversal of tree to create NFA
        nfa = self.traversal(tree)
        self.dfa = DFA(nfa, self.alph)

    def simulate(self, str):
        """
		Returns True if the string str is in the language of
		the "self" regular expression.
		"""
        return self.dfa.simulate(str)

    # you will likely add other methods to this class
    def subtree(self):
        try:
            operator = self.s2.pop()
            root = Node(operator)
            if operator == "*":
                root.insert(0, self.s1.pop())
            else:
                root.insert(1, self.s1.pop())
                root.insert(0, self.s1.pop())
        except IndexError:
            raise InvalidExpression()
        return root

    def traversal(self, current):
        if current.left != None:
            left = self.traversal(current.left)
            if current.root == "*":
                left.star_closure()
                return left
            else:
                right = self.traversal(current.right)
                if current.root == "|":
                    left.union_closure(right)
                    return left
                else:
                    left.concat_closure(right)
                    return left
        else:
            return NFA(current.root, self.alph)


# you can add other classes here, including DFA and NFA (modified to suit
# the needs of this project).


class Node:
    def __init__(self, root):
        self.left = None
        self.right = None
        self.root = root

    def insert(
        self, side, data
    ):  # be able to insert on certain sides 0 is left and 1 is right
        if self.root != None:
            if side == 0:
                if self.left is None:
                    self.left = data
            if side == 1:
                if self.right is None:
                    self.right = data


class NFA:
    def __init__(self, term, alph):
        self.alph = alph
        if term != "e" and term != "N":
            self.num_states = 2
            self.start = 0
            self.transitions = [[0, term, 1]]
            self.accept = [1]
        elif term == "e":
            self.num_states = 1
            self.start = 0
            self.transitions = []
            self.accept = [0]
        elif term == "N":
            self.num_states = 1
            self.start = 0
            self.transitions = []
            self.accept = []

    def concat_closure(self, nfa):
        for tran in nfa.transitions:
            tran[0] += self.num_states
            tran[2] += self.num_states
            self.transitions.append(tran)
        for acc in self.accept:
            self.transitions.append([acc, "e", nfa.start + self.num_states])
        self.accept = nfa.accept
        for i in range(len(self.accept)):
            self.accept[i] += self.num_states
        self.num_states += nfa.num_states

    def union_closure(self, nfa):
        for tran in nfa.transitions:
            tran[0] += self.num_states
            tran[2] += self.num_states
            self.transitions.append(tran)
        for acc in nfa.accept:
            self.accept.append(acc + self.num_states)
        self.transitions.append([self.num_states + nfa.num_states, "e", self.start])
        self.transitions.append(
            [self.num_states + nfa.num_states, "e", nfa.start + self.num_states]
        )
        self.start = self.num_states + nfa.num_states
        self.num_states += nfa.num_states + 1

    def star_closure(self):
        for acc in self.accept:
            self.transitions.append([acc, "e", self.start])
        self.transitions.append([self.num_states, "e", self.start])
        self.accept.append(self.num_states)
        self.start = self.num_states
        self.num_states += 1

    def check_states(self, states):
        not_active = {}
        for char in self.alph:
            not_active[char] = set()
            for tran in self.transitions:
                if (tran[0] in states) and (tran[1] == char):
                    not_active[char] = not_active[char] | self.get_states(tran[2])
        return not_active

    def get_states(self, state):
        active = {state}
        for tran in self.transitions:
            if tran[0] == state and tran[1] == "e":
                active = active | self.get_states(tran[2])
        return active


class DFA:
    def __init__(self, nfa, alph):
        self.transitions = []
        states = [nfa.get_states(nfa.start)]
        count = 0
        while count < len(states):
            st = nfa.check_states(states[count])
            for char in alph:
                if st[char] not in states:
                    states.append(st[char])
                self.transitions.append([count, char, states.index(st[char])])
            count += 1

        self.accept = set()
        for st_list in states:
            for acc in nfa.accept:
                if acc in st_list:
                    self.accept.add(states.index(st_list))

    def simulate(self, str):
        current = 0
        for i in str:
            for tran in self.transitions:
                if tran[0] == current and tran[1] == i:
                    current = tran[2]
                    break
        return current in self.accept

