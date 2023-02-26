# Name: pa2.py
# Author(s): Jared Flejter, Matthew Gloriani
# Date:
# Description:

from audioop import mul
import re
from queue import Queue


class NFA:
    """ Simulates an NFA """

    def __init__(self, nfa_filename):
        """
		Initializes NFA from the file whose name is
		nfa_filename.  (So you should create an internal representation
		of the nfa.)
		"""
        # Opening file and splitting into tokens
        infile = open(nfa_filename, "r")
        tokens = infile.readlines()
        with open(nfa_filename, "r") as file:
            tokens = file.read().split("\n")
        while "" in tokens:
            tokens.remove("")
        # Print out each line of the txt file
        # print(tokens)

        # Initializing states for DFA
        self.states = []
        self.alphabet = []
        self.start_state = ""
        self.accept_states = []
        self.transition_dict = {}
        self.e_dict = {}  # possibly do epsilon closure in init

        # Splitting the lines of the txt file into their respective places
        # States initialization
        inc = 1
        while inc <= int(tokens[0]):
            self.states.append(str(inc))
            inc += 1
        self.num_states = len(self.states)

        # Alphabet initialization
        for i in tokens[1]:
            self.alphabet.append(str(i))

        # Start state initialization
        self.start_state = str(tokens[-2])

        # Accept states initialization
        parts = tokens[-1].split()
        for i in parts:
            self.accept_states.append(i)

        # Transition function initialization
        transitions = tokens[2:-2]
        count = 0
        while count < len(
            transitions
        ):  # going back to nested list from Matthew's pa1 but using our new file read
            transitions[count] = transitions[count].split()
            transitions[count][1] = transitions[count][1].strip(
                "'"
            )  # removes quotes in middle part
            # seperate epsilon transitions
            if transitions[count][1] == "e":
                if transitions[count][0] in self.e_dict:
                    self.e_dict[transitions[count][0]].append(transitions[count][2])
                else:
                    self.e_dict[transitions[count][0]] = [transitions[count][2]]
                transitions.pop(count)
                count -= 1
            count += 1
        self.epsilon_check()
        self.make_dict(transitions)
        self.epsilon_combo()

    def toDFA(self, dfa_filename):
        """
		Converts the "self" NFA into an equivalent DFA
		and writes it to the file whose name is dfa_filename.
		The format of the DFA file must have the same format
		as described in the first programming assignment (pa1).
		This file must be able to be opened and simulated by your
		pa1 program.

		This function should not read in the NFA file again.  It should
		create the DFA from the internal representation of the NFA that you 
		created in __init__.
		"""
        # init dict for new transitions, init queue, and put start state in queue
        self.final_transitions = {}
        self.incomplete_states = Queue()
        self.incomplete_states.put(self.start_state)
        # loop while the queue has something in it
        while not (self.incomplete_states.empty()):
            # pull state out of queue to indicate current state being worked on
            current_state = tuple(self.incomplete_states.get())
            # if current state hasn't been mapped then go through the process
            if current_state not in self.final_transitions:
                # cycle through alphabet
                for character in self.alphabet:
                    # cycle through individual states in state we are currently focussing on
                    transitioned = []
                    for state in current_state:
                        # needed to pull state that we transition to
                        if (
                            state in self.transition_dict
                            and character in self.transition_dict[state]
                        ):
                            to_state = self.transition_dict[state][character]
                            # checks if state has been transitioned to
                            for x in to_state:
                                if x not in transitioned:
                                    transitioned.append(x)
                    # add current state to dict as well as current character in alphabet
                    current_state = tuple(sorted(current_state))
                    transitioned.sort()
                    if current_state not in self.final_transitions:
                        self.final_transitions[current_state] = {
                            character: transitioned
                        }
                    else:
                        self.final_transitions[current_state][character] = transitioned
                    # add transition list to dictionary value and to the queue
                    self.incomplete_states.put(transitioned)
        self.scribo_DFA(dfa_filename)

    def scribo_DFA(self, dfa_filename):
        """
		Writes to the dfa_filename given in the test function
		@param dfa_filename - the dfa_filename to write to
		@return - none
		"""
        dfa = open(dfa_filename, "w")
        final_states = {}
        count = 1
        for key in self.final_transitions:
            final_states[key] = count
            count += 1
        self.start_state = tuple(self.start_state)
        final_start = final_states[tuple(sorted(self.start_state))]
        final_accepts = []
        for key in self.final_transitions:
            for state in self.accept_states:
                if state in key:
                    final_accepts.append(final_states[key])

        # Number of states
        dfa.write(f"{len(self.final_transitions)}\n")

        # Alphabet
        for sym in self.alphabet:
            dfa.write(f"{sym}")  # alphabet
        dfa.write(f"\n")

        # Transition states TODO
        for key in self.final_transitions:
            for key2 in self.final_transitions[key]:
                dfa.write(
                    f"{final_states[key]} '{key2}' {final_states[tuple(self.final_transitions[key][key2])]}\n"
                )

        # Start state(s) TODO
        dfa.write(f"{final_start}\n")

        # Accept states TODO
        for element in final_accepts:
            dfa.write(f"{element} ")

        # Close dfa file
        dfa.close()

    def epsilon_combo(
        self,
    ):  # NEEDS WORK/MODIFICATION in order to include epsilon transitions not in start state
        if self.start_state in self.e_dict:
            self.start_state = [self.start_state]
            self.start_state += self.e_dict[self.start_state[0]]
        else:
            self.start_state = [self.start_state]
        return

    def epsilon_check(self):
        for key in self.e_dict:
            for val in self.e_dict[key]:
                if val in self.e_dict:
                    self.e_dict[key] += self.e_dict[val]

    def make_dict(
        self, trans
    ):  # makes a dict for the transitions using the nested list in init
        for element in trans:
            if element[0] not in self.transition_dict:
                self.transition_dict[element[0]] = {element[1]: [element[2]]}
            elif element[1] not in self.transition_dict[element[0]]:
                self.transition_dict[element[0]][element[1]] = [element[2]]
            else:
                self.transition_dict[element[0]][element[1]].append(element[2])

            if element[2] in self.e_dict:
                self.transition_dict[element[0]][element[1]].extend(
                    self.e_dict[element[2]]
                )
        return


if __name__ == "__main__":
    """ 
	Tester function to test each case
	"""
    version = 5  # change this number as needed
    print(f"Version NFA{version}")
    nfa = NFA(f"nfa{version}.txt")
    nfa.toDFA(f"dfa{version}.txt")

