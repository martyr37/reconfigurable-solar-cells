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
    
    output_nodes = [] # list containing output nodes that need to be connected together to form one node
    
    char_list = [x for x in formatted_string] # list of characters in format string
    
    for current_char in char_list:
        
        if in_brackets == False:
            
            if current_char == '-':
                preceding_node = '-'
            elif current_char == '(':
                in_brackets = True
            elif current_char == '+':
                output_nodes.append(preceding_node) # add to output_nodes the name of the last node
                preceding_node = '+'
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
    
    
    if preceding_node == '+':
        preceding_node = output_nodes[-1]
        
    if len(output_nodes) >= 2:
        for index in range(0, len(output_nodes), 2): # join nodes that are meant to be the same output node
            circuit.R('wire' + str(index), output_nodes[index], output_nodes[index + 1], 0)
    
    return circuit, preceding_node
#%%
#circuit, output_node = interconnection('-00011110+', 2, 2, uniform_shading(2,2,current=10))
#circuit, output_node = interconnection('-(0001)(1011)+', 2, 2, uniform_shading(2,2,current=10))
#circuit, output_node = interconnection('-00(0111)10+', 2, 2, uniform_shading(2,2,current=10))
#circuit, output_node = interconnection('-(0010)0111+', 2, 2, uniform_shading(2,2,current=10))
#circuit, output_node = interconnection('-(0011)(0110)+', 2, 2, uniform_shading(2,2,current=10))
#circuit, output_node = interconnection('-(0010)(0111)(0212)(0313)+', 4, 2, uniform_shading(2,4,current=10))
#circuit, output_node = interconnection('-001312(0111)100203+', 4, 2, uniform_shading(2,4,current=10))

###TCT###I
#circuit, output_node = interconnection('-(0010)(0111)+', 2, 2, uniform_shading(2,2,current=10))

###SP###
circuit, output_node = interconnection('-0001+-1011+', 2, 2, uniform_shading(2,2,current=10))

circuit.V('output', circuit.gnd, output_node, 99)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Voutput=slice(0,10,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Voutput))
plt.xlim(left=0)
plt.ylim(bottom=0, top=50)
print(circuit)
print(output_node)
#%%
#TODO: generate all possible strings given dimensions. 
# perhaps simply bruteforce with the restriction that - and + should have pairs, and each cell is 
# referred to once. Then all other invalid strings will throw errors? not sure what monstrosities 
# will arise

def generate_string(columns, rows):
    pass #





