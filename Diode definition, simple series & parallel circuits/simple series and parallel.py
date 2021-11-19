# -*- coding: utf-8 -*-
"""
Created on Fri Nov 5 16:02:44 2021

@author: MarcelLima
"""

####################################################################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

from solar_cell import solar_cell
####################################################################################################

series_or_parallel = "PARALLEL"

if series_or_parallel == "SERIES":
    circuit = Circuit('2S') # two in series
    circuit.subcircuit(solar_cell('cell1')) # instance of a normal solar_cell
    circuit.subcircuit(solar_cell('cell2')) # 2nd instance

    circuit.X('1', 'cell1', 1, circuit.gnd)
    circuit.X('2', 'cell2', 2, 1)

    circuit.V('input', 2, circuit.gnd, 0@u_V) # measuring voltage source"""
    
elif series_or_parallel == "PARALLEL":
    
    circuit = Circuit('2P') # two in parallel
    circuit.subcircuit(solar_cell('cell1', intensity = 30)) # instance of a normal solar_cell
    circuit.subcircuit(solar_cell('cell2')) # 2nd instance
    circuit.subcircuit(solar_cell('cell3')) # 3rd instance
    
    circuit.X('1', 'cell1', 1, circuit.gnd)
    circuit.X('2', 'cell2', 1, circuit.gnd)
    circuit.X('3', 'cell3', 1, circuit.gnd)
    
    circuit.V('input', 1, circuit.gnd, 0@u_V) # measuring voltage source

print(circuit)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)

analysis = simulator.dc(Vinput=slice(0,5,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput))

plt.xlabel("Load Voltage")
plt.ylabel("Current")

plt.xlim(left=0)
plt.ylim(0,100)

if series_or_parallel == "SERIES":
    plt.title("All in series")
elif series_or_parallel == "PARALLEL":
    plt.title("All in parallel")
    
