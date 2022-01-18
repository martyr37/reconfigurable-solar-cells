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
#%% get_dimenions
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

#%% make_block makes an all series connection of each block
def make_block(block, intensity_array): 
    
    number_of_columns, number_of_rows = get_dimensions(block)
    
    block_string = "".join(block)
    block_string = "-" + block_string + "+"
    
    circuit, last_node = interconnection(block_string, number_of_columns, number_of_rows, intensity_array)

    return circuit, last_node, block_string    

#%% solar_module class
class solar_module(SubCircuit):
    __nodes__ = ('t_in', 't_out')
    
    def __init__(self, name, partition_list, intensity_array):
        
        SubCircuit.__init__(self, name, *self.__nodes__)
        
        self.partition_list = partition_list
        self.intensity_array = intensity_array
        
        block_name = 65
        blocks_and_connections = {}
        
        for block in partition_list:
            blocks_and_connections[chr(block_name)] = make_block(block, intensity_array) # intra-cell connections
            self.__dict__[chr(block_name)] = blocks_and_connections[chr(block_name)]
            block_name += 1
        
        self.blocks_and_connections = blocks_and_connections
        self._blocks = list(self.blocks_and_connections.keys())
        
        circuits = [x[0] for x in self.blocks_and_connections.values()]
        output_nodes = [x[1] for x in self.blocks_and_connections.values()]
        formatted_strings = [x[2] for x in self.blocks_and_connections.values()]
        
        self._circuits = circuits
        self._output_nodes = output_nodes
        self._formatted_strings = formatted_strings
        
        self.circuit = Circuit('Block Module')        
        
    @property
    def blocks(self):
        self._blocks = list(self.blocks_and_connections.keys())
        return self._blocks
    
    @property
    def circuits(self):
        self._circuits = [x[0] for x in self.blocks_and_connections.values()]
        return self._circuits
    
    @property
    def output_nodes(self):
        self._output_nodes = [x[1] for x in self.blocks_and_connections.values()]
        return self._output_nodes
    
    @property
    def formatted_strings(self):
        self._formatted_strings = [x[2] for x in self.blocks_and_connections.values()]
        return self._formatted_strings 

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
            
    def block_interconnection(self, formatted_string = None):
            
        if formatted_string is None: # all series connection between blocks
            formatted_string = '-' + "".join(self.blocks) + '+'
            
        in_brackets = False
        preceding_node = ''
        
        char_list = [x for x in formatted_string]
        output_nodes = []
        
        for current_char in char_list:
            if in_brackets is False:
                if current_char == '-':
                    preceding_node = '-'
                elif current_char == '+':
                    output_nodes.append(preceding_node) # add to output_nodes the name of the last node
                    preceding_node = '+'
                else:
                    if preceding_node == '-':
                        getattr(self, current_char)[0].copy_to(self.circuit)
                    else:
                        getattr(self, current_char)[0].copy_to(self.circuit)
            
# TODO: connect blocks together in series or parallel

intensity_array = np.full((5,5), 10)
partition = [['00', '01', '02', '03', '10', '11', '12', '13'],
 ['20', '21', '30', '31', '40', '41'],
 ['22', '23', '32', '33', '42', '43'],
 ['04', '14', '24', '34', '44']]
plt.figure(0)
plot_partition(partition)
panel = solar_module('test', partition, intensity_array)
#panel.change_connection('A')
#panel.change_all_connections()

#%%  
class solar_block(SubCircuit):
    __nodes__ = ('block_in', 'block_out')
    
    def __init__(self, name, input_circuit):
        SubCircuit.__init__(self, name, *self.__nodes__)
        input_circuit.copy_to(self)
        self.R('-', 'block_in', self.gnd, 0) # block_in is the same as block "ground"
        
        last_node = list(input_circuit.node_names)[-1]
        self.R('+', 'block_out', last_node, 0) # block_out is the output node of the block
        
block_A = solar_block('A', panel.A[0])
block_B = solar_block('B', panel.B[0])
circuit = Circuit('test')
circuit.subcircuit(block_A)
circuit.subcircuit(block_B)
circuit.X('A_blck', 'A', circuit.gnd, 1)
circuit.X('B_blck', 'B', 1, 2)
circuit.V('output', circuit.gnd, 2, 0)
print(circuit)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Voutput=slice(0, 10, 0.01))
plt.figure(1)
plt.plot(np.array(analysis.sweep), np.array(analysis.Voutput))
plt.ylim(0, 20)