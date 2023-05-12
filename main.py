# Imports
import pygame
import random
import math

# Init
pygame.init()

# FPS / clock
fps = 60
clock = pygame.time.Clock()

# Window
window_width = 1000
window_height = 800
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Boids")

# Cursor
pygame.mouse.set_cursor((8, 8), (4, 4), (0, 0, 0, 0, 0, 0, 0, 0),
                        (24, 24, 24, 231, 231, 24, 24, 24))

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
light_black = (30, 30, 30)
red = (150, 0, 0)
green = (0, 150, 0)
blue = (0, 0, 150)
grey = (85, 85, 85)
pink = (255, 105, 180)
bar_color = (45, 45, 45)

# Constant values
boid_size = 10
half_boid_size = boid_size / 2
max_speed = 8
wall_size = 30
half_wall_size = wall_size / 2


# Classes
class CreateBoid:
    def __init__(self, pos_x, pos_y):
        # Position
        self.pos_x = pos_x
        self.pos_y = pos_y

        # Movement
        self.speed_x = random.randint(-2, 2)
        self.speed_y = random.randint(-2, 2)

    # Draws the actual Boid
    def draw(self):
        pygame.draw.rect(window, green, [self.pos_x - half_boid_size,
                                         self.pos_y - half_boid_size,
                                         boid_size, boid_size])

    # Returns distance from nearby boid using a^2 + b^2 = c^2
    def distance(self, boid):
        dist_x = self.pos_x - boid.pos_x  # a
        dist_y = self.pos_y - boid.pos_y  # b
        return math.sqrt(dist_x ** 2 + dist_y ** 2)  # return c

    # Move away from flock (Don't overcrowd) - rule 1
    def move_away(self, close_boids, min_distance, weight_r1):
        if len(close_boids) < 1:
            return

        distance_x = 0
        distance_y = 0
        num_close = 0

        for boid in close_boids:
            distance = self.distance(boid)
            if distance < min_distance:
                num_close += 1
                x_difference = self.pos_x - boid.pos_x
                y_difference = self.pos_y - boid.pos_y
                if x_difference >= 0:
                    x_difference = math.sqrt(min_distance) - x_difference
                elif x_difference < 0:
                    x_difference = -math.sqrt(min_distance) - x_difference

                if y_difference >= 0:
                    y_difference = math.sqrt(min_distance) - y_difference
                elif y_difference < 0:
                    y_difference = -math.sqrt(min_distance) - y_difference

                distance_x += x_difference
                distance_y += y_difference

        if num_close == 0:
            return

        self.speed_x -= distance_x / weight_r1  # originally 5
        self.speed_y -= distance_y / weight_r1  # originally 5

    # Move in the general direction - rule 2
    def move_with(self, close_boids, weight_r2):
        if len(close_boids) < 1:
            return

        # Find average speed of boids
        avg_speed_x = 0
        avg_speed_y = 0

        for boid in close_boids:
            avg_speed_x += boid.speed_x
            avg_speed_y += boid.speed_y

        avg_speed_x /= len(close_boids)
        avg_speed_y /= len(close_boids)

        # Follow the flock
        self.speed_x += avg_speed_x / weight_r2  # originally 40
        self.speed_y += avg_speed_y / weight_r2  # originally 40

    # Move closer to other boids - rule 3
    def move_closer(self, close_boids, weight_r3):  # Boids needs to be a list
        if len(close_boids) < 1:
            return

        # Calculate average distance from all the other boids
        avg_x = 0
        avg_y = 0

        for boid in close_boids:
            if boid.pos_x == self.pos_x and boid.pos_y == self.pos_y:
                continue  # checks if the boid is just the original boid (?)

            avg_x += (self.pos_x - boid.pos_x)
            avg_y += (self.pos_y - boid.pos_y)

        avg_x /= len(close_boids)
        avg_y /= len(close_boids)

        # set speed towards group
        self.speed_x -= avg_x / weight_r3  # originally 100
        self.speed_y -= avg_y / weight_r3  # originally 100

    def react_wall(self, walls_list):
        if walls_list:
            for wall in walls_list:

                if wall.pos_x - half_boid_size < self.pos_x < wall.pos_x + wall_size + half_boid_size \
                        and wall.pos_y - half_boid_size < self.pos_y < wall.pos_y + wall_size + half_boid_size:

                    if self.pos_x < wall.pos_x:
                        self.pos_x = wall.pos_x - half_boid_size - 3
                        self.speed_x = (self.speed_x * -1) / 3

                    if self.pos_x > wall.pos_x + wall_size:
                        self.pos_x = wall.pos_x + wall_size + half_boid_size + 3
                        self.speed_x = (self.speed_x * -1) / 3

                    if self.pos_y < wall.pos_y:
                        self.pos_y = wall.pos_y - half_boid_size - 3
                        self.speed_y = (self.speed_y * -1) / 3

                    if self.pos_y > wall.pos_y + wall_size:
                        self.pos_y = wall.pos_y + wall_size + half_boid_size + 3
                        self.speed_y = (self.speed_y * -1) / 3

    def react_prey(self, close_preys, min_distance):
        if len(close_preys) < 1:
            return

        distance_x = 0
        distance_y = 0
        num_close = 0

        closest = []

        for prey in close_preys:
            distance = self.distance(prey)
            if distance < min_distance:
                num_close += 1
                x_difference = self.pos_x - prey.pos_x
                y_difference = self.pos_y - prey.pos_y
                if x_difference >= 0:
                    x_difference = math.sqrt(min_distance) - x_difference
                elif x_difference < 0:
                    x_difference = -math.sqrt(min_distance) - x_difference

                if y_difference >= 0:
                    y_difference = math.sqrt(min_distance) - y_difference
                elif y_difference < 0:
                    y_difference = -math.sqrt(min_distance) - y_difference

                distance_x += x_difference
                distance_y += y_difference

            closest.append(distance)

        if num_close == 0:
            return

        self.speed_x -= distance_x / (min(closest) / 1.8)
        self.speed_y -= distance_y / (min(closest) / 1.8)

    def react_lure(self, lures, min_distance):
        if len(lures) < 1:
            return

        for lure in lures:
            dist_x = self.pos_x - lure.pos_x
            dist_y = self.pos_y - lure.pos_y
            dist_boid_lure = math.sqrt(dist_x ** 2 + dist_y ** 2)
            if dist_boid_lure < min_distance:
                # set speed towards lure
                self.speed_x -= dist_x / 55
                self.speed_y -= dist_y / 55

    # Does the actual moving
    def move(self):
        if abs(self.speed_x) > max_speed or abs(self.speed_y) > max_speed:
            scale_factor = max_speed / max(abs(self.speed_x), abs(self.speed_y))
            self.speed_x *= scale_factor
            self.speed_y *= scale_factor

        self.pos_x += self.speed_x
        self.pos_y += self.speed_y

    # Moves boid to other end of the screen
    def border(self):
        # For X
        if self.pos_x >= window_width and self.speed_x > 0:
            self.pos_x = 0
        if self.pos_x <= 0 and self.speed_x < 0:
            self.pos_x = window_width
        # For Y (80 is the bar / menu)
        if self.pos_y >= window_height and self.speed_y > 0:
            self.pos_y = 80
        if self.pos_y <= 80 and self.speed_y < 0:
            self.pos_y = window_height


