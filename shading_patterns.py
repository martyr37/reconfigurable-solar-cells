# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 14:13:20 2021

@author: MarcelLima
"""

####################################################################################################
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

####################################################################################################

#%% Uniform shading

def uniform_shading(rows, columns, current=1):
    return np.full((rows, columns), current)
    
#%% 4-block
def block_shading(rows, columns, current_list):
    # current_list is a one-dimensional array cnotaining the intensities in each block
    # e.g. [10, 7, 2, 6]
    
    # for now, assuming that it will always be split into 4 blocks 
    sqrt_number = int(math.sqrt(current_list.size))
    
    segments = np.resize(current_list,(sqrt_number, sqrt_number))
    
    intensity_array = np.zeros((rows, columns))
    
    for row in range(0, rows):
        for column in range(0, columns):
            if row < rows/2 and column < columns/2:
                intensity_array[row, column] = current_list[0]
            elif row < rows/2 and column >= columns/2:
                intensity_array[row, column] = current_list[1]
            elif row >= rows/2 and column < columns/2:
                intensity_array[row, column] = current_list[2]
            elif row >= rows/2 and column >= columns/2:
                intensity_array[row, column] = current_list[3]
                
    return intensity_array

#foo = np.array([1, 2, 3, 4])
#print(block_shading(12, 4, foo))

#%%
def checkerboard_shading(rows, columns, current_list):
    
    length = int(current_list.size)
    current_list_index = 0
    # current_list is an array containing the non-zero elements read from left to right.
    intensity_array = np.zeros((rows, columns))
    for row in range(0, rows):
        for column in range(0, columns):
            if (row + column) % 2 == 0:
                intensity_array[row, column] = current_list[current_list_index]
                current_list_index += 1
                current_list_index = current_list_index % length
    
    return intensity_array

#foo = np.array([(x/10) for x in range(1, 10, 1)])
#print(checkerboard_shading(12, 12, foo))
                
    
