import math
import random
from config import G, MERGE_REL_SPEED_MAX_SQ
from circle import Circle

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
    # relative speed
    rvx = c1.vx - c2.vx
    rvy = c1.vy - c2.vy
    rel_speed_sq = rvx * rvx + rvy * rvy

    if rel_speed_sq <= MERGE_REL_SPEED_MAX_SQ:
        # merge
        total_mass = c1.mass + c2.mass
        if total_mass == 0:
            return
        new_x = (c1.x * c1.mass + c2.x * c2.mass) / total_mass
        new_y = (c1.y * c1.mass + c2.y * c2.mass) / total_mass
        new_vx = (c1.vx * c1.mass + c2.vx * c2.mass) / total_mass
        new_vy = (c1.vy * c1.mass + c2.vy * c2.mass) / total_mass

        new_radius = math.sqrt(total_mass / math.pi)
        # reuse c1 as merged circle, kill c2
        c1.x = new_x
        c1.y = new_y
        c1.vx = new_vx
        c1.vy = new_vy
        c1.radius = new_radius
        c1.mass = total_mass

        c2.alive = False
        if c2.id in circles:
            del circles[c2.id]
    else:
        # optional: simple elastic bounce; for now, do nothing special
        pass

def spawn_dust_cloud(red, green, circles, id_counter):
    original_area = green.mass  # mass == area
    n_frag = random.randint(3, 7)
    frag_area = original_area / n_frag
    frag_radius = math.sqrt(frag_area / math.pi)

    new_ids = []
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
        new_ids.append(cid)

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

            # green-green
            if c1.color == "green" and c2.color == "green":
                handle_green_green_collision(c1, c2, circles)

            # red-green
            elif c1.color == "red" and c2.color == "green":
                spawn_dust_cloud(c1, c2, circles, id_counter)

            elif c1.color == "green" and c2.color == "red":
                spawn_dust_cloud(c2, c1, circles, id_counter)

            # red-red: ignore
