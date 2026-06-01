import math
import random
import itertools
import pygame

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


class Circle:
    def __init__(self, cid, x, y, radius, color):
        self.id = cid
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color  # "red" or "green"
        self.mass = math.pi * radius * radius
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.alive = True

        if self.color == "red":
            self.ticks_until_direction_change = random.randint(10, 20)
        else:
            self.ticks_until_direction_change = None

    @property
    def rgb(self):
        if self.color == "red":
            return RED_RGB
        elif self.color == "green":
            return GREEN_RGB
        return (255, 255, 255)

    def update_red_behavior(self):
        if self.color != "red":
            return
        self.ticks_until_direction_change -= 1
        if self.ticks_until_direction_change <= 0:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.0)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.ticks_until_direction_change = random.randint(10, 20)

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def bounce_edges(self):
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -self.vx

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vy = -self.vy

    def area(self):
        return math.pi * self.radius * self.radius

    def score_value(self):
        return int(round(self.mass))


def circles_collide(c1, c2):
    dx = c1.x - c2.x
    dy = c1.y - c2.y
    dist_sq = dx * dx + dy * dy
    radius_sum = c1.radius + c2.radius
    return dist_sq < radius_sum * radius_sum


def apply_green_gravity(circles):
    greens = [c for c in circles.values() if c.alive and c.color == "green"]
    n = len(greens)
    for i in range(n):
        c1 = greens[i]
        for j in range(i + 1, n):
            c2 = greens[j]
            dx = c2.x - c1.x
            dy = c2.y - c1.y
            dist_sq = dx * dx + dy * dy
            if dist_sq == 0:
                continue
            dist = math.sqrt(dist_sq)
            force = G * c1.mass * c2.mass / dist_sq
            ax1 = force * dx / (dist * c1.mass)
            ay1 = force * dy / (dist * c1.mass)
            ax2 = -force * dx / (dist * c2.mass)
            ay2 = -force * dy / (dist * c2.mass)
            c1.vx += ax1
            c1.vy += ay1
            c2.vx += ax2
            c2.vy += ay2


def handle_green_green_collision(c1, c2, circles):
    rvx = c1.vx - c2.vx
    rvy = c1.vy - c2.vy
    rel_speed_sq = rvx * rvx + rvy * rvy

    if rel_speed_sq <= MERGE_REL_SPEED_MAX_SQ:
        total_mass = c1.mass + c2.mass
        if total_mass == 0:
            return
        new_x = (c1.x * c1.mass + c2.x * c2.mass) / total_mass
        new_y = (c1.y * c1.mass + c2.y * c2.mass) / total_mass
        new_vx = (c1.vx * c1.mass + c2.vx * c2.mass) / total_mass
        new_vy = (c1.vy * c1.mass + c2.vy * c2.mass) / total_mass

        new_radius = math.sqrt(total_mass / math.pi)
        c1.x = new_x
        c1.y = new_y
        c1.vx = new_vx
        c1.vy = new_vy
        c1.radius = new_radius
        c1.mass = total_mass

        c2.alive = False
        if c2.id in circles:
            del circles[c2.id]


def spawn_dust_cloud(red, green, circles, id_counter):
    original_area = green.mass
    n_frag = random.randint(3, 7)
    frag_area = original_area / n_frag
    frag_radius = math.sqrt(frag_area / math.pi)

    for i in range(n_frag):
        angle = 2 * math.pi * i / n_frag
        offset = red.radius + frag_radius + 2
        x = red.x + math.cos(angle) * offset
        y = red.y + math.sin(angle) * offset
        cid = next(id_counter)
        frag = Circle(cid, x, y, frag_radius, "green")
        frag.vx = 0.0
        frag.vy = 0.0
        circles[cid] = frag

    green.alive = False
    if green.id in circles:
        del circles[green.id]


def handle_collisions(circles, id_counter):
    ids = list(circles.keys())
    n = len(ids)
    for i in range(n):
        if ids[i] not in circles:
            continue
        c1 = circles[ids[i]]
        if not c1.alive:
            continue
        for j in range(i + 1, n):
            if ids[j] not in circles:
                continue
            c2 = circles[ids[j]]
            if not c2.alive:
                continue

            if not circles_collide(c1, c2):
                continue

            if c1.color == "green" and c2.color == "green":
                handle_green_green_collision(c1, c2, circles)
            elif c1.color == "red" and c2.color == "green":
                spawn_dust_cloud(c1, c2, circles, id_counter)
            elif c1.color == "green" and c2.color == "red":
                spawn_dust_cloud(c2, c1, circles, id_counter)


def draw_circles(screen, circles):
    for c in circles.values():
        pygame.draw.circle(screen, c.rgb, (int(c.x), int(c.y)), int(c.radius))


def draw_scoreboard(screen, font, scores):
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


def create_random_circle(cid):
    color = random.choice(["red", "green"])
    radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
    x = random.uniform(radius, SCREEN_WIDTH - radius)
    y = random.uniform(radius, SCREEN_HEIGHT - radius)
    c = Circle(cid, x, y, radius, color)

    if color == "green":
        c.vx *= 0.5
        c.vy *= 0.5
    else:
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
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    circles = generate_circles(id_counter)
                    scores = {"red": 0, "green": 0}
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                c = find_circle_at_pos(circles, event.pos)
                if c is not None:
                    scores[c.color] += c.score_value()

        for c in circles.values():
            if c.color == "red":
                c.update_red_behavior()

        apply_green_gravity(circles)

        for c in list(circles.values()):
            c.move()
            c.bounce_edges()

        handle_collisions(circles, id_counter)

        screen.fill(BLACK)
        draw_circles(screen, circles)
        draw_scoreboard(screen, font, scores)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
