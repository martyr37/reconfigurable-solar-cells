#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:29:38 2022

@author: mlima
"""

##################################################################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

import solar_cell

####################################################################################################

shading_map = 10*solar_cell.checkerboard_shading(10, 6, np.array([0.9, 0.95, 0.8, 0.85]))

#%% All Series

series_circuit = solar_cell.all_series_connection(6, 10, shading_map)

series_circuit.V('input', 1, series_circuit.gnd, 0)
simulator = series_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "Series")

seriesI = np.array(analysis.Vinput)
seriesV = np.array(analysis.sweep)
seriesP = seriesI * seriesV
seriesMPP = max(seriesP)
seriesVMP = seriesV[seriesP.argmax()]
seriesIMP = seriesI[seriesP.argmax()]

print("Series Connection:", round(seriesMPP, 2), 'W')
print("VMP:", round(seriesVMP, 2), 'V')
print("IMP:", round(seriesIMP, 2), 'A')
print()

#%% All Series w/ Bypass Diodes

bypass_circuit = solar_cell.all_series_bypass(6, 10, shading_map)

bypass_circuit.V('input', 1, series_circuit.gnd, 0)
simulator = bypass_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "Bypass")

bypassI = np.array(analysis.Vinput)
bypassV = np.array(analysis.sweep)
bypassP = bypassI * bypassV
bypassMPP = max(bypassP)
bypassVMP = bypassV[bypassP.argmax()]
bypassIMP = bypassI[bypassP.argmax()]

print("Series w/ Bypass Connection:", round(bypassMPP, 2), 'W')
print("VMP:", round(bypassVMP, 2), 'V')
print("IMP:", round(bypassIMP, 2), 'A')
print()

#%% TCT Connection

tct_circuit = solar_cell.TCT_interconnection(6, 10, shading_map)
tct_circuit.V('input', 6, series_circuit.gnd, 0)
simulator = tct_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "TCT")

TCTI = np.array(analysis.Vinput)
TCTV = np.array(analysis.sweep)
TCTP = TCTI * TCTV
TCTMPP = max(TCTP)
TCTVMP = TCTV[TCTP.argmax()]
TCTIMP = TCTI[TCTP.argmax()]

print("TCT Connection:", round(TCTMPP, 2), 'W')
print("VMP:", round(TCTVMP, 2), 'V')
print("IMP:", round(TCTIMP, 2), 'A')
print()

#%% SP Connection

sp_circuit = solar_cell.SP_interconnection(6, 10, shading_map)
sp_circuit.V('input', 1, series_circuit.gnd, 0)
simulator = sp_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "SP")

SPI = np.array(analysis.Vinput)
SPV = np.array(analysis.sweep)
SPP = SPI * SPV
SPMPP = max(SPP)
SPVMP = SPV[SPP.argmax()]
SPIMP = SPI[SPP.argmax()]

print("SP Connection:", round(SPMPP, 2), 'W')
print("VMP:", round(SPVMP, 2), 'V')
print("IMP:", round(SPIMP, 2), 'A')

#%% Plotting

plt.xlabel("Voltage")
plt.ylabel("Current")

plt.xlim(0,60)
plt.ylim(0,100)
plt.legend()