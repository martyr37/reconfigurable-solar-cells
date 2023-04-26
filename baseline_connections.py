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
#%% 
shading_map = solar_cell.block_shading(10, 6, np.array([9, 3, 7, 8]))
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
"""
shading_map = np.array([[ 0.        ,  0.        ,  6.05065666,  9.99061914,  0.65666041,
         2.25140713],
       [ 0.04690432,  0.09380863, 10.        , 10.        ,  0.84427767,
         4.73733583],
       [ 0.23452158,  0.04690432, 10.        , 10.        ,  2.67354597,
         7.69230769],
       [ 2.43902439,  2.1575985 , 10.        ,  9.99061914, 10.        ,
        10.        ],
       [10.        ,  8.81801126, 10.        , 10.        , 10.        ,
        10.        ],
       [10.        , 10.        , 10.        , 10.        , 10.        ,
         8.39587242],
       [10.        , 10.        , 10.        , 10.        , 10.        ,
         9.19324578],
       [ 7.87992495,  9.09943715,  8.58348968, 10.        ,  8.06754221,
         8.30206379],
       [10.        , 10.        , 10.        , 10.        , 10.        ,
        10.        ],
       [ 9.61538462, 10.        , 10.        , 10.        , 10.        ,
        10.        ]])
"""
superstring = '{[-030405131415232425333435434445535455636465737475838485939495+][-000102101112202122303132404142505152606162707172808182909192+]}'

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

#%% All Series
"""
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
#        label = "All-Series Configuration: " + str(round(seriesMPP)) + ' W')
    
    
print("Series Connection:", round(seriesMPP, 2), 'W')
print("VMP:", round(seriesVMP, 2), 'V')
print("IMP:", round(seriesIMP, 2), 'A')
print()
"""
#%% All Series w/ Bypass Diodes

bypass_circuit = solar_cell.all_series_bypass(6, 10, shading_map)

bypass_circuit.V('input', 1, bypass_circuit.gnd, 0)
simulator = bypass_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

bypassI = np.array(analysis.Vinput)
bypassV = np.array(analysis.sweep)
bypassP = bypassI * bypassV
bypassMPP = max(bypassP)
bypassVMP = bypassV[bypassP.argmax()]
bypassIMP = bypassI[bypassP.argmax()]

ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput),alpha=0.5, ls='--')
ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput)*np.array(analysis.sweep),\
        label = "Conventional Series Module: " + str(round(bypassMPP)) + ' W')

print("Series w/ Bypass Connection:", round(bypassMPP, 2), 'W')
print("VMP:", round(bypassVMP, 2), 'V')
print("IMP:", round(bypassIMP, 2), 'A')
print()

#%% TCT Connection

tct_circuit = solar_cell.TCT_interconnection(6, 10, shading_map)
tct_circuit.V('input', 6, tct_circuit.gnd, 0)
simulator = tct_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

TCTI = np.array(analysis.Vinput)
TCTV = np.array(analysis.sweep)
TCTP = TCTI * TCTV
TCTMPP = max(TCTP)
TCTVMP = TCTV[TCTP.argmax()]
TCTIMP = TCTI[TCTP.argmax()]

ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput),alpha=0.5,ls='--',color='C2')
ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput)*np.array(analysis.sweep),\
         label = "TCT Configuration: " + str(round(TCTMPP)) + ' W', color='C2')

print("TCT Connection:", round(TCTMPP, 2), 'W')
print("VMP:", round(TCTVMP, 2), 'V')
print("IMP:", round(TCTIMP, 2), 'A')
print()

#%% SP Connection

sp_circuit = solar_cell.SP_interconnection(6, 10, shading_map)
sp_circuit.V('input', 1, sp_circuit.gnd, 0)
simulator = sp_circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,50,0.01))

SPI = np.array(analysis.Vinput)
SPV = np.array(analysis.sweep)
SPP = SPI * SPV
SPMPP = max(SPP)
SPVMP = SPV[SPP.argmax()]
SPIMP = SPI[SPP.argmax()]

ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput),alpha=0.5,ls='--',color='C3')
ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput)*np.array(analysis.sweep),\
         label = "Series-Parallel Configuration: " + str(round(SPMPP)) + ' W',color='C3')

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

ax1.plot(np.array(analysis.sweep), np.array(analysis.Vinput),alpha=0.5,ls='--',color='C1')
ax2.plot(np.array(analysis.sweep), np.array(analysis.Vinput)*np.array(analysis.sweep),\
        label = "Non-standard Configuration: " + str(round(reMPP)) + ' W', color='C1')

         
print("Reconfigurable Connection:", round(reMPP, 2), 'W')
print("VMP:", round(reVMP, 2), 'V')
print("IMP:", round(reIMP, 2), 'A')


#%% Plotting
ax1.tick_params(axis='both', labelsize='large')
ax2.tick_params(axis='both', labelsize='large')
ax1.set_xlabel("Voltage (V)", fontsize='large')
ax1.set_ylabel("Current (A)", fontsize='large')
ax2.set_ylabel("Power (W)", fontsize='large')


ax1.set_xlim(0,60)
ax1.set_ylim(0,100)
ax2.set_ylim(0,350)
ax2.legend(fontsize='large')
fig.savefig('Abstract.png', dpi=300, bbox_inches="tight")
