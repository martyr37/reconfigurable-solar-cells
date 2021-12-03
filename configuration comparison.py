# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 17:32:28 2021

@author: MarcelLima


TODO: output in pandas and csv in order to calculate power
TODO: calculate power
TODO: All series + all series w/diode configuration
"""

####################################################################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

from solar_cell import *
####################################################################################################

## DIMENSIONS ##
ROWS = 4
COLUMNS = 8
DEFAULT_CURRENT = 10

uniform = DEFAULT_CURRENT * uniform_shading(ROWS, COLUMNS)

block = DEFAULT_CURRENT * block_shading(ROWS, COLUMNS, np.array([0.8, 0.5, 0.4, 0.7]))

checkerboard = DEFAULT_CURRENT * checkerboard_shading(ROWS, COLUMNS, np.array([1]))

random = DEFAULT_CURRENT * random_shading(ROWS, COLUMNS, 0.7, 0.2) # last two arguments are mean and variance

fig, (ax0, ax1, ax2) = plt.subplots(1, 3)
fig.suptitle("SP and TCT connections under four different shading conditions")

ax0.set_xlim(0,50)
ax0.set_ylim(0,100)
ax1.set_xlim(0,10)
ax1.set_ylim(0,100)
ax2.set_xlim(0,10)
ax2.set_ylim(0,100)

#%% All Series

count = 1
legend_name = ""
for configuration in [uniform, block, checkerboard, random]:
    if count == 1:
        legend_name = "Uniform"
    elif count == 2:
        legend_name = "Block"
    elif count == 3:
        legend_name = "Checkerboard"
    elif count == 4:
        legend_name = "Random"
    circuit = all_series_connection(COLUMNS, ROWS, configuration)
    circuit.V('input', 1, circuit.gnd, 0)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Vinput=slice(0,50,0.01))
    
    ax0.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = legend_name)
    count += 1
#ax0.legend()

#%% SP Interconnection
count = 1
legend_name = ""
for configuration in [uniform, block, checkerboard, random]:
    if count == 1:
        legend_name = "Uniform"
    elif count == 2:
        legend_name = "Block"
    elif count == 3:
        legend_name = "Checkerboard"
    elif count == 4:
        legend_name = "Random"
    circuit = SP_interconnection(COLUMNS, ROWS, configuration)
    circuit.V('input', 1, circuit.gnd, 0)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Vinput=slice(0,10,0.01))
    
    ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = legend_name)
    count += 1
#ax1.legend()

#%% TCT Interconnection
count = 1
legend_name = ""
for configuration in [uniform, block, checkerboard, random]:
    if count == 1:
        legend_name = "Uniform"
    elif count == 2:
        legend_name = "Block"
    elif count == 3:
        legend_name = "Checkerboard"
    elif count == 4:
        legend_name = "Random"
    circuit = TCT_interconnection(COLUMNS, ROWS, configuration)
    circuit.V('input', COLUMNS, circuit.gnd, 0)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Vinput=slice(0,10,0.01))
    
    ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = legend_name)
    count+= 1
ax2.legend()    