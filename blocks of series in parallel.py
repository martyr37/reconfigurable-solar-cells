# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 10:12:23 2021

@author: MarcelLima

12/11/2021: Seems to be that TCT and SP interconnections have identical
IV curves given identical dimensions, under the same uniform shading map. 

"""

####################################################################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

from solar_cell import solar_cell, TCT_interconnection, SP_interconnection, all_series_connection

####################################################################################################
#%% Total Cross-tied configuration
NUMBER_IN_SERIES = 8
NUMBER_IN_PARALLEL = 4

intensity_array = np.full((NUMBER_IN_PARALLEL,NUMBER_IN_SERIES),10) # static shading map, uniform illumination

circuit = TCT_interconnection(NUMBER_IN_SERIES, NUMBER_IN_PARALLEL, intensity_array)

circuit.V('input', NUMBER_IN_SERIES, circuit.gnd, 0)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,10,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "TCT")

plt.xlabel("Load Voltage")
plt.ylabel("Current")

plt.xlim(left=0)
plt.ylim(0,100)
#%% Series-Parallel Configuration
NUMBER_IN_SERIES = 8
NUMBER_IN_PARALLEL = 4

intensity_array = np.full((NUMBER_IN_PARALLEL,NUMBER_IN_SERIES),10) # static shading map, uniform illumination

circuit = SP_interconnection(NUMBER_IN_SERIES, NUMBER_IN_PARALLEL, intensity_array)

circuit.V('input', 1, circuit.gnd, 0)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,10,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "SP")

plt.xlabel("Load Voltage")
plt.ylabel("Current")

plt.xlim(left=0)
plt.ylim(0,100)

#%% All Series

NUMBER_IN_SERIES = 2
NUMBER_IN_PARALLEL = 2

intensity_array = np.full((NUMBER_IN_PARALLEL,NUMBER_IN_SERIES),10) # static shading map, uniform illumination

circuit = all_series_connection(NUMBER_IN_SERIES, NUMBER_IN_PARALLEL, intensity_array)

circuit.V('input', 1, circuit.gnd, 0)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,10,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "SP")

plt.xlabel("Load Voltage")
plt.ylabel("Current")

plt.xlim(left=0)
plt.ylim(0,100)
plt.legend()