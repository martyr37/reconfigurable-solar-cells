# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 10:12:23 2021

@author: MarcelLima

12/11/2021: Seems to be that TCT and SP interconnections have identical
IV curves given identical dimensions, under the same uniform shading map. 
TODO: Investigate how TCT and SP differ under different shading conditions.
Change the NUMBER_IN_SERIES/PARALLEL constant to be automatic given an input array.
Maybe make TCT and SP methods in a class.

TODO: Different reconfiguration methods and papers listed under today's date

"""

####################################################################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

from solar_cell import solar_cell, TCT_interconnection, SP_interconnection

####################################################################################################
#%% Total Cross-tied configuration
NUMBER_IN_SERIES = 4
NUMBER_IN_PARALLEL = 3

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
NUMBER_IN_SERIES = 4
NUMBER_IN_PARALLEL = 3

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

#%%

plt.legend()