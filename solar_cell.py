# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 11:52:53 2021

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