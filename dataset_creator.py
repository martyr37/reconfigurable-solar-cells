#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 16:23:38 2022

@author: mlima
"""

####################################################################################################
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()
logger.setLevel(logging.CRITICAL)

from solar_cell import *
from flexible_interconnections import interconnection, generate_string, partition_grid, plot_partition
from solar_module import solar_module, super_to_module
from visualisation import plot_panel

from timeit import default_timer as timer
####################################################################################################
#%% Function to make solar_module instance given shading map and number of blocks
def make_panel(shading_map, no_of_blocks, adjacent = False):
    rows, columns = np.shape(shading_map)
    
    partition = partition_grid(columns, rows, no_of_blocks)
    
    panel = solar_module(str(rows) + " by " + str(columns) + "panel", columns, rows, partition, shading_map)
    
    return panel

#%% Generate Gaussian-like shading maps
def generate_gaussian(dots, rows, columns, spread=2, size=1000, diag='r'):
    x_points = [round(np.random.sample()*columns, 2) for x in range(dots)]
    y_points = [-round(np.random.sample()*rows, 2) for x in range(dots)]
    """
    fig, ax = plt.subplots()
    ax.set_xlim(0, columns)
    ax.set_ylim(-rows, 0)
    plt.scatter(x_points, y_points)
    """
    
    cov_matrices = []
    for x in range(dots):
        a = np.random.sample(size=(2,2)) * spread
        if diag == 'r':
            if np.random.randint(0,2) == 0:
                diag = False
            else:
                diag = True
        if diag == False:
            b = np.dot(a, np.transpose(a))
            cov_matrices.append(b)
        elif diag == True:
            a[0][1] = 0
            a[1][0] = 0
            cov_matrices.append(a)
        
    #print(cov_matrices)
    
    sample_array = np.zeros((dots, size, 2))
    for i in range(dots):
        sample = np.random.multivariate_normal((x_points[i], y_points[i]),\
                                                        cov_matrices[i],\
                                                        size=size)
        sample_array[i] = sample
        #xs, ys = sample[:,0], sample[:,1]
        #plt.scatter(xs, ys)    
        
    # Caclulate density
    shading_array = np.zeros((rows, columns))
    sample_array = np.reshape(sample_array, (dots*size, 2))   
    
    for point in sample_array:
        x, y = round(point[0]), -round(point[1])
        if x < 0 or x >= columns:
            continue
        if y < 0 or y >= rows:
            continue
        #print(x, y)
        current = shading_array[y, x]
        shading_array[y, x] = current + 1
    
    #plt.imshow(shading_array)
    #shading_array = shading_array / shading_array.max()
    #shading_array = np.around(shading_array, 2)
    #shading_array[shading_array < 0.5] = 0.5
    shading_array = np.interp(shading_array, \
                              (shading_array.min(), shading_array.max()), \
                              (0, 10))
    shading_array[shading_array > 4] = 4
    shading_array = np.interp(shading_array, \
                              (shading_array.min(), shading_array.max()), \
                              (0, 10))
    
    return shading_array
#%% Function that plots results of dataset creation
def plot_top_x(x, df):
    top_x = df.head(x)
    top_x_superstrings = top_x["SuperString"]
    panel_list = []
    for superstring in top_x_superstrings:
        panel_list.append(super_to_module(superstring, 6, 10, shading_map))
    plot_panel(panel_list, shading_map)

#%% 1000 static random cell and block configurations
PARTITION_ITERATIONS = 10
BLOCK_ITERATIONS = 10
CELL_ITERATIONS = 10
NUMBER_OF_BLOCKS = 5 # change to be an upper limit (say 1, 2, 5, 10, 20(?))
ADJACENCY = False
filename = 'G3'

#%% Set shading map
#shading_map = random_shading(10, 6, 0.6, 0.3)
#shading_map = block_shading(10, 6, np.array([9, 3, 7, 8]))
#shading_map = checkerboard_shading(10, 6, np.array([0.9, 0.95, 0.8, 0.85]))
shading_map = np.full((10,6),10)


#%% Generate Dataset using 1 shading map
start = timer()
data_list = []
panel_list = []
for i in range(0, PARTITION_ITERATIONS):
    print("Starting partition", i)
    number_of_partitions = random.randint(2, NUMBER_OF_BLOCKS)
    panel = make_panel(shading_map, number_of_partitions, adjacent = ADJACENCY)
    while len(panel.blocks) > number_of_partitions:
        panel = make_panel(shading_map, number_of_partitions, adjacent = ADJACENCY)
    
    partition = panel.partition_list
    
    for j in range(0, BLOCK_ITERATIONS):
        panel_string = panel.module_string
        print("Starting block", j)
    
        for cell_connection in range(0, CELL_ITERATIONS):
            cell_strings = panel.formatted_strings
            superstring = panel.make_super_string()
            circuit = panel.circuit
            last_node = panel.output_node
            circuit.V('output', circuit.gnd, last_node, 99)
            simulator = circuit.simulator(temperature=25, nominal_temperature=25)
            analysis = simulator.dc(Voutput=slice(0, 50, 0.1))
            
            power = np.array(analysis.sweep) * np.array(analysis.Voutput)
            mpp = power.max()
            vmp = analysis.sweep[power.argmax()]
            imp = analysis.Voutput[power.argmax()]
            current_values = np.array(analysis.Voutput)
            current_values = current_values[current_values >= 0]
            
            if list(current_values) == []: # in the event there is no light-generated current
                panel.change_all_connections()
                circuit = None
                continue
            
            voc = analysis.sweep[current_values.argmin()]
            isc = analysis.Voutput[0]
            
            data_list.append([partition, superstring, mpp, vmp, imp, voc, isc])
            #plt.plot(np.array(analysis.sweep), power)
            #plt.xlim(0, 100)
            #plt.ylim(0, 100)
            
            panel_list.append(panel)
            
            panel.change_all_connections()
        
        panel.generate_module_string()
        panel.block_interconnection()
        
end = timer()
df = pd.DataFrame(data = data_list, columns = ["Partition List", "SuperString", "MPP (W)", "VMP (V)",\
                                             "IMP (A)", "VOC (V)", "ISC (A)"])

df.sort_values("MPP (W)", ascending = False, inplace = True)
plot_top_x(20, df)

print(df["MPP (W)"])
print("Execution took", end - start, "seconds")

with pd.ExcelWriter("Datasets/" + filename + '.xlsx') as writer:
    df.to_excel(writer, sheet_name=filename)
plt.title(filename)
plt.savefig("Visualisation Plots/" + filename + '.png')

#%% use multiple shading maps (3) to aggregate performance
map1 = np.full((10, 6), 10)
map1[:,:2] = 3
map2 = np.copy(map1)
map3 = np.copy(map1)
map2[:,:4] = 3
map3 = np.triu(np.full((10, 6), 10))
#%%
shading_maps = [map1, map2, map3]
data_list = []
mpp_list = []
vmp_list = []
imp_list = []
voc_list = []
isc_list = []

start = timer()

for i in range(0, PARTITION_ITERATIONS):
    print("Starting partition", i)
    number_of_partitions = random.randint(2, NUMBER_OF_BLOCKS)
    panel = make_panel(shading_map, number_of_partitions, adjacent = ADJACENCY)
    partition = panel.partition_list
    
    for j in range(0, BLOCK_ITERATIONS):
        panel_string = panel.module_string
        print("Starting block", j)
    
        for cell_connection in range(0, CELL_ITERATIONS):
            cell_strings = panel.formatted_strings
            superstring = panel.make_super_string()
            
            average_power = 0
            
            for shading_map in shading_maps:
                panel_instance = super_to_module(superstring, 6, 10, shading_map)
                            
                circuit = panel_instance.circuit
                last_node = panel_instance.output_node
                circuit.V('output', circuit.gnd, last_node, 99)
                simulator = circuit.simulator(temperature=25, nominal_temperature=25)
                analysis = simulator.dc(Voutput=slice(0, 50, 0.1))
                
                power = np.array(analysis.sweep) * np.array(analysis.Voutput)
                mpp = power.max()
                vmp = analysis.sweep[power.argmax()]
                imp = analysis.Voutput[power.argmax()]
                current_values = np.array(analysis.Voutput)
                current_values = current_values[current_values >= 0]
                
                if mpp != 0:
                    voc = analysis.sweep[current_values.argmin()]
                else:
                    voc = 0
                isc = analysis.Voutput[0]
                mpp_list.append(mpp)
                vmp_list.append(vmp)
                imp_list.append(imp)
                voc_list.append(voc)
                isc_list.append(isc)
                
                average_power += mpp
            
            average_power = average_power / len(shading_maps)
            
            data_list.append([partition, superstring, average_power, str(mpp_list),\
                              str(vmp_list), str(imp_list), str(voc_list), str(isc_list)])

            mpp_list = []
            vmp_list = []
            imp_list = []
            voc_list = []
            isc_list = []
            
            panel.change_all_connections()
        
        panel.generate_module_string()
        panel.block_interconnection()
        
end = timer()
df = pd.DataFrame(data = data_list, columns = ["Partition List", "SuperString", "Average Power", \
                                               "MPP (W)", "VMP (V)", "IMP (A)", "VOC (V)", "ISC (A)"])

df.sort_values("MPP (W)", ascending = False, inplace = True)
plot_top_x(20, df)

print(df["Average Power"])
print("Execution took", end - start, "seconds")

with pd.ExcelWriter("Datasets/" + filename + '.xlsx') as writer:
    df.to_excel(writer, sheet_name=filename)
plt.title(filename)
plt.savefig("Visualisation Plots/" + filename + '.png')