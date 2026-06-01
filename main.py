import math
import random
import itertools
import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    BLACK,
    WHITE,
    RED_RGB,
    GREEN_RGB,
    random_total_circles,
    MIN_RADIUS,
    MAX_RADIUS,
)
from circle import Circle
from physics import apply_green_gravity, handle_collisions
from ui import draw_circles, draw_scoreboard

def create_random_circle(cid):
    color = random.choice(["red", "green"])
    radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
    x = random.uniform(radius, SCREEN_WIDTH - radius)
    y = random.uniform(radius, SCREEN_HEIGHT - radius)
    c = Circle(cid, x, y, radius, color)

    # tweak initial velocities
    if color == "green":
        c.vx *= 0.5
        c.vy *= 0.5
    else:  # red
        c.vx *= 1.5
        c.vy *= 1.5

    return c

def generate_circles(id_counter):
    circles = {}
    total = random_total_circles()
    for _ in range(total):
        cid = next(id_counter)
        c = create_random_circle(cid)
        circles[cid] = c
    return circles

def find_circle_at_pos(circles, pos):
    mx, my = pos
    for c in circles.values():
        dx = mx - c.x
        dy = my - c.y
        if dx * dx + dy * dy <= c.radius * c.radius:
            return c
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Red & Green Circle Gravity Toy")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    id_counter = itertools.count()
    circles = generate_circles(id_counter)

    scores = {"red": 0, "green": 0}
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0  # not heavily used, but available

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # reset
                    circles = generate_circles(id_counter)
                    scores = {"red": 0, "green": 0}

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                c = find_circle_at_pos(circles, event.pos)
                if c is not None:
                    scores[c.color] += c.score_value()

        # Update red behavior
        for c in circles.values():
            if c.color == "red":
                c.update_red_behavior()

        # Gravity for greens
        apply_green_gravity(circles)

        # Move and bounce
        for c in list(circles.values()):
            c.move()
            c.bounce_edges()

        # Collisions (green-green merge, red-green dust)
        handle_collisions(circles, id_counter)

        # Draw
        screen.fill(BLACK)
        draw_circles(screen, circles)
        draw_scoreboard(screen, font, scores)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
