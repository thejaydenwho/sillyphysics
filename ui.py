import pygame
from config import WHITE, SCREEN_WIDTH

def draw_circles(screen, circles):
    for c in circles.values():
        pygame.draw.circle(screen, c.rgb, (int(c.x), int(c.y)), int(c.radius))

def draw_scoreboard(screen, font, scores):
    # scores: dict like {"red": int, "green": int}
    lines = [
        f"Red circles: {scores.get('red', 0)}",
        f"Green circles: {scores.get('green', 0)}",
    ]
    x = SCREEN_WIDTH - 10
    y = 10
    for line in lines:
        surf = font.render(line, True, WHITE)
        rect = surf.get_rect(topright=(x, y))
        screen.blit(surf, rect)
        y += rect.height + 5
