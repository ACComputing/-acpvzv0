"""
AC'S PVZ - A Plants vs. Zombies tribute game
Runs at 60 FPS (Windows XP era speed)
All game timings are based on 60 frames per second.
"""

import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# ==========================================
# CONSTANTS (Updated to 600x400)
# ==========================================
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_ROWS = 5
GRID_COLS = 7   # Reduced columns to fit width
CELL_SIZE = 60  # Reduced cell size
SIDEBAR_WIDTH = 180
GAME_WIDTH = GRID_COLS * CELL_SIZE
GAME_HEIGHT = GRID_ROWS * CELL_SIZE
LAWN_MOWER_WIDTH = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
DARK_BROWN = (60, 30, 10)
CYAN = (0, 255, 255)
WATER_BLUE = (64, 164, 223)
DARK_WATER = (40, 120, 180)
ICE_BLUE = (200, 230, 255)

# Stone colors for PvZ1‑style sidebar
STONE_COLOR = (120, 120, 120)
STONE_DARK = (80, 80, 80)
STONE_LIGHT = (160, 160, 160)

# Game settings
SUN_START = 50
SUN_DROP_RATE = 600          # frames between natural sun drops (10 sec at 60fps)
ZOMBIE_SPAWN_BASE = 400
PEA_SHOOT_COOLDOWN = 90      # frames between pea shots (1.5 sec at 60fps)
SUNFLOWER_GEN_RATE = 600     # frames between sun production (10 sec)

# Cooldown times (in frames at 60fps) – based on PvZ1 values
COOLDOWN_FRAMES = {
    'peashooter': 450,   # 7.5 sec
    'sunflower':  450,
    'wallnut':    1800,  # 30 sec
    'cherrybomb': 3000,  # 50 sec
    'snowpea':    450,
    'repeater':   450,
    'potatomine': 450,
    'chomper':    450,
    'puffshroom': 450,
    'lilypad':    450,
    'squash':     450
}

# Plant Data
PLANT_DATA = {
    'peashooter': {'cost': 100, 'health': 100, 'unlock': '1-1'},
    'sunflower':  {'cost': 50,  'health': 100, 'unlock': '1-1'},
    'wallnut':    {'cost': 50,  'health': 800, 'unlock': '1-4'},
    'cherrybomb': {'cost': 150, 'health': 100, 'unlock': '1-2'},
    'snowpea':    {'cost': 175, 'health': 100, 'unlock': '1-6'},
    'repeater':   {'cost': 200, 'health': 100, 'unlock': '1-8'},
    'potatomine': {'cost': 25,  'health': 100, 'unlock': '1-5'},
    'chomper':    {'cost': 150, 'health': 100, 'unlock': '1-7'},
    'puffshroom': {'cost': 0,   'health': 100, 'unlock': '2-1'},
    'lilypad':    {'cost': 25,  'health': 100, 'unlock': '2-1'},
    'squash':     {'cost': 50,  'health': 100, 'unlock': '1-3'}
}

# Zombie Data
ZOMBIE_DATA = {
    'basic':     {'health': 100, 'speed': 0.25, 'damage': 100},
    'cone':      {'health': 200, 'speed': 0.25, 'damage': 100},
    'bucket':    {'health': 400, 'speed': 0.25, 'damage': 100},
    'flag':      {'health': 100, 'speed': 0.5,  'damage': 100},
    'newspaper': {'health': 150, 'speed': 0.25, 'damage': 100},
    'pole':      {'health': 100, 'speed': 0.7,  'damage': 100},
    'football':  {'health': 500, 'speed': 0.6,  'damage': 100},
    'ducky':     {'health': 100, 'speed': 0.25, 'damage': 100}
}

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AC'S PVZ")  # Updated Title
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)       # Adjusted font size for smaller screen
small_font = pygame.font.Font(None, 20)
title_font = pygame.font.Font(None, 50) # Adjusted title font

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def check_unlock(plant_name, level_str):
    """Return True if plant is unlocked at the given level."""
    unlocks = {
        'peashooter': '1-1', 'sunflower': '1-1', 'cherrybomb': '1-2',
        'squash': '1-3', 'wallnut': '1-4', 'potatomine': '1-5',
        'snowpea': '1-6', 'chomper': '1-7', 'repeater': '1-8',
        'puffshroom': '2-1', 'lilypad': '2-1'
    }
    if plant_name not in unlocks:
        return True
    current_world, current_level = map(int, level_str.split('-'))
    req_world, req_level = map(int, unlocks[plant_name].split('-'))
    if current_world > req_world:
        return True
    if current_world == req_world and current_level >= req_level:
        return True
    return False

