# Render scale (supersampling for crisp text/UI on HiDPI screens). Every pixel
# size below is multiplied by S, so the layout is identical at any S — just
# rendered at higher resolution, which keeps text and UI sharp. S=1 reproduces
# the original look; S=2 doubles the internal resolution.
S = 2

# Maze
N = 15                       # maze is N x N cells (tunable)
CELL = 22 * S                # pixel size of one cell
WALL_T = max(3, CELL // 6)   # wall thickness in px

# Layout (portrait)
HUD_H = 96 * S
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

# Movement / animation (timing + source sprite frames — NOT scaled by S)
STEP_MS = 110              # time to glide across one cell; also hold cadence
WALK_FRAME = (32, 32)
PECK_FRAME = (48, 32)
WALK_FPS = 14
PECK_FPS = 8

# Font sizes (already scaled by S)
FONT_TITLE = 40 * S
FONT_BIG = 24 * S
FONT_HUD = 24 * S
FONT_UI = 20 * S
FONT_SMALL = 18 * S

ASSET_WALK = "assets/pigeon_walking.png"
ASSET_PECK = "assets/pigeon_pecking.png"
