import pygame
import numpy as np  # we'll use numpy arrays as the basis for our grids.
import sys
from typing import Tuple, List
from dataclasses import dataclass, field

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Define some colors, mostly useful for testing
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

COLORS = [WHITE, RED, BLACK, GREEN]


# Things that can be changed: number of states, grid dimensions, square size,
# padding, neighbors function, rules function, grid initialization function.


class grid:
    gridSize: Tuple[int, int]  # columns, rows == x,y
    data: np.ndarray
    generations: int

    def __init__(self, size, setup):
        self.gridSize = size
        self.data = setup(size)
        self.generations = 0


# --------------------------------------------------------------------
# Initialization functions -- used by the constructor. Only one is used
# in any game definition. You may add your own for the creative exercise.
# --------------------------------------------------------------------

# function: randStart
# Purpose: employed by grid __init__ (constructor) to give initial value to data
# param: size
# returns: an np array of size size, whose values are uniformly selected from range(states)
def randStart(size):
    # your code here
    return


# function: glideStart
# Purpose: employed by grid __init__ (constructor) to give initial value to data
# param: size
# returns: an np array of size size, whose values are all zero, except for positions
# (2,0), (0,1), (2,1), (1,2), and (2,2), whose values are 1. Intended to be used
# on a game w 2 states.
def glideStart(size):
    arr = np.zeros([size[0], size[1]])
    arr[0][2] = 1
    arr[1][0] = 1
    arr[1][2] = 1
    arr[2][2] = 1
    arr[2][1] = 1

    # Column
    arr[10][10] = 1
    arr[10][11] = 1
    arr[10][12] = 1

    # Column
    arr[20][20] = 1
    arr[21][20] = 1
    arr[22][20] = 1
    return arr


# --------------------------------------------------------------------
# Rule functions -- used by the evolve function. Only one is used
# in any game definition. You MUST add a new one for the creative exercise.
# --------------------------------------------------------------------

# function: ruleGOL
# purpose: applies a set of rules given a current state and a set of tallies over neighbor states
# params: cell, an element from range(states), where states is the global variable
#           tallies, tallies[k] = number of neighbors of state k, for all k in the range of states
# returns: a new state based on the classic rules of the game of life.
#           See https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
# Note: assumes a two-state game, where 0 is "dead" and 1 is "alive"

def ruleGOL(cell, tallies):
    if tallies[1] == 3:
        return 1
    elif tallies[1] == 2 and cell == 1:
        return 1
    else:
        return 0


# function: ruleCycle
# purpose: applies a set of rules given a current state and a set of tallies over neighbor states
# params: cell, an element from range(states), where states is the global variable
#           tallies, tallies[k] = number of neighbors of state k, for all k in the range of states
# returns: if k is the current state, returns k+1 if there is a neighbor of state k+1, else returns k

def ruleCycle(cell, tallies):
    # your code here
    return


# --------------------------------------------------------------------
# Neighbor functions -- used by the evolve function. Only one is used
# in any game definition. You may add your own for the creative exercise.
# --------------------------------------------------------------------
# returns a list of neighbors in a square around x,y
def neighborSquare(x, y):
    # your code here
    arr = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1), (x - 1, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1)]
    return arr


# returns a list of neighbors in a diamond around x,y (NWSE positions)
def neighborDiamond(x, y):
    arr = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    # print(arr)
    return arr


# function: tally_neighbors
# purpose: counts a given cell's the neighbors' states
# params: grid, an np array of data from a grid, containing states of all cells
#         position, the current cell position (a Tuple)
#         neighborSet, a function that when called on position x,y returns a list of x,y's neighbors
# returns: a list whose entries, tally[k] are the number of valid neighbors of x,y whose state is k.
# Note: neighborSet may not necessarily return *valid* neighbors. It's tally_neighbor's job to check
# for validity.

def tally_neighbors(grid, position, neighborSet):
    tally = np.zeros(states)
    # print(position)
    for coordinate in neighborSet(position[0], position[1]):
        x, y = coordinate
        # print(x, y, grid.gridSize)
        if x < 0 or x >= grid.gridSize[0] or y < 0 or y >= grid.gridSize[1]:
            continue
        else:
            value = int(grid.data[y][x])
            # print('value', value)
            tally[value] = tally[value] + 1
    return tally


