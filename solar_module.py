#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 14:28:27 2022

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
from flexible_interconnections import interconnection, generate_string, partition_grid, plot_partition
####################################################################################################
#%% 
def get_dimensions(l):
    row_coords = set()
    column_coords = set()
    for cell in l:
        row = int(cell[0])
        column = int(cell[1])
        row_coords.add(row)
        column_coords.add(column)
    number_of_columns = len(column_coords)
    number_of_rows = len(row_coords)
    return number_of_columns, number_of_rows

#%% makes an all series connection of each block
def make_block(block, intensity_array): 
    
    number_of_columns, number_of_rows = get_dimensions(block)
    
    block_string = "".join(block)
    block_string = "-" + block_string + "+"
    
    circuit, last_node = interconnection(block_string, number_of_columns, number_of_rows, intensity_array)

    return circuit, last_node, block_string
#%% change_cell_interconnection (TO BE DELETED AFTER CLASS IS MADE)
def change_cell_interconnection(circuit, intensity_array, formatted_string = None, adjacent = False):
    
    element_names = list(circuit.element_names)
    cell_names = []
    for cell in element_names:
        cell_names.append(cell[1] + cell[2])
        
    ## use generate_string to change interconnection
    cols, rows = get_dimensions(cell_names)
    
    if formatted_string is None:
        new_interconnection = generate_string(cols, rows, adjacent)
    else:
        new_interconnection = formatted_string
    
    new_circuit, new_last_node = interconnection(new_interconnection, cols, rows, intensity_array)
    
    return new_circuit, new_last_node, new_interconnection

    
#%%    

class solar_module(SubCircuit):
    __nodes__ = ('t_in', 't_out')
    
    def __init__(self, name, partition_list, intensity_array):
        
        SubCircuit.__init__(self, name, *self.__nodes__)
        
        self.partition_list = partition_list
        self.intensity_array = intensity_array
        
        block_name = 65
        blocks_and_connections = {}
        
        for block in partition_list:
            blocks_and_connections[chr(block_name)] = make_block(block, intensity_array)
            self.__dict__[chr(block_name)] = blocks_and_connections[chr(block_name)]
            block_name += 1
        
        self.blocks_and_connections = blocks_and_connections
        self.blocks = list(self.blocks_and_connections.keys())
        
        circuits = [x[0] for x in self.blocks_and_connections.values()]
        output_nodes = [x[1] for x in self.blocks_and_connections.values()]
        formatted_strings = [x[2] for x in self.blocks_and_connections.values()]
        
        self.circuits = circuits # TODO: update self.blocks, circuits, output_nodes and formatted_strings automatically
        self.output_nodes = output_nodes
        self.formatted_strings = formatted_strings

    def change_connection(self, block, formatted_string = None, adjacent = False):
        
        element_names = list(self.blocks_and_connections[block][0].element_names)
        cell_names = []
        for cell in element_names:
            cell_names.append(cell[1] + cell[2])
            
        ## use generate_string to change interconnection
        cols, rows = get_dimensions(cell_names)
        
        if formatted_string is None:
            if adjacent is False:
                new_interconnection = generate_string(cols, rows)
            elif adjacent is True:
                new_interconnection = generate_string(cols, rows, adjacent = True)
        else:
            new_interconnection = formatted_string
        
        new_circuit, new_last_node = interconnection(new_interconnection, cols, rows, intensity_array)
        
        self.blocks_and_connections[block] = (new_circuit, new_last_node, new_interconnection)
        self.__dict__[block] = (new_circuit, new_last_node, new_interconnection)
    
    def change_all_connections(self):
        blocks = self.blocks
        for block in blocks:
            self.change_connection(block)
        
        
# TODO: connect blocks together in series or parallel

intensity_array = np.full((5,5), 10)
partition = [['00', '01', '02', '03', '10', '11', '12', '13'],
 ['20', '21', '30', '31', '40', '41'],
 ['22', '23', '32', '33', '42', '43'],
 ['04', '14', '24', '34', '44']]
plot_partition(partition)
panel = solar_module('test', partition, intensity_array)
panel.change_connection('A')
#panel.change_all_connections()

#%% testing for make_block and change_cell_interconnection function
"""
partition = partition_grid(5, 5, 4)
plot_partition(partition)
intensity_array = np.full((5,5), 10)
circuit, output_node, connection = make_block(partition[0], intensity_array)
print(circuit)
new_circuit, new_output_node, new_interconnection = change_cell_interconnection(circuit, intensity_array)
print(new_circuit)
print(new_interconnection)
"""
