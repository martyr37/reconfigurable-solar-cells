#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 17:12:39 2022

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

from solar_cell import *
from flexible_interconnections import interconnection, generate_string, partition_grid, plot_partition
from solar_module import solar_module, super_to_module
from visualisation import plot_panel


from timeit import default_timer as timer
####################################################################################################
#%% 
shading_map = block_shading(10, 6, np.array([9, 3, 7, 8]))
filename = 'B9378P10'

#%%
def plot_top_x(x, df):
    top_x = df.head(x)
    top_x_superstrings = top_x["SuperString"]
    panel_list = []
    for superstring in top_x_superstrings:
        panel_list.append(super_to_module(superstring, 6, 10, shading_map))
    plot_panel(panel_list, shading_map)

#%%

df = pd.read_excel('Datasets/' + filename + '.xlsx')
#%%

plot_top_x(20, df)
