#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 18:17:20 2021

@author: mlima
"""

####################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

from solar_cell import *
####################################################################################################

## assuming cell IDs are always two characters, e.g. 23, 10, etc.



def interconnection(formatted_string, columns, rows, intensity_array):
    global node_counter
    global circuit
    node_counter = 97 # refers to 'a'
    
    circuit = Circuit('Module')
    for row in range(0, rows):
        for column in range(0, columns):
            circuit.subcircuit(solar_cell(str(row) + str(column), intensity=intensity_array[row,column]))
    #print(circuit)
    
    #%%
    def shared_node(string, preceding_connection):
        global node_counter
        global circuit
        
        if preceding_connection == '-':
            preceding_connection = circuit.gnd
            
        for char in range(0, len(string), 2):
            cell_name = string[char:char+2]
            circuit.X(cell_name + 'sbckt', cell_name, preceding_connection, chr(node_counter))
            
        node_counter += 1
        
        return chr(node_counter - 1) # return the node that this will connect to
    #%%
    
    in_brackets = False # state determining whether current character is in brackets
    read_state = False # since cell names are 2 characters long, we need a way for the program to know
                        # when we're reading in a 2-character cell name and not assigning a connection to it 
    current_cell = '' # placeholder string for the above
    preceding_node = '' # the preceding node that needs to be connected to the current node
    
    string_in_brackets = [] # string for shared_node function to read in 
    
    char_list = [x for x in formatted_string] # list of characters in format string
    
    for current_char in char_list:
        
        if in_brackets == False:
            
            if current_char == '-':
                preceding_node = '-'
            elif current_char == '(':
                in_brackets = True
            elif current_char == '+':
                continue
            else: # outside of brackets, read in two characters at a time using read_state
                if read_state == False:
                    current_cell = current_char
                    read_state = True
                elif read_state == True: # connecting cells in series
                    current_cell = current_cell + current_char
                    if preceding_node == '-':
                        circuit.X(current_cell + 'sbckt', current_cell, circuit.gnd, chr(node_counter))
                    else:
                        circuit.X(current_cell + 'sbckt', current_cell, preceding_node, chr(node_counter))
                    preceding_node = chr(node_counter)
                    node_counter += 1
                    read_state = False
                
        elif in_brackets == True and current_char != ')':
            string_in_brackets.append(current_char)
        elif in_brackets == True and current_char == ')':
            preceding_node = shared_node("".join(string_in_brackets), preceding_node)
            string_in_brackets = []
            in_brackets = False
            
    
    return circuit, preceding_node
    
#circuit, output_node = interconnection('-00011110+', 2, 2, uniform_shading(2,2))
#circuit, output_node = interconnection('-(0001)(1011)+', 2, 2, uniform_shading(2,2))
#circuit, output_node = interconnection('-00(0111)10+', 2, 2, uniform_shading(2,2))
#circuit, output_node = interconnection('-(0010)0111+', 2, 2, uniform_shading(2,2))
#circuit, output_node = interconnection('-(0011)(0110)+', 2, 2, uniform_shading(2,2))
#circuit, output_node = interconnection('-(0010)(0111)(0212)(0313)+', 4, 2, uniform_shading(2,4))
circuit, output_node = interconnection('-001312(0111)100203+', 4, 2, uniform_shading(2,4))
print(circuit)
print(output_node)