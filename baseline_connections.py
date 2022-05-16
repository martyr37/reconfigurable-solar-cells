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
import solar_module

####################################################################################################

#shading_map = solar_cell.block_shading(10, 6, np.array([9, 3, 7, 8]))
#shading_map = np.full((10, 6), 10)
#shading_map[:,-1:] = 3

#shading_map = np.triu(np.full((10,6), 10))
"""
shading_map = np.full((10, 6), 10)
shading_map[:,:2] = 3
map2 = np.copy(shading_map)
map3 = np.copy(shading_map)
map2[:,:4] = 3
map3 = np.triu(np.full((10, 6), 10))

shading_map = map3
"""

shading_map = np.array([[10. , 10. ,  9.5,  9.5,  8.5,  8. ],
       [10. ,  9.5,  9.5,  8.5,  8.5,  7. ],
       [ 9.5,  9.5,  8.5,  8.5,  7. ,  6. ],
       [ 9.5,  8.5,  8.5,  7. ,  6. ,  5. ],
       [ 8.5,  8.5,  7. ,  6. ,  5. ,  5. ],
       [ 8. ,  7. ,  6. ,  5. ,  5. ,  4. ],
       [ 7. ,  6. ,  5. ,  5. ,  4. ,  4. ],
       [ 6. ,  5. ,  5. ,  4. ,  4. ,  3. ],
       [ 5. ,  5. ,  4. ,  4. ,  3. ,  2. ],
       [ 5. ,  4. ,  4. ,  3. ,  2. ,  2. ]])

superstring = '[-91(90809382)(8192)83+][-(8595)(9484)+][-12246263642214434533045020710153255210132123737432154205344441005470355140613072113102(035560)(6575)+]'

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()


#%% All Series

series_circuit = solar_cell.all_series_connection(6, 10, shading_map)

series_circuit.V('input', 1, series_circuit.gnd, 0)
simulator = series_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

seriesI = np.array(analysis.Vinput)
seriesV = np.array(analysis.sweep)
seriesP = seriesI * seriesV
seriesMPP = max(seriesP)
seriesVMP = seriesV[seriesP.argmax()]
seriesIMP = seriesI[seriesP.argmax()]

#ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput), alpha=0.3, ls='--')
#ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput)*np.array(analysis.sweep), \
#         label = "All-Series Configuration: " + str(round(seriesMPP)) + ' W')
    
    
print("Series Connection:", round(seriesMPP, 2), 'W')
print("VMP:", round(seriesVMP, 2), 'V')
print("IMP:", round(seriesIMP, 2), 'A')
print()

#%% All Series w/ Bypass Diodes

bypass_circuit = solar_cell.all_series_bypass(6, 10, shading_map)

bypass_circuit.V('input', 1, series_circuit.gnd, 0)
simulator = bypass_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

bypassI = np.array(analysis.Vinput)
bypassV = np.array(analysis.sweep)
bypassP = bypassI * bypassV
bypassMPP = max(bypassP)
bypassVMP = bypassV[bypassP.argmax()]
bypassIMP = bypassI[bypassP.argmax()]

ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput),alpha=0.3, ls='--')
ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput)*np.array(analysis.sweep),\
         label = "Conventional Series Module: " + str(round(bypassMPP)) + ' W')

print("Series w/ Bypass Connection:", round(bypassMPP, 2), 'W')
print("VMP:", round(bypassVMP, 2), 'V')
print("IMP:", round(bypassIMP, 2), 'A')
print()

#%% TCT Connection

tct_circuit = solar_cell.TCT_interconnection(6, 10, shading_map)
tct_circuit.V('input', 6, series_circuit.gnd, 0)
simulator = tct_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

TCTI = np.array(analysis.Vinput)
TCTV = np.array(analysis.sweep)
TCTP = TCTI * TCTV
TCTMPP = max(TCTP)
TCTVMP = TCTV[TCTP.argmax()]
TCTIMP = TCTI[TCTP.argmax()]

#plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "TCT: " + str(round(TCTMPP)) + ' W')

print("TCT Connection:", round(TCTMPP, 2), 'W')
print("VMP:", round(TCTVMP, 2), 'V')
print("IMP:", round(TCTIMP, 2), 'A')
print()

#%% SP Connection

sp_circuit = solar_cell.SP_interconnection(6, 10, shading_map)
sp_circuit.V('input', 1, series_circuit.gnd, 0)
simulator = sp_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

SPI = np.array(analysis.Vinput)
SPV = np.array(analysis.sweep)
SPP = SPI * SPV
SPMPP = max(SPP)
SPVMP = SPV[SPP.argmax()]
SPIMP = SPI[SPP.argmax()]

#plt.plot(np.array(analysis.sweep), np.array(analysis.Vinput), label = "Series-Parallel Configuration: " + str(round(SPMPP)) + ' W')

print("SP Connection:", round(SPMPP, 2), 'W')
print("VMP:", round(SPVMP, 2), 'V')
print("IMP:", round(SPIMP, 2), 'A')
print()

#%%
reconfigurable_panel = solar_module.super_to_module(superstring, 6, 10, shading_map)
re_circuit = reconfigurable_panel.circuit
re_circuit.V('input', re_circuit.gnd, reconfigurable_panel.output_node, 99)
simulator = re_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

reI = np.array(analysis.Vinput)
reV = np.array(analysis.sweep)
reP = reI * reV
reMPP = max(reP)
reVMP = reV[reP.argmax()]
reIMP = reI[reP.argmax()]

ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput), alpha=0.3, ls='--')
ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput)*np.array(analysis.sweep),\
         label = "Non-standard Configuration: " + str(round(reMPP)) + ' W')

         
print("Reconfigurable Connection:", round(reMPP, 2), 'W')
print("VMP:", round(reVMP, 2), 'V')
print("IMP:", round(reIMP, 2), 'A')


#%% Plotting

ax1.set_xlabel("Voltage (V)")
ax1.set_ylabel("Current (A)")
ax2.set_ylabel("Power (W)")


ax1.set_xlim(0,60)
ax1.set_ylim(0,10)
ax2.set_ylim(0,200)
ax2.legend(fontsize='small')
fig.savefig('Abstract.png', dpi=200)