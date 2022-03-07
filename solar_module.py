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
import string
import regex as re

from timeit import default_timer as timer
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

#%%
def get_top_left_coord(l):
    row_coords = set()
    column_coords = set()
    for cell in l:
        row = int(cell[0])
        column = int(cell[1])
        row_coords.add(row)
        column_coords.add(column)
    lowest_column = min(column_coords)
    lowest_row = min(row_coords)
    return lowest_column, lowest_row

#%% make_block makes an all series connection of each block
def make_block(block, intensity_array): 
    
    number_of_columns, number_of_rows = get_dimensions(block)
    
    block_string = "".join(block)
    block_string = "-" + block_string + "+"
    
    circuit, last_node = interconnection(block_string, number_of_columns, number_of_rows, intensity_array)

    return circuit, last_node, block_string    

#%% solar_module class
class solar_module():
    #__nodes__ = ('t_in', 't_out')
    node_names = list(string.ascii_lowercase)
    node_names.extend([str(x) + str(x) for x in string.ascii_lowercase])
    node_names.extend([str(x) + str(x) + str(x) for x in string.ascii_lowercase])
    node_names.insert(0, '')
    
    def __init__(self, name, columns, rows, partition_list, intensity_array, panel_string = None):
        
        #SubCircuit.__init__(self, name, *self.__nodes__)
        
        self.name = name
        
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
            if cell[0] == 'X':
                cell_names.append(cell[1] + cell[2])
            
        ## use generate_string to change interconnection
        cols, rows = get_dimensions(cell_names)
        l_col, l_row = get_top_left_coord(cell_names)
        
        if formatted_string is None:
            if adjacent is False:
                new_interconnection = generate_string(cols, rows, start_col = l_col, start_row = l_row)
            elif adjacent is True:
                new_interconnection = generate_string(cols, rows, adjacent = True, start_col = l_col, start_row = l_row)
        else:
            new_interconnection = formatted_string
        
        new_circuit, new_last_node = interconnection(new_interconnection, cols, rows, self.intensity_array)
        
        self.blocks_and_connections[block] = (new_circuit, new_last_node, new_interconnection)
        self.__dict__[block] = (new_circuit, new_last_node, new_interconnection)
        
        self.block_interconnection()

    def change_all_connections(self, adjacent = False):
        blocks = self.blocks
        for block in blocks:
            if adjacent is False:
                self.change_connection(block)
            elif adjacent is True:
                self.change_connection(block, adjacent = True)
            
    def generate_module_string(self): # based off generate_string
        
        block_list = self.blocks.copy()
        
        random.shuffle(block_list)
        
        l_bracket = '('
        r_bracket = ')'
        
        maximum_brackets = int(len(block_list) / 2) # TODO: Change to variable
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
        
        maximum_pms = int(len(self.blocks) / 2) # TODO: Change to variable
        
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
        
        module_string = "".join(block_list)
        
        pattern1 = re.compile(r'(?<=^-)(?:\+-)+(?=.*$)')
        pattern2 = re.compile(r'(?<=^-.*)(?:\+-)+(?=\+$)')
        pattern3 = re.compile(r'(\+-)+(?=(\+-)+)')
        module_string = re.sub(pattern1, '', module_string)
        module_string = re.sub(pattern2, '', module_string)
        module_string = re.sub(pattern3, '', module_string)
        self.module_string = module_string
    
    def block_interconnection(self):        
        panel_string = self.module_string
        in_brackets = False
        
        output_list = []
        output_nodes = []
        isolated_nodes = []
        
        char_list = [x for x in panel_string]
        
        new_circuit = Circuit('Module')
        
        intermediate_node = 0
        
        wire_no = 0
        
        end_of_block = '' # '' is before the alphabet list in node_names
        
        for char in char_list:
            if in_brackets is False:
                if char == '-':
                    intermediate_node = 0
                    output_list.append(char)
                elif char == '(':
                    in_brackets = True
                    if all(element == '-' for element in output_list): # connect in series the preceding letters, if there are any
                        continue
                    intermediate_circuit, intermediate_node = interconnection("".join(output_list), self.columns, self.rows, self.intensity_array,\
                                                                              gnd = intermediate_node, first_node = self.node_names[self.node_names.index(end_of_block) + 1])
                    intermediate_circuit.copy_to(new_circuit)
                    end_of_block = intermediate_node
                    output_list = ['-']
                elif char == '+': # connect in series the preceding letters, if there are any
                    if all(element == '-' for element in output_list):
                        continue
                    output_list.append('+')
                    intermediate_circuit, intermediate_node = interconnection("".join(output_list), self.columns, self.rows, self.intensity_array,\
                                                                              gnd = intermediate_node, first_node = self.node_names[self.node_names.index(end_of_block) + 1])
                    intermediate_circuit.copy_to(new_circuit)
                    isolated_nodes.append(intermediate_node)
                    end_of_block = intermediate_node
                    output_list = ['-']
                elif char in self.blocks: # reading a letter (A, B, C, etc.)
                    current_block_string = getattr(self, char)[2]
                    current_block_string = current_block_string.lstrip('-')
                    current_block_string = current_block_string.rstrip('+')
                    output_list.append(current_block_string)
                    
            elif in_brackets is True and char != ')':
                current_block_string = getattr(self, char)[2]
                intermediate_circuit, end_of_block = interconnection(current_block_string, self.columns, self.rows, self.intensity_array, \
                                                                     gnd = intermediate_node, first_node = self.node_names[self.node_names.index(end_of_block) + 1])
                intermediate_circuit.copy_to(new_circuit)
                output_nodes.append(end_of_block)
            elif in_brackets is True and char == ')':
                in_brackets = False
                intermediate_node = end_of_block
                for index in range(0, len(output_nodes) - 1): # join nodes that are meant to be the same output node
                    new_circuit.R('line' + str(wire_no), output_nodes[index], output_nodes[index + 1], 0)
                    wire_no += 1
                output_nodes = []
        
        if len(isolated_nodes) >= 2:
            for index in range(0, len(isolated_nodes) - 1):
                new_circuit.R('iso' + str(wire_no), isolated_nodes[index], isolated_nodes[index + 1], 0)
                wire_no += 1
    
        self.circuit = new_circuit
        self.output_node = list(new_circuit.node_names)[-1]
    
    def make_super_string(self):
        super_string = ''
        for char in self.module_string:
            if char == '-':
                super_string += '-'
            elif char == '(':
                in_brackets = True
                super_string += '{'
            elif char == ')':
                super_string += '}'
                in_brackets = False
            elif char.isupper() is True:
                super_string += '['
                block_string = getattr(self, char)[2]
                #block_string = block_string.lstrip('-')
                #block_string = block_string.rstrip('+')
                super_string += block_string
                super_string += ']'
            elif char == '+':
                super_string += '+'
        super_string = super_string.lstrip('-')
        super_string = super_string.rstrip('+')
        return super_string

