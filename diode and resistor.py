# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 13:43:39 2021

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

####################################################################################################

circuit = Circuit('Two-Diode Model')

input_current = 20@u_A
series_resistance = 1@u_mOhm
parallel_resistance = 10@u_kOhm

circuit.model('MyDiode', 'D', IS=1e-8, N=2)
circuit.model('MyDiode2', 'D', IS=1e-12, N=1)
    
#circuit.model('MyDiode', 'D', N=1.996)

circuit.I('illumination', "load", "in", input_current)
circuit.R('series_resistor', "load", circuit.gnd, series_resistance)
circuit.R('parallel_resistor', "in", "load", parallel_resistance)
circuit.Diode('diode', 'in', "load", model='MyDiode')
circuit.Diode('diode2','in','load',model='MyDiode2')
circuit.V('load_voltage', 'in', circuit.gnd, 0@u_V)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)

#analysis = simulator.operating_point()
analysis = simulator.dc(Vload_voltage=slice(0, 1, 0.005))

#print("Node:", str(analysis["illumination"]), "Values:", np.array(analysis["illumination"]))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vload_voltage))

plt.xlabel("Load Voltage")
plt.ylabel("Current")

plt.ylim(bottom=0)

plt.title("Double diode model - single cell")

print(circuit)

