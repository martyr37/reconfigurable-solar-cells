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

import random
import warnings
####################################################################################################

## assuming cell IDs are always two characters, e.g. 23, 10, etc.
#%% interconnection function (use PySpice to build circuits)
def interconnection(formatted_string, columns, rows, intensity_array):
    global node_counter
    global circuit
    node_counter = 97 # refers to 'a'
    
    circuit = Circuit('Module')
    for row in range(0, rows):
        for column in range(0, columns):
            circuit.subcircuit(solar_cell(str(row) + str(column), intensity=intensity_array[row,column]))
    
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
        for index in range(0, len(output_nodes) - 1): # join nodes that are meant to be the same output node
            circuit.R('wire' + str(index), output_nodes[index], output_nodes[index + 1], 0)
    
    return circuit, preceding_node
#%% interconnection tests (hand-drawn interconnections as on 15/12/21)
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
#circuit, output_node = interconnection('-0001+-1011+', 2, 2, uniform_shading(2,2,current=10))
"""
circuit.V('output', circuit.gnd, output_node, 99)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Voutput=slice(0,10,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Voutput))
plt.xlim(left=0)
plt.ylim(bottom=0, top=50)
"""
#print(circuit)
#print(output_node)
#%% check_adjacency function (adjacency parameter for generate_string)
def check_adjacency(cell_ids):
    for index in range(0, len(cell_ids)):
        current_cell = cell_ids[index]
        current_row_number = int(current_cell[0])
        current_column_number = int(current_cell[1])
        
        if index != 0:
            if abs(current_row_number - previous_row_number) >= 2 or abs(current_column_number - previous_column_number) >= 2:
                return False

        previous_row_number = int(current_cell[0])
        previous_column_number = int(current_cell[1])
    return True
#%% generate_string function (generate interconnection strings)
def generate_string(columns, rows, adjacent = False):
    cell_ids = []
    for row in range(0, rows):
        for column in range(0, columns):
            cell_ids.append(str(row) + str(column))
    
    l_bracket = '('
    r_bracket = ')'
    
    if adjacent == False:
        random.shuffle(cell_ids) # shuffle cell order
    elif adjacent == True:
        is_adjacent = check_adjacency(cell_ids)
        while is_adjacent == False:
            random.shuffle(cell_ids) # reshuffle cell order if non-adjacent
            is_adjacent = check_adjacency(cell_ids)
            
    maximum_brackets = int((columns * rows) / 2)
    number_of_brackets = random.randint(0, maximum_brackets) 
    for x in range(0, number_of_brackets):
        if x == 0:
            inserting_index = random.randint(0, len(cell_ids) - 2)
            cell_ids.insert(inserting_index, l_bracket)
            rb_inserting_index = random.randint(inserting_index + 3, len(cell_ids))
            cell_ids.insert(rb_inserting_index, r_bracket)
        else:
            inserting_index = random.randint(rb_inserting_index + 1, len(cell_ids) - 2) # ensuring next set of brackets is after the last
            cell_ids.insert(inserting_index, l_bracket)
            rb_inserting_index = random.randint(inserting_index + 3, len(cell_ids))
            cell_ids.insert(rb_inserting_index, r_bracket) 
        
        sliced_cell_ids = cell_ids[rb_inserting_index + 1:]
        if len(sliced_cell_ids) < 2:
            break
        
    pm = '+-'
    
    maximum_pms = max(columns, rows) - 1
    
    number_of_pms = random.randint(0, maximum_pms)
    
    for x in range(0, number_of_pms):
        random_index = random.randint(0, len(cell_ids))
        sliced_cell_ids = cell_ids[:random_index]
        number_of_l_brackets = sliced_cell_ids.count(l_bracket)
        number_of_r_brackets = sliced_cell_ids.count(r_bracket)
        if number_of_l_brackets == number_of_r_brackets:
            cell_ids.insert(random_index, pm)
    """
    pattern1 = re.compile(r'\(.*(\+-).*\)') # disregard any configurations with +- inside ()
    pattern2 = re.compile(r'\((.*\(.*)+.*\)') # disregard nested brackets
    
    if re.search(pattern2, "".join(cell_ids)):
        return None
    """
    
    cell_ids.insert(0, '-')
    cell_ids.append('+')
    """
    try:
        interconnection("".join(cell_ids), columns, rows, uniform_shading(rows, columns))
        return "".join(cell_ids)
    except:
        generate_string(columns, rows)
    """
    return "".join(cell_ids)
