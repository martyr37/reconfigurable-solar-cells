# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 10:12:23 2021

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
circuit = Circuit('3P/3S')

NUMBER_IN_SERIES = 3
NUMBER_IN_PARALLEL = 3

intensity_array = np.full((NUMBER_IN_PARALLEL,NUMBER_IN_SERIES),10)

print(intensity_array)

for row in range(0,NUMBER_IN_PARALLEL):
    for column in range(0,NUMBER_IN_SERIES):
        circuit.subcircuit(solar_cell(str(row) + str(column),intensity=intensity_array[row,column]))

## how to connect them up?

print(circuit)

