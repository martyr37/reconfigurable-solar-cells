#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 16:31:45 2022

@author: mlima
"""
####################################################################################################
import random
import numpy as np
####################################################################################################

def make_adjacent(cell_ids):
    original_cell_ids = cell_ids

    adjacent_cells = []
    
    row_coords = set()
    column_coords = set()
    
    for cell in cell_ids:
        row = int(cell[0])
        column = int(cell[1])
        row_coords.add(row)
        column_coords.add(column)
    min_row, max_row = min(row_coords), max(row_coords)
    min_col, max_col = min(column_coords), max(column_coords)
    
    random_cell = random.choice(cell_ids)
    adjacent_cells.append(random_cell) # add to final list the current cell chosen at random
    current_cell = random_cell
    while len(adjacent_cells) != len(cell_ids):
        
        current_y, current_x = int(current_cell[0]), int(current_cell[1])
        
        possible_cells = [str(y) + str(x) for y in range(current_y - 1, current_y + 2)\
                          for x in range(current_x - 1, current_x + 2)\
                              if (min_row <= y <= max_row) and (min_col <= x <= max_col)]
            
        possible_cells.remove(str(current_y) + str(current_x)) 
        possible_cells = list(filter(lambda foo: foo not in adjacent_cells, possible_cells))
        
        if possible_cells != []:
            current_cell = random.choice(possible_cells)
            adjacent_cells.append(current_cell)
        else:
            return None
        
    return adjacent_cells
    
cells = [str(y) + str(x) for y in range(0, 3) for x in range(0, 5)]
cells = make_adjacent(cells)

class Cell():
    def __init__(self, cell_id, panel_cols, panel_rows, start_col = 0, start_row = 0):
        self.cell_id = cell_id
        self.panel_cols = panel_cols
        self.panel_rows = panel_rows
        self.start_col = start_col
        self.start_row = start_row
        
        self.y, self.x = int(cell_id[0]), int(cell_id[1])
    def adjacent_cells(self):
        possible_cells = [str(y) + str(x) for y in range(self.y - 1, self.y + 2)\
                          for x in range(self.x - 1, self.x + 2)\
                              if (self.start_col <= y <= self.start_col + self.panel_cols - 1)\
                                  and (self.start_row <= x <= self.start_row + self.panel_rows - 1)]
        possible_cells.remove(str(self.y) + str(self.x))
        return possible_cells

test = Cell('00', 3, 3)

class Graph():
    def __init__(self, panel_cols, panel_rows, start_col = 0, start_row = 0):
        self.cols = panel_cols
        self.rows = panel_rows
        self.start_col = start_col
        self.start_row = start_row
        
        self.graph = np.zeros((self.rows, self.cols))
        
        self.cell_objs = []
        self.cell_ids = []
        
        for y in range(start_row, start_row + self.rows):
            for x in range(start_col, start_col + self.cols):
                cell = Cell(str(y) + str(x), self.cols, self.rows, start_col, start_row)
                self.cell_objs.append(cell)
                self.cell_ids.append(cell.cell_id)
                
                
        self.cell_objs = np.reshape(np.array(self.cell_objs), (self.rows, self.cols))
        self.cell_ids = np.reshape(np.array(self.cell_ids), (self.rows, self.cols))
        
    def adjacent_path(self):
        col, row = 0, 0
        self.graph[row][col] = 1
        while True:
            current_cell = self.cell_objs[row][col]
            adjacent_cell = random.choice(current_cell.adjacent_cells())
            
            y, x = int(adjacent_cell[0]) - self.start_col, int(adjacent_cell[1]) - self.start_row
            
            if self.graph[x][y] == 0:
                self.
            
            return adjacent_cell, y, x
            
        
    
test1 = Graph(3, 3, 2, 2)
        