# ==========================================
# STONE TEXTURE
# ==========================================
def draw_stone_background(screen, rect):
    """Fill the given rectangle with a speckled stone texture."""
    pygame.draw.rect(screen, STONE_COLOR, rect)
    for _ in range(150): # Reduced speckles for smaller area
        x = random.randint(rect.left, rect.right - 1)
        y = random.randint(rect.top, rect.bottom - 1)
        if random.random() < 0.5:
            color = STONE_LIGHT
        else:
            color = STONE_DARK
        pygame.draw.circle(screen, color, (x, y), 1)

# ==========================================
# INFO SCREENS
# ==========================================
def draw_info_background(screen):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            base_color = LIGHT_GREEN
            alt_color = DARK_GREEN
            pygame.draw.rect(screen, base_color if (row+col)%2==0 else alt_color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
    sidebar_rect = pygame.Rect(GAME_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
    draw_stone_background(screen, sidebar_rect)

def display_info_screen(title, lines):
    waiting = True
    while waiting:
        draw_info_background(screen)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        title_surf = title_font.render(title, True, YELLOW)
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 40))
        y_offset = 100
        for line in lines:
            text = font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 30
        instr = small_font.render("Press ESC or click to return", True, GRAY)
        screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, SCREEN_HEIGHT-40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        clock.tick(60)

