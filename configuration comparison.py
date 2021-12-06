# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 17:32:28 2021

@author: MarcelLima


TODO: output in pandas and csv in order to calculate power
TODO: calculate power
TODO: all series w/ bypass diode configuration
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
####################################################################################################

## DIMENSIONS ##
ROWS = 4
COLUMNS = 8
DEFAULT_CURRENT = 10

uniform = DEFAULT_CURRENT * uniform_shading(ROWS, COLUMNS)

block = DEFAULT_CURRENT * block_shading(ROWS, COLUMNS, np.array([0.8, 0.5, 0.4, 0.7]))

checkerboard = DEFAULT_CURRENT * checkerboard_shading(ROWS, COLUMNS, np.array([1]))

random = DEFAULT_CURRENT * random_shading(ROWS, COLUMNS, 0.7, 0.2) # last two arguments are mean and variance

fig, (ax0, ax1, ax2) = plt.subplots(1, 3, sharey=True)
fig.suptitle("Series, SP and TCT connections under four different shading conditions")

ax0.set_xlim(0,50)
ax0.set_ylim(0,100)
ax1.set_xlim(0,10)
ax2.set_xlim(0,10)

output_dict = {}


#%% All Series
count = 1
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
    analysis = simulator.dc(Vinput=slice(0,25,0.01))
    
    output_dict["SERIES " + legend_name] = np.array(analysis.Vinput)
    
    ax0.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = legend_name)
    
    count += 1
    
#ax0.legend()


#%% SP Interconnection
count = 1
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
    analysis = simulator.dc(Vinput=slice(0,25,0.01))
    
    output_dict["SP " + legend_name] = np.array(analysis.Vinput)
    
    ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = legend_name)
    
    count += 1
#ax1.legend()

#%% TCT Interconnection
count = 1
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
    analysis = simulator.dc(Vinput=slice(0,25,0.01))
    
    output_dict["TCT " + legend_name] = np.array(analysis.Vinput)
    
    ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = legend_name)
    
    count+= 1
ax2.legend()

#%% Data Frame Creation
df = pd.DataFrame(data = output_dict, index = np.arange(0,25,0.01))
configuration_columns = df.columns.tolist()

for column in configuration_columns:
    df[column].loc[lambda x: x < 0] = 0
    
#%% Calculate Power
for column in configuration_columns:
    df[str(column) + " Power"] = df[column]*df.index


power_df = df[df.columns[-12:]]
fig, (ax0, ax1, ax2) = plt.subplots(1, 3, sharey=True)

fig.suptitle("Series, SP and TCT Power curves")
ax0.set_xlim(0,25)
ax1.set_xlim(0,7)
ax2.set_xlim(0,7)
ax0.plot(power_df[power_df.columns[:4]])
ax1.plot(power_df[power_df.columns[4:8]])
ax2.plot(power_df[power_df.columns[-4:]])
ax2.legend(["Uniform", "Block", "Checkerboard", "Random"])

power_list = []
for column in configuration_columns:
    power = np.trapz(np.array(df[column]), x = np.array(df.index))
    power_list.append(power)
    print(column + " Power = ", power, "W")
    
power_df.loc["Total Power"] = power_list # SettingWithCopyWarning?

#%%

                  
