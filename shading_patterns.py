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

def uniform_shading(rows, columns, current=10):
    return np.full((rows, columns), current)
    
#%% 4-variable
def segmented_shading(rows, columns, current_list):
    # current_list is a one-dimensional array cnotaining the intensities in each segment
    # e.g. [10, 7, 2, 6]
    
    # for now, assuming that it will always be split into 4 sections 
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

current_list = np.array([10, 9, 8, 7])
print(segmented_shading(6, 4, current_list))
    
#%%