# ==========================================
# MAIN MENU
# ==========================================
def draw_menu_background(screen, frame_count):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            base_color = LIGHT_GREEN
            alt_color = DARK_GREEN
            pygame.draw.rect(screen, base_color if (row+col)%2==0 else alt_color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
    sidebar_rect = pygame.Rect(GAME_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
    draw_stone_background(screen, sidebar_rect)

def draw_menu_sun(screen):
    sun_x = 50
    sun_y = 50
    pygame.draw.circle(screen, YELLOW, (sun_x, sun_y), 20)
    pygame.draw.circle(screen, ORANGE, (sun_x, sun_y), 15)
    text = font.render("50", True, BLACK)
    screen.blit(text, (sun_x - 10, sun_y - 8))

def main_menu():
    frame_count = 0
    left_buttons = [
        ("Adventure", "adventure"),
        ("Mini-Games", "mini"),
        ("Survival", "survival"),
        ("Zen Garden", "zen"),
        ("Quit", "quit")
    ]
    right_buttons = [
        ("How to Play", "howtoplay"),
        ("Controls", "controls"),
        ("Credits", "credits"),
        ("About", "about")
    ]

    while True:
        draw_menu_background(screen, frame_count)
        draw_menu_sun(screen)

        # Title
        title_shadow = title_font.render("AC'S PVZ", True, DARK_BROWN)
        title_text = title_font.render("AC'S PVZ", True, (255, 255, 150))
        screen.blit(title_shadow, (SCREEN_WIDTH//2 - 78, 22))
        screen.blit(title_text, (SCREEN_WIDTH//2 - 80, 20))

        # Buttons
        left_x = 20
        right_x = SCREEN_WIDTH // 2 + 10
        button_width = SCREEN_WIDTH // 2 - 40
        button_height = 40
        start_y = 90
        spacing = 50

        rects = []

        # Left Column
        for i, (text, action) in enumerate(left_buttons):
            y = start_y + i * spacing
            rect = pygame.Rect(left_x, y, button_width, button_height)
            pygame.draw.rect(screen, (160, 100, 40), rect)
            pygame.draw.rect(screen, (200, 140, 60), rect.inflate(-6, -6))
            pygame.draw.rect(screen, BLACK, rect, 2)
            txt_surf = font.render(text, True, BLACK)
            screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - 8))
            rects.append((rect, action))

        # Right Column
        for i, (text, action) in enumerate(right_buttons):
            y = start_y + i * spacing
            rect = pygame.Rect(right_x, y, button_width, button_height)
            pygame.draw.rect(screen, (160, 100, 40), rect)
            pygame.draw.rect(screen, (200, 140, 60), rect.inflate(-6, -6))
            pygame.draw.rect(screen, BLACK, rect, 2)
            txt_surf = font.render(text, True, BLACK)
            screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - 8))
            rects.append((rect, action))

        pygame.display.flip()
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, action in rects:
                    if rect.collidepoint(event.pos):
                        return action
        clock.tick(60)

# ==========================================
# GAME CLASSES
# ==========================================
class Plant:
    def __init__(self, x, y, plant_type, env="day"):
        self.x = x
        self.y = y
        self.type = plant_type
        self.health = PLANT_DATA.get(plant_type, {}).get('health', 100)
        self.max_health = self.health
        self.rect = pygame.Rect(x, y, CELL_SIZE-5, CELL_SIZE-5)
        self.last_shot = 0
        self.last_sun_gen = 0
        self.exploded = False
        self.arm_timer = 0
        self.is_armed = False
        self.chewing = 0
        self.sleeping = False

        if 'shroom' in plant_type and env == "day":
            self.sleeping = True

    def update(self, current_time, zombies):
        if self.sleeping:
            return None

        if self.type == 'sunflower':
            if current_time - self.last_sun_gen > SUNFLOWER_GEN_RATE:
                self.last_sun_gen = current_time
                return ('sun', 25)

        elif self.type == 'cherrybomb' and not self.exploded:
            self.exploded = True
            return ('explode',)

        elif self.type == 'potatomine':
            if not self.is_armed:
                self.arm_timer += 1
                if self.arm_timer > 200:
                    self.is_armed = True
            else:
                for z in zombies:
                    if z.row == (self.y // CELL_SIZE) and z.rect.colliderect(self.rect):
                        self.health = 0
                        return ('mine_explode', self.x, self.y)

        elif self.type == 'chomper':
            if self.chewing > 0:
                self.chewing -= 1
            else:
                for z in zombies:
                    if z.row == (self.y // CELL_SIZE) and abs(z.x - self.x) < 30:
                        if z.type not in ('football', 'bucket'):
                            self.chewing = 300
                            return ('eat_zombie', z)
        return None

    def draw(self, screen):
        color_map = {
            'peashooter': GREEN,
            'sunflower': YELLOW,
            'wallnut': BROWN,
            'cherrybomb': RED,
            'snowpea': ICE_BLUE,
            'repeater': DARK_GREEN,
            'potatomine': BROWN if not self.is_armed else ORANGE,
            'chomper': PURPLE,
            'puffshroom': (200, 150, 255),
            'lilypad': (0, 100, 0),
            'squash': ORANGE
        }
        color = color_map.get(self.type, WHITE)
        pygame.draw.rect(screen, color, self.rect)

        if self.sleeping:
            pygame.draw.circle(screen, BLACK, self.rect.center, 5)
            text = small_font.render("Zzz", True, WHITE)
            screen.blit(text, (self.x+2, self.y-10))
        elif self.type == 'chomper' and self.chewing > 0:
            pygame.draw.rect(screen, RED, (self.x+10, self.y-5, 10, 5))

        letter = self.type[0].upper()
        text = small_font.render(letter, True, BLACK)
        screen.blit(text, (self.rect.centerx - 4, self.rect.centery - 6))

        if self.health < self.max_health:
            bar_width = self.rect.width * (self.health / self.max_health)
            pygame.draw.rect(screen, RED, (self.x, self.y-5, self.rect.width, 3))
            pygame.draw.rect(screen, GREEN, (self.x, self.y-5, bar_width, 3))

class Zombie:
    def __init__(self, row, col, z_type='basic', env='day'):
        self.row = row
        self.col = col
        self.type = z_type
        data = ZOMBIE_DATA.get(z_type, ZOMBIE_DATA['basic'])
        self.health = data['health']
        self.max_health = self.health
        self.base_speed = data['speed']
        self.speed = self.base_speed

        self.x = GAME_WIDTH + random.randint(0, 100)
        self.y = row * CELL_SIZE + 5
        self.rect = pygame.Rect(self.x, self.y, CELL_SIZE-15, CELL_SIZE-15)
        self.eating = False
        self.target_plant = None
        self.has_pole = (z_type == 'pole')
        self.angry = False
        self.slowed = 0

    def update(self, grid):
        if self.slowed > 0:
            self.slowed -= 1
            current_speed = self.speed * 0.5
        else:
            current_speed = self.speed

        if self.type == 'newspaper' and self.health < 150 and not self.angry:
            self.angry = True
            self.speed = self.base_speed * 2.0

        if self.type == 'pole' and self.has_pole:
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    plant = grid[r][c]
                    if plant and r == self.row:
                        if plant.type not in ('lilypad', 'tallnut'):
                            if abs(plant.x - self.x) < 30:
                                self.x -= 80
                                self.has_pole = False
                                return

        if not self.eating:
            self.x -= current_speed
            self.col = max(0, int(self.x / CELL_SIZE))
            self.rect.x = self.x

        front_col = max(0, int((self.x + 5) // CELL_SIZE))
        if front_col < len(grid[0]):
            plant = grid[self.row][front_col]
            if plant and not self.eating:
                self.eating = True
                self.target_plant = plant

            if self.eating and self.target_plant:
                self.target_plant.health -= 1
                if self.target_plant.health <= 0:
                    grid[self.row][front_col] = None
                    self.eating = False
                    self.target_plant = None

    def draw(self, screen):
        color_map = {
            'basic': BROWN,
            'cone': ORANGE,
            'bucket': GRAY,
            'flag': RED,
            'newspaper': PINK if self.angry else WHITE,
            'pole': YELLOW if not self.has_pole else ORANGE,
            'football': (50, 50, 50),
            'ducky': YELLOW
        }
        color = color_map.get(self.type, BROWN)
        pygame.draw.rect(screen, color, self.rect)

        if self.slowed > 0:
            pygame.draw.rect(screen, ICE_BLUE, self.rect, 2)

        text = small_font.render("Z", True, BLACK)
        screen.blit(text, (self.x+15, self.y+10))

        bar_width = self.rect.width * (self.health / self.max_health)
        pygame.draw.rect(screen, RED, (self.x, self.y-5, self.rect.width, 3))
        pygame.draw.rect(screen, GREEN, (self.x, self.y-5, bar_width, 3))

class Projectile:
    def __init__(self, x, y, target_row, damage=20, p_type='pea'):
        self.x = x
        self.y = y + CELL_SIZE//2 - 3
        self.target_row = target_row
        self.speed = 4
        self.damage = damage
        self.type = p_type
        self.rect = pygame.Rect(self.x, self.y, 6, 6)

    def move(self):
        self.x += self.speed
        self.rect.x = self.x

    def draw(self, screen):
        color = GREEN if self.type == 'pea' else ICE_BLUE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)

class Sun:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.rect = pygame.Rect(x-10, y-10, 20, 20)
        self.falling = True
        self.speed = 1

    def update(self):
        if self.falling:
            self.y += self.speed
            self.rect.y = self.y
            if self.y > GAME_HEIGHT - 30:
                self.falling = False

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), 10)
        text = small_font.render(str(self.value), True, BLACK)
        screen.blit(text, (self.x-5, self.y-6))

# ==========================================
# GAME MANAGER
# ==========================================
class Game:
    def __init__(self, level_str="1-1", mode="adventure"):
        self.mode = mode
        self.level_str = level_str
        self.world, self.sublevel = map(int, level_str.split('-'))

        if self.world == 1:
            self.env = "day"
        elif self.world == 2:
            self.env = "night"
        elif self.world == 3:
            self.env = "pool"
        else:
            self.env = "fog"

        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.water_rows = [2, 3] if self.env in ("pool", "fog") else []

        self.zombies = []
        self.projectiles = []
        self.suns = []
        self.sun_points = SUN_START
        self.frame_count = 0
        self.selected_plant = None
        self.game_over = False
        self.win = False
        self.zombies_spawned = 0
        self.zombies_to_spawn = 5 + self.sublevel * 2
        self.spawn_delay = ZOMBIE_SPAWN_BASE
        self.next_spawn = 200

        self.plant_cooldowns = {p: 0 for p in PLANT_DATA.keys()}
        self.lawn_mowers = [True] * GRID_ROWS

    def handle_click(self, pos):
        x, y = pos
        if x > GAME_WIDTH:
            self.handle_sidebar_click(x, y)
        elif not self.game_over:
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                target_cell = self.grid[row][col]
                is_water = row in self.water_rows

                if self.selected_plant:
                    p_type = self.selected_plant
                    if is_water:
                        if p_type == 'lilypad' and target_cell is None:
                            self.place_plant(row, col, 'lilypad')
                        elif target_cell and target_cell.type == 'lilypad':
                            self.place_plant(row, col, p_type)
                    else:
                        if target_cell is None:
                            self.place_plant(row, col, p_type)

    def place_plant(self, row, col, p_type):
        cost = PLANT_DATA[p_type]['cost']
        if self.sun_points >= cost:
            if self.frame_count < self.plant_cooldowns[p_type]:
                return
            self.sun_points -= cost
            new_plant = Plant(col*CELL_SIZE+2, row*CELL_SIZE+2, p_type, self.env)
            self.grid[row][col] = new_plant
            self.selected_plant = None
            self.plant_cooldowns[p_type] = self.frame_count + COOLDOWN_FRAMES[p_type]

    def handle_sidebar_click(self, x, y):
        y_index = (y - 40) // 40  # Adjusted for smaller sidebar
        plants_available = [
            'peashooter', 'sunflower', 'wallnut', 'cherrybomb',
            'snowpea', 'repeater', 'potatomine', 'chomper',
            'puffshroom', 'lilypad', 'squash'
        ]
        if 0 <= y_index < len(plants_available):
            p = plants_available[y_index]
            if check_unlock(p, self.level_str):
                if self.frame_count >= self.plant_cooldowns[p]:
                    self.selected_plant = p

    def update(self):
        if self.game_over or self.win:
            return

        self.frame_count += 1

        if self.env == "day" and self.frame_count % SUN_DROP_RATE == 0:
            self.suns.append(Sun(random.randint(50, GAME_WIDTH-50), 0, 25))

        if self.zombies_spawned < self.zombies_to_spawn:
            if self.frame_count >= self.next_spawn:
                self.spawn_zombie()
                self.next_spawn = self.frame_count + self.spawn_delay - (self.sublevel * 10)
        elif len(self.zombies) == 0:
            self.win = True

        self.update_plants()
        self.update_projectiles()
        self.update_zombies()
        self.update_suns()
        self.shooting_logic()

    def spawn_zombie(self):
        row = random.randint(0, GRID_ROWS-1)
        r = random.random()
        if self.world == 3:
            if row in self.water_rows:
                z_type = 'ducky'
            else:
                z_type = random.choice(['basic', 'cone', 'bucket'])
        else:
            if self.sublevel >= 5:
                if r < 0.2: z_type = 'pole'
                elif r < 0.4: z_type = 'newspaper'
                elif r < 0.6: z_type = 'bucket'
                else: z_type = 'basic'
            elif self.sublevel >= 3:
                if r < 0.3: z_type = 'cone'
                else: z_type = 'basic'
            else:
                z_type = 'basic'
        self.zombies.append(Zombie(row, GRID_COLS-1, z_type, self.env))
        self.zombies_spawned += 1

    def shooting_logic(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                plant = self.grid[row][col]
                if plant and not plant.sleeping:
                    if plant.type in ('peashooter', 'snowpea', 'repeater', 'puffshroom'):
                        has_target = False
                        for z in self.zombies:
                            if z.row == row and z.x > plant.x:
                                has_target = True
                                break
                        if has_target and self.frame_count - plant.last_shot > PEA_SHOOT_COOLDOWN:
                            plant.last_shot = self.frame_count
                            p_type = 'pea'
                            if plant.type == 'snowpea': p_type = 'frozen'
                            self.projectiles.append(Projectile(plant.x+CELL_SIZE, plant.y, row, p_type=p_type))
                            if plant.type == 'repeater':
                                self.projectiles.append(Projectile(plant.x+CELL_SIZE+10, plant.y, row, p_type='pea'))

    def update_plants(self):
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                plant = self.grid[r][c]
                if plant:
                    result = plant.update(self.frame_count, self.zombies)
                    if result is None: continue
                    action = result[0]
                    if action == 'explode':
                        self.cherry_explode(r, c)
                        self.grid[r][c] = None
                    elif action == 'mine_explode':
                        _, ex, ey = result
                        for z in self.zombies[:]:
                            if z.row == r and abs(z.x - ex) < 40:
                                z.health = 0
                        self.grid[r][c] = None
                    elif action == 'eat_zombie':
                        target_z = result[1]
                        if target_z in self.zombies: self.zombies.remove(target_z)
                    elif action == 'sun':
                        _, value = result
                        self.suns.append(Sun(plant.x+CELL_SIZE//2, plant.y, value))

    def cherry_explode(self, row, col):
        for z in self.zombies[:]:
            if abs(z.row - row) <= 1 and z.col >= col-1 and z.col <= col+1:
                z.health = 0

    def update_zombies(self):
        for z in self.zombies[:]:
            z.update(self.grid)
            if z.x < 0 and self.lawn_mowers[z.row]:
                self.lawn_mowers[z.row] = False
                for zombie in self.zombies[:]:
                    if zombie.row == z.row: zombie.health = 0
            if z.health <= 0:
                self.zombies.remove(z)

    def update_projectiles(self):
        for p in self.projectiles[:]:
            p.move()
            if p.x > GAME_WIDTH:
                self.projectiles.remove(p)
                continue
            for z in self.zombies:
                if z.row == p.target_row and z.rect.colliderect(p.rect):
                    z.health -= p.damage
                    if p.type == 'frozen': z.slowed = 300
                    if p in self.projectiles:
                        self.projectiles.remove(p)
                    break

    def update_suns(self):
        for s in self.suns[:]:
            s.update()
            if s.y > SCREEN_HEIGHT:
                self.suns.remove(s)

    def draw(self, screen):
        self.draw_background(screen)

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if self.grid[row][col]:
                    self.grid[row][col].draw(screen)

        for z in self.zombies: z.draw(screen)
        for p in self.projectiles: p.draw(screen)
        for s in self.suns: s.draw(screen)

        self.draw_sidebar(screen)
        self.draw_overlay(screen)

    def draw_background(self, screen):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                base_color = LIGHT_GREEN
                alt_color = DARK_GREEN
                if self.env == "night":
                    base_color = (50, 80, 50)
                    alt_color = (30, 60, 30)
                elif row in self.water_rows:
                    if (self.frame_count // 10) % 2 == 0:
                        base_color = WATER_BLUE
                        alt_color = DARK_WATER
                    else:
                        base_color = DARK_WATER
                        alt_color = WATER_BLUE
                pygame.draw.rect(screen, base_color if (row+col)%2==0 else alt_color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

            if self.lawn_mowers[row]:
                mower_rect = pygame.Rect(5, row*CELL_SIZE + CELL_SIZE//2 - 10, LAWN_MOWER_WIDTH, 20)
                pygame.draw.rect(screen, RED, mower_rect)
                pygame.draw.rect(screen, BLACK, mower_rect, 1)
            else:
                mower_rect = pygame.Rect(5, row*CELL_SIZE + CELL_SIZE//2 - 10, LAWN_MOWER_WIDTH, 20)
                pygame.draw.rect(screen, GRAY, mower_rect)
                pygame.draw.rect(screen, BLACK, mower_rect, 1)

        if GAME_HEIGHT < SCREEN_HEIGHT:
            bottom_rect = pygame.Rect(0, GAME_HEIGHT, GAME_WIDTH, SCREEN_HEIGHT - GAME_HEIGHT)
            pygame.draw.rect(screen, (50, 50, 20), bottom_rect)

    def draw_sidebar(self, screen):
        sidebar_rect = pygame.Rect(GAME_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        draw_stone_background(screen, sidebar_rect)

        text = font.render(f"Sun: {self.sun_points}", True, BLACK)
        screen.blit(text, (GAME_WIDTH+5, 5))

        plants = ['peashooter', 'sunflower', 'wallnut', 'cherrybomb',
                  'snowpea', 'repeater', 'potatomine', 'chomper',
                  'puffshroom', 'lilypad', 'squash']
        y = 35
        for p in plants:
            btn = pygame.Rect(GAME_WIDTH+5, y, SIDEBAR_WIDTH-10, 30) # Adjusted button size
            if not check_unlock(p, self.level_str):
                color = DARK_BROWN
            elif self.frame_count < self.plant_cooldowns[p]:
                color = (100, 100, 100)
            elif self.selected_plant == p:
                color = GREEN
            else:
                color = WHITE

            pygame.draw.rect(screen, color, btn)
            pygame.draw.rect(screen, BLACK, btn, 1)

            if self.frame_count < self.plant_cooldowns[p]:
                remaining = (self.plant_cooldowns[p] - self.frame_count) // 60
                timer_text = small_font.render(str(remaining), True, BLACK)
                screen.blit(timer_text, (btn.x+130, btn.y+5))

            cost = PLANT_DATA[p]['cost']
            txt = small_font.render(f"{p[:6]}({cost})", True, BLACK)
            screen.blit(txt, (btn.x+2, btn.y+5))
            y += 32

        lvl_txt = font.render(f"Lvl: {self.level_str}", True, BLACK)
        screen.blit(lvl_txt, (GAME_WIDTH+5, SCREEN_HEIGHT-50))
        mode_txt = small_font.render(f"Mode: {self.mode}", True, BLACK)
        screen.blit(mode_txt, (GAME_WIDTH+5, SCREEN_HEIGHT-25))

    def draw_overlay(self, screen):
        if self.game_over:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(128)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
            txt = font.render("GAME OVER", True, RED)
            screen.blit(txt, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2))
        elif self.win:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(128)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
            txt = font.render("LEVEL COMPLETE!", True, GREEN)
            screen.blit(txt, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2))

# ==========================================
# GAME LOOP
# ==========================================
def run_game(level_str, mode="adventure"):
    game = Game(level_str, mode)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

                for s in game.suns[:]:
                    if s.rect.collidepoint(event.pos):
                        game.sun_points += s.value
                        game.suns.remove(s)

                if game.win:
                    w, sl = map(int, level_str.split('-'))
                    sl += 1
                    if sl > 10:
                        sl = 1
                        w += 1
                    return f"{w}-{sl}"
                if game.game_over:
                    return "menu"

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60) # 60 FPS Target

def main():
    state = "menu"
    current_level = "1-1"

    while state != "quit":
        if state == "menu":
            state = main_menu()
        elif state == "adventure":
            state = run_game(current_level, "adventure")
            if state and '-' in state:
                current_level = state
                state = "adventure"
        elif state == "mini":
            state = run_game("1-1", "mini")
        elif state == "survival":
            state = run_game("1-1", "survival")
        elif state == "zen":
            state = run_game("1-1", "zen")
        elif state == "howtoplay":
            lines = [
                "Place plants to stop zombies.",
                "Collect sun to buy plants.",
                "Click sidebar, then lawn to plant.",
                "Survive the wave!"
            ]
            display_info_screen("How to Play", lines)
            state = "menu"
        elif state == "controls":
            lines = [
                "Mouse: Select and Collect.",
                "ESC: Return to menu."
            ]
            display_info_screen("Controls", lines)
            state = "menu"
        elif state == "credits":
            lines = [
                "AC'S PVZ 1.X",
                "Pygame Project",
                "Programmer: AC AND Popcap"
            ]
            display_info_screen("Credits", lines)
            state = "menu"
        elif state == "about":
            lines = [
                "AC'S PVZ",
                "Version 1.X",
                "Tribute to PvZ"
            ]
            display_info_screen("About", lines)
            state = "menu"

if __name__ == "__main__":
    main()