#%% make partition list based off block strings
def make_partition_list(block_strings):
    partition_list = []
    for block in block_strings:
        partition = []
        read_state = False
        cell = ''
        for char in block:
            if char.isdigit() is True and read_state is False:
                read_state = True
                cell += char
            elif char.isdigit() is True and read_state is True:
                read_state = False
                cell += char
                partition.append(cell)
                cell = ''
        partition.sort()
        partition_list.append(partition)
    return partition_list
                
#print(make_partition_list(['-83+', '-727473+', '-(8171)+', '-10+-0020+-(4030)+', '-(5352)+', '-(51506160)+', '-75+', '-(9282)+', '-95+', '-041424(4434)+', '-(6362)+', '-85+', '-(051525)+', '-321223111303(312233414342210201)+', '-(65553545)+', '-93+', '-(5464)+', '-(8494)+', '-8070+', '-9190+']))
#%% super_string to solar_module object
def super_to_module(super_string, columns, rows, intensity_array):
    block_strings = []
    block_letters = []
    block_names = list(string.ascii_uppercase)
    interim_string = ''
    in_square_brackets = False
    for char in super_string:
        if char == '[':
            in_square_brackets = True
        elif char == ']':
            in_square_brackets = False
            block_letters.append(block_names.pop(0))
            block_strings.append(interim_string)
            interim_string = ''
        elif in_square_brackets is True:
            interim_string += char
        elif (char == '+' or char == '-') and in_square_brackets is False:
            block_letters.append(char)
        elif char == '{' and in_square_brackets is False:
            block_letters.append('{')
        elif char == '}' and in_square_brackets is False:
            block_letters.append('}')
            
    module_string = "".join(block_letters)
    module_string = module_string.replace('{', '(')
    module_string = module_string.replace('}', ')')
    module_string = '-' + module_string + '+'
    
    module_object = solar_module("Module", columns, rows, make_partition_list(block_strings),\
                                 intensity_array, panel_string = module_string)
    
    for x in range(0, len(block_strings)):
        letter = string.ascii_uppercase[x]
        module_object.change_connection(letter, formatted_string=block_strings[x])
    
    return module_object
