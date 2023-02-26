# Name: pa1.py
# Author(s): Jared Flejter and Matthew Gloriani
# Date:9/28/2022
# Description: creating a DFA simulation with text files giving the DFA parameters
import sys
import re


class DFA:
    """ Simulates a DFA """

    def __init__(self, filename):
        """
        Initializes DFA from the file whose name is
        filename
        """
        # Add your code
        file = open(filename, "r")
        self.num_states = file.readline().strip("\n")  # reads first line
        self.alphabet = file.readline().strip(
            "\n"
        )  # reads second line as single string
        reg = re.compile("\d*\s...\s\d*")  # makes regex for checking for transitions
        self.transitions = []  # makes empty list for transitions
        nextline = file.readline().strip("\n")
        while reg.match(nextline):
            tran_uncut = nextline.split(" ")
            trans = []
            trans.append(tran_uncut[0])
            trans.append(tran_uncut[1][1])
            trans.append(tran_uncut[2])
            nextline = file.readline().strip("\n")
            self.transitions.append(trans)
        self.start = nextline
        self.accept_states = file.readline().strip("\n").split(" ")
        file.close()

    def simulate(self, str):
        """ 
        Simulates the DFA on input str.  Returns
        True if str is in the language of the DFA,
        and False if not.
        """
        # Add your code
        current = self.start
        for element in str:
            for x in range(len(self.transitions)):
                if current == self.transitions[x][0]:
                    if element == self.transitions[x][1]:
                        current = self.transitions[x][2]
                        break

        if current in self.accept_states:
            return True
        else:
            return False

