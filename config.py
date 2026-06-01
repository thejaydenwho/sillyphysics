import random

# Screen
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED_RGB = (220, 60, 60)
GREEN_RGB = (60, 220, 60)

# Gravity
G = 0.0005  # tweak for feel

# Circles
MIN_CIRCLES = 5
MAX_CIRCLES = 20
MIN_RADIUS = 8
MAX_RADIUS = 35

# Green merge threshold (squared speed)
MERGE_REL_SPEED_MAX = 1.0  # px/tick
MERGE_REL_SPEED_MAX_SQ = MERGE_REL_SPEED_MAX ** 2

def random_total_circles():
    return random.randint(MIN_CIRCLES, MAX_CIRCLES)