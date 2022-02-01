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
#%%
def make_panel(shading_map, no_of_blocks, adjacent = False):
    rows, columns = np.shape(shading_map)
    
    partition = partition_grid(columns, rows, no_of_blocks)
    
    panel = solar_module(str(rows) + " by " + str(columns) + "panel", columns, rows, partition, shading_map)
    
    return panel

#%% 1000 static random cell and block configurations
PARTITION_ITERATIONS = 10
BLOCK_ITERATIONS = 10
CELL_ITERATIONS = 10
NUMBER_OF_BLOCKS = 6
ADJACENCY = False
#%%
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
data_list = []
start = timer()
for i in range(0, PARTITION_ITERATIONS):
    panel = make_panel(shading_map, NUMBER_OF_BLOCKS, adjacent = ADJACENCY)
    if len(panel.blocks) != NUMBER_OF_BLOCKS:
        continue
    
    partition = panel.partition_list
    
    for j in range(0, BLOCK_ITERATIONS):
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
df.sort_values("MPP (W)", ascending = False, inplace = True)
print(df["MPP (W)"])
print("Execution took", end - start, "seconds")

with pd.ExcelWriter('dataset1.xlsx') as writer:
    df.to_excel(writer, sheet_name="Panel configurations")

#%% use multiple shading maps (3) to aggregate performance
map1 = 10 * random_shading(10, 6, 0.6, 0.3)
map2 = 10 * block_shading(10, 6, np.array([0.7, 0.3, 0.6, 0.4]))
map3 = 10 * checkerboard_shading(10, 6, np.array([0.5, 0.55, 0.6]))

data_list = []
start = timer()
for i in range(0, PARTITION_ITERATIONS):
    partition = partition_grid(6, 10, NUMBER_OF_BLOCKS)
    if len(partition) != NUMBER_OF_BLOCKS: # partition creating excess blocks
        continue
    panel1 = solar_module("Panel 1", 6, 10, partition, map1)
    
    for j in range(0, BLOCK_ITERATIONS):
        module_string = panel1.module_string
        for k in range(0, CELL_ITERATIONS):
            panel1.change_all_connections()
            cell_strings = panel1.formatted_strings
            panel2 = solar_module("Panel 2", 6, 10, partition, map2, module_string)
            panel3 = solar_module("Panel 3", 6, 10, partition, map3, module_string)
            block_letters = ['A', 'B', 'C', 'D', 'E', 'F']
            for block in range(0, NUMBER_OF_BLOCKS):
                panel2.change_connection(block_letters[block], formatted_string = cell_strings[block])
                panel3.change_connection(block_letters[block], formatted_string = cell_strings[block])
            
            last_node = panel1.output_node
            circuit1 = panel1.circuit
            circuit2 = panel2.circuit
            circuit3 = panel3.circuit
            circuit1.V('output', circuit1.gnd, last_node, 99)
            circuit2.V('output', circuit1.gnd, last_node, 99)
            circuit3.V('output', circuit1.gnd, last_node, 99)
            simulator1 = circuit1.simulator(temperature=25, nominal_temperature=25)
            simulator2 = circuit2.simulator(temperature=25, nominal_temperature=25)
            simulator3 = circuit3.simulator(temperature=25, nominal_temperature=25)
            analysis1 = simulator1.dc(Voutput=slice(0, 50, 0.1))
            analysis2 = simulator2.dc(Voutput=slice(0, 50, 0.1))
            analysis3 = simulator3.dc(Voutput=slice(0, 50, 0.1))
            
            power1 = np.array(analysis1.sweep) * np.array(analysis1.Voutput)
            power2 = np.array(analysis2.sweep) * np.array(analysis2.Voutput)
            power3 = np.array(analysis3.sweep) * np.array(analysis3.Voutput)
            mpp1 = power1.max()
            mpp2 = power2.max()
            mpp3 = power3.max()
            mpp_total = mpp1 + mpp2 + mpp3
            vmp1 = analysis1.sweep[power1.argmax()]
            vmp2 = analysis2.sweep[power2.argmax()]
            vmp3 = analysis3.sweep[power3.argmax()]
            imp1 = analysis1.Voutput[power1.argmax()]
            imp2 = analysis2.Voutput[power2.argmax()]
            imp3 = analysis3.Voutput[power3.argmax()]
            
            data_list.append([partition, module_string, cell_strings, mpp_total, mpp1, mpp2, mpp3])
            
            # get data
            
        panel1.generate_module_string()
        panel1.block_interconnection()
end = timer()
df = pd.DataFrame(data = data_list, columns = ["Partition List", "Module String", "Cell Strings",\
                                               "Total MPP (W)", "MPP1", "MPP2", "MPP3"])
df.sort_values("Total MPP (W)", ascending = False, inplace = True)
print(df[df.columns[3:7]])
print("Execution took", end - start, "seconds")
with pd.ExcelWriter('dataset2.xlsx') as writer:
    df.to_excel(writer, sheet_name="Panel configurations")