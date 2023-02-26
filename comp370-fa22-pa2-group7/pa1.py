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
        
        # opens file as needed
        file = open(filename, "r")
        self.num_states = file.readline().strip("\n")
        self.alphabet = file.readline().strip("\n")  # reads second line as single string
        
        # initializing transitions
        reg = re.compile("\d*\s...\s\d*")  # makes regex for checking for transitions
        self.transitions = []
        nextline = file.readline().strip("\n")
        while reg.match(nextline): # makes sure that transition line is valid
            tran_uncut = nextline.split(" ")
            trans = []
            trans.append(tran_uncut[0])
            trans.append(tran_uncut[1][1])
            trans.append(tran_uncut[2])
            nextline = file.readline().strip("\n")
            self.transitions.append(trans)
        
        # initializes start state
        self.start_state = nextline

        # initializes accepting states
        self.accept_states = file.readline().strip("\n").split(" ")

        # closes file for no random errors :D
        file.close()

    def simulate(self, str):
        """ 
        Simulates the DFA on input str.  Returns
        True if str is in the language of the DFA,
        and False if not.
        """
        
        # changes current state based on the transition
        current_state = self.start_state
        for element in str:
            for x in range(len(self.transitions)):
                if current_state == self.transitions[x][0]:
                    if element == self.transitions[x][1]:
                        current_state = self.transitions[x][2]
                        break

        # accepts current state if in the accepting state
        return (current_state in self.accept_states)

