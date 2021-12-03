# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 11:52:53 2021

@author: MarcelLima

"""
####################################################################################################
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *
logger = Logging.setup_logging()

####################################################################################################

class solar_cell(SubCircuit):
    __nodes__ = ('t_in', 't_out')
    
    def __init__(self, name, intensity=10@u_A, series_resistance=1@u_mOhm, parallel_resistance=10@u_kOhm,\
                 saturation_current_1=1e-8, ideality_1=2, saturation_current_2=1e-12, ideality_2=1):
        
        SubCircuit.__init__(self, name, *self.__nodes__) 
        
        self.model('Diode1', 'D', IS=saturation_current_1, N=ideality_1)
        self.model('Diode2', 'D', IS=saturation_current_2, N=ideality_2)
        
        self.intensity = intensity
        self.series_resistance = series_resistance
        self.parllel_resistance = parallel_resistance
        self.I(1, 't_load', 't_in', intensity)
        self.R(2, 't_load', 't_out', series_resistance)
        self.R(3, 't_in', 't_load', parallel_resistance)
        self.Diode(4, 't_in', 't_load', model='Diode1')
        self.Diode(5, 't_in', 't_load', model='Diode2')

        
    def set_illumination(self,intensity):
        self.intensity = intensity
        self.I(1, 't_load', 't_in', intensity)
        self.R(2, 't_load', 't_out', series_resistance)
        self.R(3, 't_in', 't_load', parallel_resistance)
        self.Diode(4, 't_in', 't_load', model='Diode1')
        self.Diode(5, 't_in', 't_load', model='Diode2')
        return None
    """
    ## a method to plot the IV curve of a cell - TODO
    def plot_IV(self, v_low=-1, v_high=1, step=0.01): 
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        
        analysis = simulator.dc(Vload_voltage = slice(v_low, v_high, step))
        
        fig = plt.figure()
        plt.plot(np.array(analysis.sweep), np.array(analysis.Vload_voltage))
        plt.xlabel("Load Voltage") 
        plt.ylabel("Current")
        
        return None
    """
    
#%% Total Cross Tied Interconnection
    
def TCT_interconnection(NUMBER_IN_SERIES, NUMBER_IN_PARALLEL, intensity_array):     
    circuit = Circuit('TCT Interconnected')
    for row in range(0,NUMBER_IN_PARALLEL): 
        for column in range(0,NUMBER_IN_SERIES):
            circuit.subcircuit(solar_cell(str(row) + str(column),intensity=intensity_array[row,column]))
        
    for row in range(0, NUMBER_IN_PARALLEL):
        for column in range(0, NUMBER_IN_SERIES):
            if column == 0:
                circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                          column + 1, circuit.gnd)
            else:
                circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                          column + 1, column)
    return circuit

#%% Series-Parallel Interconnection

def SP_interconnection(NUMBER_IN_SERIES, NUMBER_IN_PARALLEL, intensity_array):
    circuit = Circuit('SP Interconnected')
    for row in range(0,NUMBER_IN_PARALLEL):
        for column in range(0,NUMBER_IN_SERIES):
            circuit.subcircuit(solar_cell(str(row) + str(column),intensity=intensity_array[row,column]))
    
    for row in range(0, NUMBER_IN_PARALLEL):
        for column in range(0, NUMBER_IN_SERIES):
            if column == 0:
                circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                          str(row) + str(column), circuit.gnd)
            elif column == NUMBER_IN_SERIES - 1:
                circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                          '1', str(row) + str(column - 1)) # '1' represents the positive terminal of the module
            else:
                circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                          str(row) + str(column), str(row) + str(column - 1))
    return circuit

#%% All Series Connection
def all_series_connection(columns, rows, intensity_array):
    circuit = Circuit('All Series Connected')
    for row in range(0, rows):
        for column in range(0, columns):
            circuit.subcircuit(solar_cell(str(row) + str(column), intensity=intensity_array[row,column]))
        
    for row in range(0, rows):
        if row % 2 == 0:
            for column in range(0, columns):
                if row == 0 and column == 0:
                    circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                              str(row) + str(column), circuit.gnd)
                elif column == 0:
                    circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                              str(row) + str(column), str(row - 1) + str(column))
                elif row == rows - 1 and column == columns - 1:
                    circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                              '1', str(row) + str(column - 1))
                else:
                    circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                              str(row) + str(column), str(row) + str(column - 1))
        elif row % 2 == 1:
            for column in range(columns - 1, -1, -1):
                if column == columns - 1:
                    circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                              str(row) + str(column), str(row - 1) + str(column))
                elif row == rows - 1 and column == 0:
                    circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                              '1', str(row) + str(column + 1))
                else:
                    circuit.X(str(row) + str(column) + 'sbckt', str(row) + str(column), \
                              str(row) + str(column), str(row) + str(column + 1))
                    
    return circuit

print(all_series_connection(8, 3, np.full((3,8),10)))

#%% Uniform shading

def uniform_shading(rows, columns, current=1):
    return np.full((rows, columns), current)
    
#%% 4-block
def block_shading(rows, columns, current_list):
    # current_list is a one-dimensional array cnotaining the intensities in each block
    # e.g. [10, 7, 2, 6]
    
    # for now, assuming that it will always be split into 4 blocks 
    sqrt_number = int(math.sqrt(current_list.size))
    
    segments = np.resize(current_list,(sqrt_number, sqrt_number))
    
    intensity_array = np.zeros((rows, columns))
    
    for row in range(0, rows):
        for column in range(0, columns):
            if row < rows/2 and column < columns/2:
                intensity_array[row, column] = current_list[0]
            elif row < rows/2 and column >= columns/2:
                intensity_array[row, column] = current_list[1]
            elif row >= rows/2 and column < columns/2:
                intensity_array[row, column] = current_list[2]
            elif row >= rows/2 and column >= columns/2:
                intensity_array[row, column] = current_list[3]
                
    return intensity_array

#foo = np.array([1, 2, 3, 4])
#print(block_shading(12, 4, foo))

#%% Checkboard Shading
def checkerboard_shading(rows, columns, current_list):
    
    length = int(current_list.size)
    current_list_index = 0
    # current_list is an array containing the non-zero elements read from left to right.
    intensity_array = np.full((rows, columns), 0.2) # 0.2 is the "minimum" light level
    for row in range(0, rows):
        for column in range(0, columns):
            if (row + column) % 2 == 0:
                intensity_array[row, column] = current_list[current_list_index]
                current_list_index += 1
                current_list_index = current_list_index % length
    
    return intensity_array

#foo = np.array([(x/10) for x in range(1, 10, 1)])
#print(checkerboard_shading(12, 12, foo))
                
#%% Random Intensities

def random_shading(rows, columns, mean, variance):
    intensity_array = np.zeros((rows, columns))
    for row in range(0, rows):
        for column in range(0, columns):
            random_value = np.random.normal(mean, variance)
            if random_value > 1:
                random_value = 1
            intensity_array[row, column] = random_value
    
    return intensity_array