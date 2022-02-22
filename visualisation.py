#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 12:10:49 2022

@author: mlima
"""

####################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
from matplotlib.pyplot import cm


import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

from solar_cell import *
from flexible_interconnections import interconnection, generate_string, partition_grid, plot_partition
from solar_module import solar_module, get_dimensions, get_top_left_coord

from timeit import default_timer as timer
####################################################################################################
#%%
shading_map = block_shading(10, 6, np.array([9, 3, 7, 8]))
#shading_map = random_shading(10, 6, 0.7, 0.3)
#%%
partition = [['00', '01', '02', '03', '04'], ['10', '20', '30', '40', '50'], ['11', '12', '13', '21', '22', '23', '31', '32', '33', '41', '42', '43', '51', '52', '53'], ['14', '24', '34', '44', '54'], ['60', '61', '70', '71', '80', '81'], ['90', '91'], ['62', '72'], ['82'], ['63', '73', '83'], ['05'], ['64'], ['15', '25', '35', '45'], ['55'], ['65'], ['92', '93'], ['74'], ['75'], ['84', '85'], ['94'], ['95']]
module_string = '-AD+-LTMKHQPBIERSNFOGJC+'
cell_strings = ['-0103+-(040200)+', '-304010+-5020+', '-11411331(5222322312535142)43(3321)+', '-34+-24+-(5444)14+', '-806070+-(7181)61+', '-(9190)+', '-62+-72+', '-82+', '-83(6373)+', '-05+', '-64+', '-2535(1545)+', '-55+', '-65+', '-(9293)+', '-74+', '-75+', '-8584+', '-94+', '-95+']
#%%
panel = solar_module("test", 6, 10, partition, shading_map, panel_string = module_string)
for block_no in range(len(panel.blocks)):
    letter = panel.blocks[block_no]
    panel.change_connection(letter, formatted_string=cell_strings[block_no])
#%% parallelness function
def parallel_measure(block_string):
    cell_count = 0
    cells_in_brackets = 0
    in_brackets = False
    for char in block_string:
        if char.isdigit() is True:
            cell_count += 0.5
            if in_brackets is True:
                cells_in_brackets += 0.5
        elif char == '(':
            in_brackets = True
        elif char == ')':
            in_brackets = False
    if cell_count == 1:
        return float(1)
    else:
        return cells_in_brackets / cell_count
        
#%%
def plot_panel(panel, shading_map):
    columns = panel.columns
    rows = panel.rows
    
    x = np.arange(0.5, columns + 0.5)
    y = np.arange(-0.5, -(rows + 0.5), -1)
    
    xx, yy = np.meshgrid(x, y)
    
    circle_sizes = np.reshape(shading_map, (columns * rows,))
    #circle_sizes = (circle_sizes - np.min(circle_sizes)) / (np.max(circle_sizes) - np.min(circle_sizes))
    
    
    plt.scatter(xx, yy, s=25*circle_sizes, c=shading_map, cmap = 'magma', edgecolor='black', linewidth=1)
    plt.ylim(-10, 0)
    plt.xlim(0, 6)
    plt.grid()
    axes = plt.gca()
    axes.set_yticks(np.arange(0, -10, -1))
    
    #color = iter(cm.rainbow(np.linspace(0, 1, len(panel.partition_list))))

    for block in panel.partition_list:
        block_string = panel.formatted_strings[panel.partition_list.index(block)]
        block_columns, block_rows = get_dimensions(block)
        xx, yy =  get_top_left_coord(block)
        #c = next(color)
        #TODO: alpha is the parameter of parallelness
        parallelness = parallel_measure(block_string)
        
        # (R, G, B, alpha)
        rectangle = patches.Rectangle((xx, -yy), block_columns, -(block_rows), facecolor=(0,1,0,parallelness*0.33),\
                                      fill=True, edgecolor=(0,0,1,0.2), linewidth=4)
        axes.add_patch(rectangle)
        
        print(block_string, parallelness)
        
    print(panel.module_string)

plot_panel(panel, shading_map)
panel.change_all_connections()
plot_panel(panel,shading_map)
panel.change_all_connections()
plot_panel(panel,shading_map)
#%%
def plot_panel2(panel_string, shading_map):
    cell_list = []
    number = False
    current_cell = ''
    for char in panel_string:
        if char.isdigit() is True and number is False:
            number = True
            current_cell = char
        elif char.isdigit() is True and number is True:
            cell_list.append(current_cell + char)
            number = False
    
    columns, rows = get_dimensions(cell_list)
    
    circuit, last_node = interconnection(panel_string, columns, rows, shading_map)
    

print(plot_panel2('-314253+-22(325233111343212312)+-(4151)+', shading_map))

#TODO: Assign a number to each block detailing amount of parallel connections
#TODO: Label each block
#TODO: Heatmap of each cell to determine parallel connectedness

