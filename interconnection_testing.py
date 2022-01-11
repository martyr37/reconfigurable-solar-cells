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
ROWS = 4
ADJACENCY = False # make FALSE for anything larger than 4x4, takes too long

shading_map = 10 * random_shading(ROWS, COLUMNS, 0.6, 0.3)
#shading_map = 10 * checkerboard_shading(ROWS, COLUMNS, np.array([0.5, 0.5]))

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


#%%
with pd.ExcelWriter('interconnection_testing.xlsx') as writer:
    #iv_df.to_excel(writer, sheet_name="IV data")
    #pv_df.to_excel(writer, sheet_name="PV data")
    #summary_df.to_excel(writer, sheet_name="MPP data")
    df.to_excel(writer, sheet_name="Generated configurations")