#print(super_to_module('[-63+][-7262+][-95+][-65+][-73+]{[-64+][-74+]}+-[-5452+-(505153)+][-04131121030022143441421210332444320240200123303143+][-9293+][-75+]+-[-9484+]+-[-91+]{[-83+][-807061608171+][-85+][-450525(3515)+][-90+][-55+][-82+]}', 6, 10, np.full((10, 6), 10)))
#%% solar_module testing
"""
#intensity_array = np.full((5,5), 10)
intensity_array = 10 * random_shading(10, 6, 0.6, 0.3)
#intensity_array = np.array([[ 3.85077183,  3.47404535,  2.14447809,  8.08367472,  6.06844605],
#       [ 8.10586786,  9.04505209,  4.18749092,  5.17228197,  7.54703278],
#       [ 2.30814686,  5.0450831 ,  4.94938548,  6.25303969,  2.        ],
#       [10.        ,  7.09460595,  9.04410613,  8.14184236,  2.        ],
#       [ 6.06391736,  6.61745045,  5.99851596,  5.2649692 ,  6.50901227]])

#partition = [['00', '01', '02', '03', '10', '11', '12', '13'],
# ['20', '21', '30', '31', '40', '41'],
# ['22', '23', '32', '33', '42', '43'],
# ['04', '14', '24', '34', '44']]

partition = partition_grid(6, 10, 20)
plt.figure(0)
plot_partition(partition)
panel = solar_module('test_panel', 6, 10, partition, intensity_array)
#panel = solar_module('test_panel', 5, 5, partition, intensity_array, panel_string='-ABCD+')
#panel = solar_module('test_panel', 5, 5, partition, intensity_array, panel_string='-A(BC)D+')
#panel = solar_module('test_panel', 5, 5, partition, intensity_array, panel_string='-(AB)CD+')
#panel = solar_module('test_panel', 5, 5, partition, intensity_array, panel_string='-AB(CD)+')
#panel = solar_module('test_panel', 5, 5, partition, intensity_array, panel_string='-(AB)(CD)+')
#panel = solar_module('test_panel', 5, 5, partition, intensity_array, panel_string='-(ADCB)+')

#panel.change_connection('A', adjacent=True)
#panel.change_connection('A')
panel.change_all_connections()

panel.generate_module_string()
panel.block_interconnection()

circuit = panel.circuit
last_node = panel.output_node
circuit.V('output', circuit.gnd, last_node, 99)

print(circuit)
print()
print(panel.module_string)
print()
print(panel.formatted_strings)
print()
print(panel.make_super_string())
print()
recreated_panel = super_to_module(panel.make_super_string(), 6, 10, intensity_array)
print(recreated_panel.module_string)
print()
print(recreated_panel.formatted_strings)
print(recreated_panel.make_super_string() == panel.make_super_string())

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Voutput=slice(0, 30, 0.01))
plt.figure(1)
plt.plot(np.array(analysis.sweep), np.array(analysis.Voutput))
power = np.array(analysis.sweep) * np.array(analysis.Voutput)
plt.plot(np.array(analysis.sweep), power)
plt.xlim(0, 30)
plt.ylim(0, 50)

recreated_circuit = recreated_panel.circuit
recreated_last_node = recreated_panel.output_node
recreated_circuit.V('output', recreated_circuit.gnd, recreated_last_node, 99)

simulator = recreated_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Voutput=slice(0, 30, 0.01))
plt.plot(np.array(analysis.sweep), np.array(analysis.Voutput))
power = np.array(analysis.sweep) * np.array(analysis.Voutput)
plt.plot(np.array(analysis.sweep), power)
plt.xlim(0, 30)
plt.ylim(0, 50)
"""
