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
from flexible_interconnections import interconnection, generate_string
####################################################################################################

output_dict = {}
COLUMNS = 6
ROWS = 10
ADJACENCY = False # make FALSE for anything larger than 4x4, takes too long

shading_map = 10 * random_shading(ROWS, COLUMNS, 0.6, 0.3)
#shading_map = 10 * checkerboard_shading(ROWS, COLUMNS, np.array([.4, .3, .6, .5]))
#shading_map = block_shading(ROWS, COLUMNS, np.array([9,3,7,8]))

#%% Testing 7 predetermined 2x2 interconnections

"""

interconnection_list = ['-00011110+', '-(0001)(1011)+', '-00(0111)10+', '-(0010)0111+', \
                        '-(0011)(0110)+', '-(0010)(0111)+', '-0001+-1011+']
for connection in interconnection_list:
    circuit, output_node = interconnection(connection, 3, 3, shading_map)
    circuit.V('output', circuit.gnd, output_node, 99)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Voutput=slice(0,10,0.01))
    
    plt.plot(np.array(analysis.sweep), np.array(analysis.Voutput), label=connection)
    
    output_dict[connection] = analysis.Voutput


plt.xlim(left=0)
plt.ylim(bottom=0, top=50) 
plt.legend()

iv_df = pd.DataFrame(data = output_dict, index = np.array(analysis.sweep))

pv_df = pd.DataFrame(data = None, index = np.array(analysis.sweep), columns = iv_df.columns.tolist())

for column in iv_df:
    pv_df[column] = iv_df[column] * np.array(iv_df.index)
    pv_df[column] = pv_df[column].loc[lambda x: x >= 0] # only positive power
    output_dict[column] = [pv_df[column].max(), pv_df[column].idxmax(), iv_df[column][pv_df[column].idxmax()]]
    
summary_df = pd.DataFrame(data = output_dict, index = ["P_MP", "V_MP", "I_MP"])
summary_df = summary_df.transpose()

#print(iv_df)
#print(pv_df)
#print(summary_df)

"""

#%% Testing 1000 random configurations

mpp_list = {}

for x in range(0, 1000):
    formatted_string = generate_string(COLUMNS, ROWS, adjacent = ADJACENCY)
    if formatted_string == None:
        continue
    circuit, output_node = interconnection(formatted_string, COLUMNS, ROWS, shading_map)
    #print(circuit)
    #print(output_node)
    #print(formatted_string)
    circuit.V('output', circuit.gnd, output_node, 99)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Voutput=slice(0,10,0.01))
    
    power = np.array(analysis.sweep) * np.array(analysis.Voutput)
    
    # append P_MP, V_MP and I_MP of each configuration
    
    mpp_list[formatted_string] = (power.max(), np.array(analysis.sweep)[power.argmax()], \
                                           np.array(analysis.Voutput)[power.argmax()])
# note that despite the above loop running 1000 times, the number of configurations in the 
# dataframe is less, as generate_string may generate duplicate interconnections

df = pd.DataFrame(data = mpp_list, index = ["P_MP", "V_MP", "I_MP"])
df.sort_values('P_MP', axis=1, ascending=False, inplace=True)
df = df.transpose()
print(df)

#%% Writing results to interconnection_testing.xlsx
with pd.ExcelWriter('interconnection_testing.xlsx') as writer:
    #iv_df.to_excel(writer, sheet_name="IV data")
    #pv_df.to_excel(writer, sheet_name="PV data")
    #summary_df.to_excel(writer, sheet_name="MPP data")
    df.to_excel(writer, sheet_name="Generated configurations")
    
#%%
circuit = foo[0]
circuit.V('input', 0, foo[1], 0)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(0,10,0.01))
#%%
circuit1 = all_series_connection(6, 10, shading_map)
circuit2 = all_series_bypass(6, 10, shading_map)
circuit3 = SP_interconnection(6, 10, shading_map)
circuit4 = TCT_interconnection(6, 10, shading_map)
circuit1.V('input', 1, circuit1.gnd, 0)
circuit2.V('input', 1, circuit2.gnd, 0)
circuit3.V('input', 1, circuit3.gnd, 0)
circuit4.V('input', 6, circuit4.gnd, 0)
simulator1 = circuit1.simulator(temperature=25, nominal_temperature=25)
analysis1 = simulator1.dc(Vinput=slice(0,50,0.01))
simulator2 = circuit2.simulator(temperature=25, nominal_temperature=25)
analysis2 = simulator2.dc(Vinput=slice(0,50,0.01))
simulator3 = circuit3.simulator(temperature=25, nominal_temperature=25)
analysis3 = simulator3.dc(Vinput=slice(0,50,0.01))
simulator4 = circuit4.simulator(temperature=25, nominal_temperature=25)
analysis4 = simulator4.dc(Vinput=slice(0,50,0.01))
#%%
fig, ax = plt.subplots()

# plot analysis data
ax.plot(analysis.sweep, analysis.Vinput, color='black',label='Non-standard configuration')
#ax.plot(analysis1.sweep, analysis1.Vinput, color='teal',label='AS configuration')
ax.plot(analysis2.sweep, analysis2.Vinput, color='blue', label='AS configuration with BPD')
ax.plot(analysis3.sweep, analysis3.Vinput, color='red',label='SP configuration')
ax.plot(analysis4.sweep, analysis4.Vinput, color='green',label='TCT configuration')

# create twin axis
ax.tick_params(axis='both', labelsize=14)
ax2 = ax.twinx()
ax2.tick_params(axis='both', labelsize=14)

# plot analysis.Vinput*analysis.sweep on twin axis
ax2.plot(analysis.sweep, analysis.Vinput*analysis.sweep, linestyle='--', linewidth=1.5, alpha=0.6, color='black')
#ax2.plot(analysis1.sweep, analysis1.Vinput*analysis1.sweep, linestyle='--', linewidth=1.5, alpha=0.6, color='teal')
ax2.plot(analysis2.sweep, analysis2.Vinput*analysis2.sweep, linestyle='--', linewidth=1.5, alpha=0.6, color='blue')
ax2.plot(analysis3.sweep, analysis3.Vinput*analysis3.sweep, linestyle='--', linewidth=1.5, alpha=0.6, color='red')
ax2.plot(analysis4.sweep, analysis4.Vinput*analysis4.sweep, linestyle='--',linewidth=1.5, alpha=0.6, color='green')

# set x and y limits
ax.set_xlim(0, 50)
ax.set_ylim(0, 150)
ax2.set_ylim(0, 250)

# set labels and legend
ax.set_xlabel('Voltage (V)',fontsize=14)
ax.set_ylabel('Current (A)',fontsize=14)
ax2.set_ylabel('Power (W)',fontsize=14)
ax.legend()
plt.savefig('config.png', dpi=300, bbox_inches='tight')
#%%
plt.imshow(shading_map)
#plt.text(0.8, 2.2, '9',color='black',fontsize=14)
#plt.text(3.8, 2.2, '3',color='white',fontsize=14)
#plt.text(0.8, 7.2, '7',color='black',fontsize=14)
#plt.text(3.8, 7.2, '8',color='black',fontsize=14)
plt.tick_params(axis='both', which='both', length=0, width=0, labelsize=0)