class CreateWall:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x - half_wall_size
        self.pos_y = pos_y - half_wall_size

    def draw(self):
        pygame.draw.rect(window, grey, [self.pos_x, self.pos_y,
                                        wall_size, wall_size])


class CreatePrey:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x - half_boid_size
        self.pos_y = pos_y - half_boid_size

    def draw(self):
        pygame.draw.rect(window, red, [self.pos_x, self.pos_y,
                                       boid_size, boid_size])


class CreateLure:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x - half_boid_size
        self.pos_y = pos_y - half_boid_size

    def draw(self):
        pygame.draw.rect(window, pink, [self.pos_x, self.pos_y,
                                        boid_size, boid_size])


class Slider:
    def __init__(self, pos_x, pos_y):
        pos_x /= 2
        pos_x += 190

        pos_x -= half_boid_size
        pos_y -= half_boid_size

        self.pos_x = pos_x
        self.pos_y = pos_y

    def slide(self, weight):
        pygame.draw.rect(window, white, [self.pos_x, self.pos_y + 1, boid_size, boid_size], 1)
        s_x_pos, s_y_pos = pygame.mouse.get_pos()

        if weight > 200:
            return 200
        elif weight < 1:
            return 1
        elif self.pos_x <= s_x_pos <= self.pos_x + boid_size \
                and self.pos_y <= s_y_pos <= self.pos_y + boid_size \
                and 200 >= weight >= 1 and pygame.mouse.get_pressed()[0]:
            return (s_x_pos - 190) * 2

        return weight


