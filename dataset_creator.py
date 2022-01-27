#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 16:23:38 2022

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
from solar_module import solar_module

from timeit import default_timer as timer
####################################################################################################


#%% 1000 static random shading maps
PARTITION_ITERATIONS = 10
BLOCK_ITERATIONS = 10
CELL_ITERATIONS = 10
NUMBER_OF_BLOCKS = 4
ADJACENCY = False

#shading_map = random_shading(10, 6, 0.6, 0.3)
shading_map = np.array([[ 9.4742303,  8.5130091,  9.0097782, 10.       ,  2.2051557,
         9.8594214],
       [ 2.       ,  7.2851699,  2.       ,  8.3885022,  2.       ,
         5.8681359],
       [ 5.4146223,  2.       ,  6.1911822, 10.       ,  7.4924369,
         3.7785194],
       [ 5.9212888,  2.       , 10.       ,  3.887803 , 10.       ,
         2.       ],
       [ 5.4473682, 10.       ,  4.2143121,  4.9051392,  5.6402594,
         8.7597521],
       [ 9.3852263,  6.1126854,  5.7047751,  7.1600714,  4.8632554,
         7.8609917],
       [ 7.4808069,  7.5640434,  4.2641627,  6.0818833, 10.       ,
        10.       ],
       [ 4.9132147,  5.6187117,  9.35946  ,  2.       ,  4.5713966,
         4.4256315],
       [ 2.5777461,  8.2521419, 10.       ,  4.4512831,  4.9305791,
         9.5587955],
       [ 6.3195871,  4.0262248,  2.       ,  9.2115397, 10.       ,
        10.       ]])

def make_panel(shading_map, no_of_blocks, adjacent = False):
    rows, columns = np.shape(shading_map)
    
    partition = partition_grid(columns, rows, no_of_blocks)
    
    panel = solar_module(str(rows) + " by " + str(columns) + "panel", columns, rows, partition, shading_map)
    
    return panel

data_list = []
start = timer()
for index in range(0, PARTITION_ITERATIONS):
    panel = make_panel(shading_map, NUMBER_OF_BLOCKS, adjacent = ADJACENCY)
    if len(panel.blocks) != NUMBER_OF_BLOCKS:
        continue
    
    partition = panel.partition_list
    
    for index in range(0, BLOCK_ITERATIONS):
        panel_string = panel.module_string
        
    
        for cell_connection in range(0, CELL_ITERATIONS):
            cell_strings = panel.formatted_strings
            circuit = panel.circuit
            last_node = panel.output_node
            circuit.V('output', circuit.gnd, last_node, 99)
            simulator = circuit.simulator(temperature=25, nominal_temperature=25)
            analysis = simulator.dc(Voutput=slice(0, 50, 0.1))
            
            
            power = np.array(analysis.sweep) * np.array(analysis.Voutput)
            mpp = power.max()
            vmp = analysis.sweep[power.argmax()]
            imp = analysis.Voutput[power.argmax()]
            
            data_list.append([partition, panel_string, cell_strings, mpp, vmp, imp])
            #plt.plot(np.array(analysis.sweep), power)
            #plt.xlim(0, 100)
            #plt.ylim(0, 100)
            
            panel.change_all_connections()
        
        panel.generate_module_string()
        panel.block_interconnection()
        
end = timer()
df = pd.DataFrame(data = data_list, columns = ["Partition List", "Module String", "Cell Strings", "MPP (W)", "VMP (V)",\
                                             "IMP (A)"])
df.sort_values("MPP (W)", ascending = False, inplace = True) # might be slowing program down
print(df["MPP (W)"])
print("Execution took", end - start, "seconds")
#%%
with pd.ExcelWriter('dataset.xlsx') as writer:
    df.to_excel(writer, sheet_name="Panel configurations")