# student: putting it all together.
# function: evolve
# purpose: to increment the automata by *one* time step. Given an array representing the automaton at the
# start of the time step (the start grid), this function creates an array for the end of the time step
# (the end grid) by applying the rule specified in function apply_rule to every position in the array.
# Note that all rule evaluation is done on the start grid, but the new state is set in the end grid.
# This function *changes* the input parameter to the new state. TODO: ??? but how to maintain start grid?
# The grid's generations variable should be incremented every time the function is called. (This variable
# may only be useful for debugging--there is a lot we *could* do with it, but our application doesn't use it.)
def evolve(gr, apply_rule, neighborSet):
    gr.generations = gr.generations + 1
    end_grid = np.zeros([gr.gridSize[0], gr.gridSize[0]])
    for y in range(gr.gridSize[0]):
        for x in range(gr.gridSize[0]):
            end_grid[y][x] = apply_rule(gr.data[y][x],
                                        tally_neighbors(gr, (x, y),
                                                        neighborSet))
    gr.data = end_grid


# function draw_block
# purpose: draw a rectangle of color acolor for *grid* location x,y. Uses globals pad and sqSize.
# function solution is:     pygame.draw.rect(screen, acolor,
#   [upper left horiz pixel location, upper left vertical pixel location, sqSize, sqSize])
# returns: nothing
def draw_block(x, y, acolor):
    tl_x = (x + 1) * pad + x * sqSize
    tl_y = (y + 1) * pad + y * sqSize
    pygame.draw.rect(screen, acolor, [tl_x, tl_y, sqSize, sqSize])
    return


# function: draw
# purpose: translates the game representation from the grid, to an image on the screen
# param: gr, a grid. for every position in gr.data, computes a color based on the state
# in that location, and then makes a call to draw_block to place that color into the pygame
# screen. Also passes the grid location so draw_block can compute the correct screen location.
# The new color is represented in HSVA (see https://www.pygame.org/docs/ref/color.html#pygame.Color.hsva
# and has hue h = (360 // states) * current state, s = 100, and v = 50 (we just left A of HSVA 
# at its default value). You may want to experiment with these values for artistic effect. :)
# returns: nothing
def draw(gr):
    for y, row in enumerate(gr.data):
        for x, cell in enumerate(row):
            draw_block(x, y, COLORS[int(cell)])
    return


# following are the game, grid, and screen parameters for the problem

# Set the number of states to use within each cell
states = 2  # we leave this as a global variable since it doesn't change.

# words to display on the window
pygame.display.set_caption("CPSC 203 Life")

# the game state is maintained in a grid object.
# grid data values will be updated upon every click of the clock.
# parameters are the (width, height) dimensions of the grid, and a
# function that initializes the start state
# g = grid((100, 150), randStart)
g = grid((30, 30), glideStart)

# drawing parameters that determine the look of the grid when it's shown.
# These can be set, but defaults are probably fine
sqSize = 20  # size of the squares in pixels
pad = sqSize // 5  # the number of pixels between each square

# computed from parameters above and grid g dimensions
width = (g.gridSize[0] + 1) * pad + (g.gridSize[0] * sqSize)
s = (width, width)
screen = pygame.display.set_mode(s)  # initializes the display window

# Used to manage how fast the screen updates
clock = pygame.time.Clock()


# given: necessary for gracefully ending game loop (pygame)
def handleInputEvents():
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close...
            sys.exit(0)  # quit


# some variables you probably won't want to change
frameCount = 0
desiredGifLength = 200
frameRate = 1
frames = []

# -------- Main Program Loop -----------
while True:  # runs continually until stopped
    # --- Main event loop
    handleInputEvents()

    # --- Draw the grid
    # this function loops over the data in the grid object
    # and draws appropriately colored rectangles.
    draw(g)

    # --- Game logic should go here
    # evolve( g, rule, neighbors)
    # g -- an object of type grid, previously initialized to hold data start state
    # rule -- a function that applies the game rule, given a cell state and a neighbor tally
    # neighbors -- a function that returns a list of neighbors relative to a given x,y position.
    # evolve(g, ruleCycle, neighborDiamond)
    evolve(g, ruleGOL, neighborSquare)

    # --- Mysterious reorientation that every pygame application seems to employ
    pygame.display.flip()

    # --- Uncomment code below to save a GIF of your custom automaton
    # if frameCount < desiredGifLength:
    #     pygame.image.save(screen, "temp.png")
    #     frames.append(Image.open("temp.png"))
    # else:
    #     frames[0].save('custom.gif', format='GIF',
    #                    append_images=frames[1:], duration=1000/frameRate,
    #                    save_all=True, loop=0)
    # frameCount += 1

    # --- Limit to 60 frames per second
    clock.tick(frameRate)

# Close the window and quit.
pygame.quit()
