#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 14:49:35 2021

@author: mlima
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
from flexible_interconnections import interconnection
####################################################################################################

shading_map = 10 * checkerboard_shading(2, 2, np.array([0.5, 0.5]))

plt.figure(0)

interconnection_list = ['-00011110+', '-(0001)(1011)+', '-00(0111)10+', '-(0010)0111+', \
                        '-(0011)(0110)+', '-(0010)(0111)+', '-0001+-1011+']
    
for connection in interconnection_list:
    circuit, output_node = interconnection(connection, 2, 2, shading_map)
    circuit.V('output', circuit.gnd, output_node, 99)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Voutput=slice(0,10,0.01))
    
    plt.plot(np.array(analysis.sweep), np.array(analysis.Voutput), label=connection)


plt.xlim(left=0)
plt.ylim(bottom=0, top=50) 
plt.legend()