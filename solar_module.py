#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 14:28:27 2022

@author: mlima
"""

#TODO: make each block a subcircuit
#TODO: allow changing of interconnection inside each block 

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
def make_block(block, intensity_array):
    row_coords = set()
    column_coords = set()
    for cell in block:
        row = int(cell[0])
        column = int(cell[1])
        row_coords.add(row)
        column_coords.add(column)
    
    number_of_columns = len(column_coords)
    number_of_rows = len(row_coords)
    
    block_string = "".join(block)
    block_string = "-" + block_string + "+"

    circuit, last_node = interconnection(block_string, number_of_columns, number_of_rows, sliced_shading_map)
    
    return circuit, last_node
    

class solar_module(SubCircuit):
    __nodes__ = ('t_in', 't_out')
    
    def __init__(self, name, partition_list, intensity_array):
        
        SubCircuit.__init__(self, name, *self.__nodes__)
    
    def change_cell_interconnection(formatted_string):
        pass
     
    
partition = partition_grid(5, 5, 4)
plot_partition(partition)
circuit, output_node = make_block(partition[0], np.full((5, 5), 10))
print(circuit)