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
import random
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
    
    def __init__(self, name, columns, rows, partition_list, intensity_array, panel_string = None):
        
        SubCircuit.__init__(self, name, *self.__nodes__)
        
        self.columns = columns
        self.rows = rows
        
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
        
        if panel_string is None:
            self.generate_module_string()
        else:
            self.module_string = panel_string
        
        self.block_interconnection()
 
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
            
    def generate_module_string(self): # based off generate_string
        
        block_list = self.blocks.copy()
        
        random.shuffle(block_list)
        
        l_bracket = '('
        r_bracket = ')'
        
        maximum_brackets = len(block_list) / 2
        number_of_brackets = random.randint(0, maximum_brackets)
        for x in range(0, number_of_brackets):
            if x == 0:
                inserting_index = random.randint(0, len(block_list) - 2)
                block_list.insert(inserting_index, l_bracket)
                rb_inserting_index = random.randint(inserting_index + 3, len(block_list))
                block_list.insert(rb_inserting_index, r_bracket)
            else:
                inserting_index = random.randint(rb_inserting_index + 1, len(block_list) - 2)
                block_list.insert(inserting_index, l_bracket)
                rb_inserting_index = random.randint(inserting_index + 3, len(block_list))
                block_list.insert(rb_inserting_index, r_bracket)
            
            sliced_block_list = block_list[rb_inserting_index + 1:]
            if len(sliced_block_list) < 2:
                break
        
        pm = '+-'
        
        maximum_pms = len(self.blocks)
        
        number_of_pms = random.randint(0, maximum_pms)
        
        for x in range(0, number_of_pms):
            random_index = random.randint(0, len(block_list))
            sliced_cell_ids = block_list[:random_index]
            number_of_l_brackets = sliced_cell_ids.count(l_bracket)
            number_of_r_brackets = sliced_cell_ids.count(r_bracket)
            if number_of_l_brackets == number_of_r_brackets:
                block_list.insert(random_index, pm)
                
        block_list.insert(0, '-')
        block_list.append('+')
        
        self.module_string = "".join(block_list)        
    
    def block_interconnection(self):
        panel_string = self.module_string
        
        char_list = [x for x in panel_string]
        
        preceding_char = ''
        
        output_list = []
        for char in char_list:
            if char == '-':
                preceding_char = '-'
                output_list.append(char)
            elif char == '+':
                pass
            elif char in self.blocks:
                current_block_string = getattr(self, char)[2]
                current_block_string = current_block_string.lstrip('-')
                current_block_string = current_block_string.rstrip('+')
                output_list.append(current_block_string)
        
        output_str = "".join(output_list)
        new_circuit, output_node = interconnection(output_str, self.columns, self.rows, self.intensity_array)
        
        self.circuit = new_circuit
        self.output_node = output_node
            
# TODO: connect blocks together in series or parallel

intensity_array = np.full((5,5), 10)
partition = [['00', '01', '02', '03', '10', '11', '12', '13'],
 ['20', '21', '30', '31', '40', '41'],
 ['22', '23', '32', '33', '42', '43'],
 ['04', '14', '24', '34', '44']]
plt.figure(0)
plot_partition(partition)
panel = solar_module('test', 5, 5, partition, intensity_array)
#panel.change_connection('A')
#panel.change_all_connections()

#%%  
"""
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
"""