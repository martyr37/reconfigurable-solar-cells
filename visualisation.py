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
#%%
def plot_panel(panel, shading_map):
    columns = panel.columns
    rows = panel.rows
    
    x = np.arange(columns + 1)
    y = np.arange(0, -(rows + 1), -1)
    
    plt.pcolormesh(x, y, shading_map, cmap="magma")
    plt.grid()
    axes = plt.gca()
    axes.set_yticks(np.arange(0, -10, -1))
    
    #color = iter(cm.rainbow(np.linspace(0, 1, len(panel.partition_list))))

    for block in panel.partition_list:
        print(panel.formatted_strings[panel.partition_list.index(block)])
        block_columns, block_rows = get_dimensions(block)
        xx, yy =  get_top_left_coord(block)
        #c = next(color)
        rectangle = patches.Rectangle((xx, -yy), block_columns, -(block_rows), fill=False, edgecolor='b', linewidth=4)
        axes.add_patch(rectangle)
        
    print(panel.module_string)

plot_panel(panel, shading_map)

#TODO: Assign a number to each block detailing amount of parallel connections
#TODO: Label each block
#TODO: Heatmap of each cell to determine parallel connectedness


