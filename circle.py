import math
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, RED_RGB, GREEN_RGB

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
        # mass == area; you can round if you want integers
        return int(round(self.mass))
