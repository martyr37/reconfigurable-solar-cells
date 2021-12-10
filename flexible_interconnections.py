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
    
    a = shared_node('1011', '-')
    shared_node('2021', a)

    return circuit
    
print(interconnection('-(1011)(2021)+', 2, 2, uniform_shading(2,2)))