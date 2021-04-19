import os
import sys
import pygame
import numpy as np
from PIL import Image
from typing import Tuple, List

path = os.path.dirname(__file__)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

COLORS = [WHITE, RED, BLACK, GREEN]


class Grid:
    gridSize: Tuple[int, int]  # columns, rows == x,y
    data: np.ndarray
    generations: int

    def __init__(self, size, setup):
        self.gridSize = size
        self.data = setup(size)
        self.generations = 0


def rand_start(size):
    """
    Used by grid's (constructor) to provide random initial data.

    Returns an array of size `size[0]` by `size[1]` whose values are uniformly selected from states.
    """
    raise NotImplementedError


def glide_start(size):
    """
    Start with a glider.

    Returns an np array of size size, whose values are all zero, except for positions
    (2,0), (0,1), (2,1), (1,2), and (2,2), whose values are one.
    """
    start = np.zeros([size[0], size[1]])
    start[0][2] = 1
    start[1][0] = 1
    start[1][2] = 1
    start[2][2] = 1
    start[2][1] = 1
    return start


def rule_gol(cell, tallies):
    """
    Return a cell's new state based on the classic rules of the Game of Life, by John Conway.

    NOTE: Assumes a two-state game, with 0 for "dead" and 1 for "alive."

    [See more.](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
    """
    if tallies[1] == 3:
        return 1
    elif tallies[1] == 2 and cell == 1:
        return 1
    else:
        return 0


def rule_cycle(cell, tallies):
    """
    Applies a set of rules given a current state and a set of tallies over neighbor states.

    If k is the current state, returns k+1 if there is a neighbor of state k+1, else returns k.
    """
    raise NotImplementedError


def neighbor_square(x: int, y: int) -> List[Tuple[int, int]]:
    """
    Returns coordinates of neighbors in a square around (x, y).
    """
    return [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
        (x - 1, y - 1),
        (x + 1, y + 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
    ]


def neighbor_diamond(x: int, y: int) -> List[Tuple[int, int]]:
    """
    Returns coordinates of neighbors in a diamond around (x, y).
    """
    return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


def tally_neighbors(grid, position, neighbor_set):
    """
    Counts a cell's neighbors' states. Produces tally in the `tally` list.
    """
    tally = np.zeros(states)
    for coordinate in neighbor_set(position[0], position[1]):
        x, y = coordinate

        if x < 0 or x >= grid.gridSize[0] or y < 0 or y >= grid.gridSize[1]:
            # if co-ordinate is invalid, skip
            continue
        else:
            value = int(grid.data[y][x])
            tally[value] = tally[value] + 1

    return tally


def evolve(grid, apply_rule, neighbor_set):
    """
    Increment the automata by one step in time.
    """
    grid.generations = grid.generations + 1
    end_grid = np.zeros([grid.gridSize[0], grid.gridSize[0]])
    for y in range(grid.gridSize[0]):
        for x in range(grid.gridSize[0]):
            end_grid[y][x] = apply_rule(
                grid.data[y][x], tally_neighbors(grid, (x, y), neighbor_set)
            )
    grid.data = end_grid


def draw_block(x, y, color):
    """
    Draw a rectangle at grid location (x, y).
    """
    tl_x = (x + 1) * pad + x * square_size
    tl_y = (y + 1) * pad + y * square_size
    pygame.draw.rect(screen, color, [tl_x, tl_y, square_size, square_size])
    return


def draw(grid):
    """
    Draws many blocks, representing the game grid.
    """
    for y, row in enumerate(grid.data):
        for x, cell in enumerate(row):
            draw_block(x, y, COLORS[int(cell)])
    return


def handle_inputs():
    """
    Handle user inputs to gracefully exit.
    """
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close...
            sys.exit(0)  # quit


if __name__ == "__main__":
    # Set window caption
    pygame.display.set_caption("Conway's Game of Life")

    # Set the number of states to use within each cell
    states = 2

    # Video settings
    frame_count = 0
    gif_length = 110
    fps = 10
    frames = []

    # Game grid object with number of grid **cells** wide and tall
    g_width = 30
    g_height = 30
    grid = Grid((g_width, g_height), glide_start)

    # Square size and padding size, for sketching the grid
    square_size = 20
    pad = square_size // 5

    # Define window size of pygame
    width = (grid.gridSize[0] + 1) * pad + (grid.gridSize[0] * square_size)
    height = (grid.gridSize[1] + 1) * pad + (grid.gridSize[1] * square_size)
    s = (width, height)
    screen = pygame.display.set_mode(s)

    # Set pygame clock
    clock = pygame.time.Clock()

    while True:
        # Check user inputs
        handle_inputs()

        # Draw the grid
        draw(grid)

        # Go to next state
        evolve(grid, rule_gol, neighbor_square)

        if frame_count < gif_length:
            frame_path = os.path.join(path, f"tmp/temp-{frame_count}.png")
            pygame.image.save(screen, frame_path)
            frames.append(Image.open(frame_path))
        else:
            frames[0].save(
                "conway.gif",
                format="GIF",
                append_images=frames[1:],
                duration=1000 / fps,
                save_all=True,
                loop=1,
            )
            print("GIF made!")
            print("Trying to empty tmp/ directory...")
            tmp_path = os.path.join(path, "tmp")
            for filename in os.listdir(tmp_path):
                file_path = os.path.join(tmp_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except:
                    print(f"Could not delete {filename} from tmp/ directory.")
            print("Exiting... hope you enjoyed!")
            sys.exit(0)

        frame_count += 1

        clock.tick(fps)

        # Render changes
        pygame.display.flip()

# To be IDLE friendly...
pygame.quit()
