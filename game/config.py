# Maze
N = 15                     # maze is N x N cells (tunable)
CELL = 22                  # pixel size of one cell
WALL_T = max(3, CELL // 6) # wall thickness in px

# Layout (portrait)
HUD_H = 96
WIDTH = N * CELL
HEIGHT = N * CELL + HUD_H
FPS = 60

# Park-hedge palette
BG = (21, 17, 15)
WALL = (63, 107, 57)
WALL_HI = (81, 145, 69)
PATH = (217, 196, 154)
PATH_ALT = (205, 183, 140)
SEED = (244, 180, 0)
TEXT = (236, 229, 218)
TEXT_DIM = (169, 159, 147)
BUTTON = (81, 145, 69)
BUTTON_TEXT = (21, 17, 15)

# Movement / animation
STEP_MS = 110              # time to glide across one cell; also hold cadence
WALK_FRAME = (32, 32)
PECK_FRAME = (48, 32)
WALK_FPS = 14
PECK_FPS = 8

ASSET_WALK = "assets/pigeon_walking.png"
ASSET_PECK = "assets/pigeon_pecking.png"