# Functions
def print_text(message, color, size, position):
    font = pygame.font.SysFont(None, size)
    m = font.render(message, 1, color)
    return window.blit(m, position)


# The main game loop
def main_loop():
    running = True

    # Lists
    boids = []
    walls = []
    preys = []
    lures = []

    # Weights
    weight1 = 5
    weight2 = 40
    weight3 = 100

    # React distances
    react_dist_boid = 175
    react_dist_prey = 200
    react_dist_lure = 150

    # Rules ON / OFF
    rule1 = 0
    rule2 = 0
    rule3 = 0

    # Choose block
    tool = 0
    mouse_block = 0

    while running:
        window.fill(light_black)
        pygame.draw.rect(window, bar_color, (0, 0, window_width, 80))
        clock.tick(fps)

        ###### KEYPRESS ######

        for event in pygame.event.get():
            # Quit game if exit button
            if event.type == pygame.QUIT:
                running = False

            mpos_x, mpos_y = pygame.mouse.get_pos()
            safe_x, safe_y = pygame.mouse.get_pos()

            # Mouse-press
            if event.type == pygame.MOUSEBUTTONDOWN:
                if safe_y > 80:
                    # Create and delete boid - tool 0
                    if event.button == 1 and tool == 0:  # 1 = Left click
                        boids.append(CreateBoid(mpos_x, mpos_y))
                    elif event.button == 3 and tool == 0:  # 3 = Right click
                        if boids:
                            del boids[-1]
                    # Create and delete wall - tool 1
                    if event.button == 1 and tool == 1:
                        walls.append(CreateWall(mpos_x, mpos_y))
                    elif event.button == 3 and tool == 1:
                        if walls:
                            del walls[-1]
                    # Create and delete prey - tool 2
                    if event.button == 1 and tool == 2:
                        preys.append(CreatePrey(mpos_x, mpos_y))
                    elif event.button == 3 and tool == 2:
                        if preys:
                            del preys[-1]
                    # Create and delete lure - tool 3
                    if event.button == 1 and tool == 3:
                        lures.append(CreateLure(mpos_x, mpos_y))
                    elif event.button == 3 and tool == 3:
                        if lures:
                            del lures[-1]
                # Turn block on mouse ON / OFF
                if 800 < mpos_x < 850 and 20 < mpos_y < 70:
                    mouse_block += 1

                # Set tool
                if event.button == 4 and tool < 3:  # 4 = scroll up
                    tool += 1
                elif event.button == 5 and tool > 0:  # 5 = scroll down
                    tool -= 1

            # Key-press
            if event.type == pygame.KEYDOWN:
                # Turn ON / OFF rules
                if event.key == pygame.K_1:
                    rule1 += 1
                elif event.key == pygame.K_2:
                    rule2 += 1
                elif event.key == pygame.K_3:
                    rule3 += 1
                # Clear screen (start over)
                if event.key == pygame.K_c:
                    main_loop()

            # Make multiple walls
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0] and mpos_y > 80 \
                        and tool == 1 and walls:
                    walls.append(CreateWall(mpos_x, mpos_y))

        # Blocks follows mouse
        bmpos_x, bmpos_y = pygame.mouse.get_pos()
        if bmpos_y > 80 and mouse_block % 2 == 1:
            if tool == 0 and boids:
                boids[-1] = CreateBoid(bmpos_x, bmpos_y)
            elif tool == 1 and walls:
                walls[-1] = CreateWall(bmpos_x, bmpos_y)
            elif tool == 2 and preys:
                preys[-1] = CreatePrey(bmpos_x, bmpos_y)
            elif tool == 3 and lures:
                lures[-1] = CreateLure(bmpos_x, bmpos_y)

        ###### WALL ######
        for wall in walls:
            wall.draw()

        ###### PREY ######
        for prey in preys:
            prey.draw()

        ###### LURE ######
        for lure in lures:
            lure.draw()

        ###### BOID ######

        for boid in boids:
            nearby_boids = []
            nearby_preys = []

            boid.draw()
            boid.border()
            boid.react_wall(walls)
            boid.react_lure(lures, react_dist_lure)

            for other_boid in boids:
                if other_boid == boid:
                    continue
                distance = boid.distance(other_boid)
                if distance < react_dist_boid:
                    nearby_boids.append(other_boid)

            for prey in preys:
                distance = boid.distance(prey)
                if distance < react_dist_prey:
                    nearby_preys.append(prey)

            boid.react_prey(nearby_preys, react_dist_prey)

            # Turn Rules ON or OFF
            if rule1 % 2 == 0:
                boid.move_away(nearby_boids, 30, weight1)  # RULE 1
                print_text("Rule1: ON", white, 20, (107, 8))
            else:
                print_text("Rule1: OFF", white, 20, (107, 8))
            if rule2 % 2 == 0:
                boid.move_with(nearby_boids, weight2)  # RULE 2
                print_text("Rule2: ON", white, 20, (107, 30))
            else:
                print_text("Rule2: OFF", white, 20, (107, 30))
            if rule3 % 2 == 0:
                boid.move_closer(nearby_boids, weight3)  # RULE 3
                print_text("Rule3: ON", white, 20, (107, 52))
            else:
                print_text("Rule3: OFF", white, 20, (107, 52))

            boid.move()

        ###### GRAPHICS STUFF ######
        # Show which tool is selected and mouse ON / OFF box
        pygame.draw.rect(window, white, (900, 20, 50, 50), 2)

        print_text("On mouse", white, 21, (790, 1))
        if mouse_block % 2 == 0:
            pygame.draw.rect(window, white, (800, 20, 50, 50), 2)
            print_text("OFF", white, 21, (811, 36))
        else:
            pygame.draw.rect(window, white, (800, 20, 50, 50))
            print_text("ON", light_black, 21, (814, 36))

        if tool == 0:
            print_text("Tool: Boid", white, 21, (890, 1))
            pygame.draw.rect(window, green, (925 - half_boid_size,
                                             45 - half_boid_size,
                                             boid_size, boid_size))
        elif tool == 1:
            print_text("Tool: Wall", white, 21, (890, 1))
            pygame.draw.rect(window, grey, (925 - half_wall_size,
                                            45 - half_wall_size,
                                            wall_size, wall_size))
        elif tool == 2:
            print_text("Tool: Prey", white, 21, (890, 1))  # MAYBE CHANGE SIZE?
            pygame.draw.rect(window, red, (925 - half_boid_size,
                                           45 - half_boid_size,
                                           boid_size, boid_size))
        elif tool == 3:
            print_text("Tool: Lure", white, 21, (890, 1))
            pygame.draw.rect(window, pink, (925 - half_boid_size,
                                            45 - half_boid_size,
                                            boid_size, boid_size))

        # Show FPS
        print_text("MBF: " + str(clock.tick(fps)), white, 21, \
        (window_width - 65, window_height - 25))
        # Show number of boids
        print_text("Boids: " + str(len(boids)), white, 21, (5, 1))
        # Show number of walls
        print_text("Walls: " + str(len(walls)), white, 21, (5, 20))
        # Show number of prey
        print_text("Preys: " + str(len(preys)), white, 21, (5, 40))
        # Show number of attractive blocks
        print_text("Lures: " + str(len(lures)), white, 21, (5, 60))

        #### Pretty graphics ####
        pygame.draw.line(window, white, (100, 0), (100, 79), 2)
        pygame.draw.line(window, white, (180, 0), (180, 79), 2)
        pygame.draw.line(window, white, (0, 80), (window_width, 80), 2)

        #  Slier for rule 1
        pygame.draw.line(window, white, (190, 13), (290, 13), 2)
        r_w_1 = Slider(weight1, 13)
        weight1 = r_w_1.slide(weight1)
        print_text("Weight 1: " + str(weight1), white, 21, (300, 8))

        # Slider for rule 2
        pygame.draw.line(window, white, (190, 35), (290, 35), 2)
        r_w_2 = Slider(weight2, 35)
        weight2 = r_w_2.slide(weight2)
        print_text("Weight 2: " + str(weight2), white, 21, (300, 30))

        # Slider for rule 3
        pygame.draw.line(window, white, (190, 57), (290, 57), 2)
        r_w_3 = Slider(weight3, 57)
        weight3 = r_w_3.slide(weight3)
        print_text("Weight 3: " + str(weight3), white, 21, (300, 52))

        pygame.display.update()

    pygame.quit()
    quit()


main_loop()