#%% check rectangle
def is_rectangular(list_of_cells):
    list_of_cells.sort()
    row_coords = set()
    column_coords = set()
    for cell in list_of_cells:
        row = int(cell[0])
        column = int(cell[1])
        row_coords.add(row)
        column_coords.add(column)
    
    number_of_points = len(row_coords) * len(column_coords)
    
    if len(list_of_cells) != number_of_points:
        return False
    else:
        return True
    
#%% partition grid 
def partition_grid(columns, rows, number_of_rectangles):
    cell_ids = []
    for row in range(0, rows):
        for column in range(0, columns):
            cell_ids.append(str(row) + str(column))
    
    grid = np.array(cell_ids).reshape(rows, columns)

    grid_list = []
    while len(grid_list) < number_of_rectangles:
        
        edge_choice = random.randint(0, 1)
        
        if edge_choice == 0:
            
            vertical_line = random.randint(1, columns - 1)
            vertical_stop = random.randint(1, rows)
            
            if grid_list == []:
                slice1 = grid[:, :vertical_line]
                slice2 = grid[:, vertical_line:]
            else:
                slice1 = grid[:vertical_stop, :vertical_line]
                slice2 = grid[vertical_stop:, vertical_line:]
            
            if slice1.flatten().tolist() in grid_list or slice2.flatten().tolist() in grid_list:
                continue
            
            if grid_list == []:
                grid_list.append(slice1.flatten().tolist())
                grid_list.append(slice2.flatten().tolist())
            else:
                old_grid_list = grid_list.copy()
                new_rectangle = slice1.flatten().tolist()
                grid_list.insert(0, new_rectangle)
                for index in range(1, len(grid_list)):
                    for cell in new_rectangle:
                        if cell in grid_list[index]:
                            grid_list[index].remove(cell)

        elif edge_choice == 1:
            horizontal_line = random.randint(1, rows - 1)
            horizontal_stop = random.randint(1, columns)
            if grid_list == []:
                slice1 = grid[:horizontal_line]
                slice2 = grid[horizontal_line:]
            else:
                slice1 = grid[:horizontal_line, :horizontal_stop]
                slice2 = grid[horizontal_line:, horizontal_stop:]
            
            if slice1.flatten().tolist() in grid_list or slice2.flatten().tolist() in grid_list:
                continue
            
            if grid_list == []:
                grid_list.append(slice1.flatten().tolist())
                grid_list.append(slice2.flatten().tolist())
            else:
                old_grid_list = grid_list.copy()
                new_rectangle = slice1.flatten().tolist()
                grid_list.insert(0, new_rectangle)
                for index in range(1, len(grid_list)):
                    for cell in new_rectangle:
                        if cell in grid_list[index]:
                            grid_list[index].remove(cell)
        
        if [] in grid_list: # no new rectangle was made
            grid_list = [x for x in grid_list if x != []] # remove [] from grid_list
            continue
        elif all(map(is_rectangular, grid_list)) is False: # if new partition is invalid
            grid_list = old_grid_list.copy() # revert grid_list to previous state
            continue
        flattened_grid_list = [item for l in grid_list for item in l]
        if len(flattened_grid_list) != columns * rows:
            cells_in_grid = grid.flatten().tolist()
            remaining_cells = [x for x in cells_in_grid if x not in flattened_grid_list]
            if is_rectangular(remaining_cells) is False:
                grid_list = old_grid_list.copy()
                continue
            elif is_rectangular(remaining_cells) is True:
                grid_list.append(remaining_cells)
     
    if len(grid_list) > number_of_rectangles:
        warnings.warn("\nWARNING: Partition generated contains more rectangles than specified.")
    return grid_list
    # returns a list of tuples, each tuple containing the cell_ids in that rectangle

def plot_partition(grid_list):
    for l in grid_list:
        rectangle_plot = []
        for cell in l:
            ycoord = -int(cell[0])
            xcoord = int(cell[1])
            rectangle_plot.append((xcoord, ycoord))
        plt.scatter(*zip(*rectangle_plot)) 
