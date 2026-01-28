import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
DARK_YELLOW = (180, 180, 0)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
GREEN = (34, 139, 34)
DARK_GRAY = (70, 70, 70)
RED = (220, 20, 60)
DARK_RED = (150, 10, 40)
BLUE = (30, 144, 255)
BROWN = (139, 69, 19)
DARK_BROWN = (90, 45, 12)

# Game States
STATE_MENU = 'MENU'
STATE_PLAYING = 'PLAYING'
STATE_GAMEOVER = 'GAMEOVER'

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crossy Road")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)


def draw_voxel_rect(surface, x, y, width, height, top_color, side_color, depth=8):
    """
    Draw a pseudo-3D voxel-style rectangle
    
    Args:
        surface: Pygame surface to draw on
        x, y: Bottom-left position of the voxel
        width, height: Dimensions of the top face
        top_color: Color of the top face
        side_color: Color of the side face
        depth: Height of the 3D effect (pixels)
    """
    # Draw the side (darker rectangle at original position)
    side_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, side_color, side_rect)
    
    # Draw the top (main color shifted up)
    top_rect = pygame.Rect(x, y - depth, width, height)
    pygame.draw.rect(surface, top_color, top_rect)
    
    # Draw connecting edges to make it look 3D
    # Left edge
    pygame.draw.polygon(surface, side_color, [
        (x, y),
        (x, y - depth),
        (x, y - depth + height),
        (x, y + height)
    ])
    
    # Right edge (slightly lighter for depth)
    edge_color = tuple(min(255, int(c * 1.1)) for c in side_color)
    pygame.draw.polygon(surface, edge_color, [
        (x + width, y),
        (x + width, y - depth),
        (x + width, y - depth + height),
        (x + width, y + height)
    ])


class Car:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 2  # Cars are 2 tiles wide
        self.height = TILE_SIZE - 4  # Slightly smaller than lane height
        self.speed = speed
        self.direction = direction  # 1 for right, -1 for left
        self.color = RED
        self.dark_color = DARK_RED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        """Move the car horizontally"""
        self.x += self.speed * self.direction
        self.rect.x = self.x
        
        # Check if car is off screen
        if self.direction > 0:  # Moving right
            return self.x > SCREEN_WIDTH
        else:  # Moving left
            return self.x + self.width < 0
    
    def move_down(self, dy):
        """Move car down (for camera scrolling)"""
        self.y += dy
        self.rect.y = self.y
    
    def draw(self, surface):
        """Draw the car with voxel effect, windows, and headlights"""
        # Draw main car body with voxel effect
        draw_voxel_rect(surface, self.x, self.y, self.width, self.height, 
                       self.color, self.dark_color, depth=8)
        
        # Draw windows (darker rectangle on top of car body)
        window_width = self.width * 0.5
        window_height = self.height * 0.5
        window_x = self.x + (self.width - window_width) / 2
        window_y = self.y - 8 + (self.height - window_height) / 2  # -8 accounts for voxel depth
        
        # Very dark color for windows
        window_color = (30, 30, 30)
        pygame.draw.rect(surface, window_color, 
                        (int(window_x), int(window_y), int(window_width), int(window_height)))
        
        # Draw headlights (two tiny yellow circles at the front)
        headlight_radius = 3
        headlight_y = self.y - 8 + self.height / 2  # Center vertically on the top of the voxel
        
        if self.direction > 0:  # Moving right, headlights on the right side
            headlight_x = self.x + self.width - headlight_radius * 2
            # Two headlights stacked vertically
            pygame.draw.circle(surface, YELLOW, 
                             (int(headlight_x), int(headlight_y - 5)), headlight_radius)
            pygame.draw.circle(surface, YELLOW, 
                             (int(headlight_x), int(headlight_y + 5)), headlight_radius)
        else:  # Moving left, headlights on the left side
            headlight_x = self.x + headlight_radius * 2
            # Two headlights stacked vertically
            pygame.draw.circle(surface, YELLOW, 
                             (int(headlight_x), int(headlight_y - 5)), headlight_radius)
            pygame.draw.circle(surface, YELLOW, 
                             (int(headlight_x), int(headlight_y + 5)), headlight_radius)


class Log:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 3  # Logs are 3 tiles wide (larger than cars)
        self.height = TILE_SIZE - 4  # Slightly smaller than lane height
        self.speed = speed
        self.direction = direction  # 1 for right, -1 for left
        self.color = BROWN
        self.dark_color = DARK_BROWN
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        """Move the log horizontally"""
        self.x += self.speed * self.direction
        self.rect.x = self.x
        
        # Check if log is off screen
        if self.direction > 0:  # Moving right
            return self.x > SCREEN_WIDTH
        else:  # Moving left
            return self.x + self.width < 0
    
    def move_down(self, dy):
        """Move log down (for camera scrolling)"""
        self.y += dy
        self.rect.y = self.y
    
    def draw(self, surface):
        """Draw the log with voxel effect and wood grain"""
        # Draw main log body with voxel effect
        draw_voxel_rect(surface, self.x, self.y, self.width, self.height, 
                       self.color, self.dark_color, depth=8)
        
        # Draw wood grain (three thin dark-brown horizontal lines)
        grain_color = (60, 30, 10)  # Very dark brown for wood grain
        grain_y_top = self.y - 8  # Top surface of the voxel
        
        # Three horizontal lines at different positions
        grain_positions = [0.25, 0.5, 0.75]  # Percentages across the height
        
        for pos in grain_positions:
            grain_y = grain_y_top + self.height * pos
            # Draw thin line across the length of the log
            pygame.draw.line(surface, grain_color, 
                           (int(self.x), int(grain_y)), 
                           (int(self.x + self.width), int(grain_y)), 
                           2)  # Line thickness of 2 pixels


class Lane:
    def __init__(self, y, lane_type):
        self.rect = pygame.Rect(0, y, SCREEN_WIDTH, TILE_SIZE)
        self.type = lane_type  # 'GRASS', 'ROAD', or 'RIVER'
        self.cars = []
        self.logs = []
        
        # Set color based on type
        if self.type == 'GRASS':
            self.color = GREEN
        elif self.type == 'ROAD':
            self.color = DARK_GRAY
            # Road lanes have cars with random speed and direction
            self.car_speed = random.randint(2, 5)
            self.car_direction = random.choice([-1, 1])  # -1 left, 1 right
            # Random spawn chance per frame (lower = more frequent)
            self.spawn_chance = random.uniform(0.01, 0.03)  # 1-3% chance per frame
            self.min_car_spacing = random.randint(200, 400)  # Much larger spacing: 200-400 pixels (5-10 tiles)
        else:  # RIVER
            self.color = BLUE
            # River lanes have logs with slower speeds
            self.log_speed = random.randint(1, 3)  # Slower than cars
            self.log_direction = random.choice([-1, 1])  # -1 left, 1 right
            # Random spawn chance per frame
            self.spawn_chance = random.uniform(0.01, 0.025)  # 1-2.5% chance per frame
            self.min_log_spacing = random.randint(150, 300)  # Spacing between logs
    
    def spawn_car(self):
        """Spawn a new car at the edge of the screen"""
        if self.car_direction > 0:  # Moving right, spawn on left
            x = -TILE_SIZE * 2
        else:  # Moving left, spawn on right
            x = SCREEN_WIDTH
        
        car = Car(x, self.rect.y + 2, self.car_speed, self.car_direction)
        self.cars.append(car)
    
    def spawn_log(self):
        """Spawn a new log at the edge of the screen"""
        if self.log_direction > 0:  # Moving right, spawn on left
            x = -TILE_SIZE * 3
        else:  # Moving left, spawn on right
            x = SCREEN_WIDTH
        
        log = Log(x, self.rect.y + 2, self.log_speed, self.log_direction)
        self.logs.append(log)
    
    def can_spawn_car(self):
        """Check if there's enough space to spawn a new car"""
        if not self.cars:
            return True
        
        # Check the most recently spawned car
        last_car = self.cars[-1]
        
        # Calculate distance from spawn point to the last car
        # We want to ensure the last car has moved far enough into the screen
        if self.car_direction > 0:  # Moving right, cars spawn from left
            # Last car needs to be well into the screen before spawning next
            distance = last_car.x
        else:  # Moving left, cars spawn from right
            # Last car needs to have moved well away from right edge
            distance = SCREEN_WIDTH - (last_car.x + last_car.width)
        
        # Require much larger spacing - at least 200-400 pixels (5-10 tiles)
        return distance >= self.min_car_spacing
    
    def can_spawn_log(self):
        """Check if there's enough space to spawn a new log"""
        if not self.logs:
            return True
        
        # Check the most recently spawned log
        last_log = self.logs[-1]
        
        # Calculate distance from spawn point to the last log
        if self.log_direction > 0:  # Moving right, logs spawn from left
            distance = last_log.x
        else:  # Moving left, logs spawn from right
            distance = SCREEN_WIDTH - (last_log.x + last_log.width)
        
        return distance >= self.min_log_spacing
    
    def update(self):
        """Update cars/logs in this lane"""
        if self.type == 'ROAD':
            # Random chance to spawn a car each frame
            if random.random() < self.spawn_chance and self.can_spawn_car():
                self.spawn_car()
            
            # Update all cars and remove those off screen
            cars_to_remove = []
            for car in self.cars:
                if car.update():  # Returns True if off screen
                    cars_to_remove.append(car)
            
            for car in cars_to_remove:
                self.cars.remove(car)
        
        elif self.type == 'RIVER':
            # Random chance to spawn a log each frame
            if random.random() < self.spawn_chance and self.can_spawn_log():
                self.spawn_log()
            
            # Update all logs and remove those off screen
            logs_to_remove = []
            for log in self.logs:
                if log.update():  # Returns True if off screen
                    logs_to_remove.append(log)
            
            for log in logs_to_remove:
                self.logs.remove(log)
    
    def move_down(self, dy):
        """Move lane down by dy pixels"""
        self.rect.y += dy
        # Also move all cars and logs in this lane
        for car in self.cars:
            car.move_down(dy)
        for log in self.logs:
            log.move_down(dy)
    
    def draw(self, surface):
        """Draw the lane and its cars/logs"""
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw cars if this is a road
        if self.type == 'ROAD':
            for car in self.cars:
                car.draw(surface)
        
        # Draw logs if this is a river
        elif self.type == 'RIVER':
            for log in self.logs:
                log.draw(surface)


class LaneManager:
    def __init__(self, start_y=0):
        self.lanes = []
        self.camera_y = start_y - SCREEN_HEIGHT * 0.6  # Start camera so player is in lower part of screen
        
        # Initialize lanes around the player's starting position
        # Create lanes from player position and going upward (negative Y)
        for i in range(30):
            y = start_y - i * TILE_SIZE  # Start at player Y and go up
            
            # Choose lane type with rules: no river after road, no road after river
            if i == 0:
                lane_type = 'GRASS'  # First lane is always grass
            else:
                prev_lane_type = self.lanes[-1].type
                lane_type = self.get_valid_lane_type(prev_lane_type)
            
            self.lanes.append(Lane(y, lane_type))
        
        # Make sure first 5 lanes are grass for safe starting area
        for i in range(5):
            self.lanes[i].type = 'GRASS'
            self.lanes[i].color = GREEN
    
    def get_valid_lane_type(self, prev_lane_type):
        """Get a valid lane type that can follow the previous lane type"""
        if prev_lane_type == 'ROAD':
            # After road: can be grass or road (not river)
            return random.choice(['GRASS', 'ROAD'])
        elif prev_lane_type == 'RIVER':
            # After river: can be grass or river (not road)
            return random.choice(['GRASS', 'RIVER'])
        else:  # prev_lane_type == 'GRASS'
            # After grass: can be anything
            return random.choice(['GRASS', 'ROAD', 'RIVER'])
    
    def update_camera(self, player_world_y):
        """Update camera to follow player with a dead zone and smooth interpolation"""
        # Dead zone - camera only moves if player is in upper 60% of screen
        target_camera_y = player_world_y - SCREEN_HEIGHT * 0.6
        
        # Smooth camera follow with lerp (linear interpolation)
        # Instead of jumping instantly, smoothly move toward target
        if self.camera_y > target_camera_y:
            # Lerp factor: 0.1 = smooth, 0.5 = snappier, 1.0 = instant
            lerp_factor = 0.15
            self.camera_y += (target_camera_y - self.camera_y) * lerp_factor
        
        # Generate new lanes ahead of camera (upward direction, negative Y)
        if self.lanes:
            highest_lane_y = self.lanes[-1].rect.y
        else:
            highest_lane_y = 0
            
        while highest_lane_y > self.camera_y - SCREEN_HEIGHT:
            new_y = highest_lane_y - TILE_SIZE
            # Get the previous lane type to determine valid next types
            prev_lane_type = self.lanes[-1].type
            lane_type = self.get_valid_lane_type(prev_lane_type)
            new_lane = Lane(new_y, lane_type)
            self.lanes.append(new_lane)
            highest_lane_y = new_y
        
        # Remove lanes that are far behind camera (lanes below the visible area)
        # Since we're moving upward (negative Y), we want to keep lanes that are NOT too far below
        # Keep lanes that are above camera_y (lower values) or within 2 screens below
        self.lanes = [lane for lane in self.lanes if lane.rect.y < self.camera_y + SCREEN_HEIGHT * 2]
    
    def update(self):
        """Update all lanes (spawns and moves cars)"""
        for lane in self.lanes:
            lane.update()
    
    def check_collision(self, player_rect):
        """Check if player collides with any car"""
        for lane in self.lanes:
            if lane.type == 'ROAD':
                for car in lane.cars:
                    if player_rect.colliderect(car.rect):
                        return True
        return False
    
    def get_player_lane(self, player_y):
        """Get the lane the player is currently on"""
        for lane in self.lanes:
            # Check if player's Y position is within this lane
            if lane.rect.y <= player_y < lane.rect.y + TILE_SIZE:
                return lane
        return None
    
    def handle_river_logic(self, player):
        """Handle river physics: player must be on a log or drown"""
        player_lane = self.get_player_lane(player.y)
        
        if player_lane and player_lane.type == 'RIVER':
            # Player is on a river - check if they're on a log
            on_log = False
            
            for log in player_lane.logs:
                if player.rect.colliderect(log.rect):
                    on_log = True
                    # Move player with the log (parenting)
                    player.x += log.speed * log.direction
                    player.rect.x = player.x
                    break
            
            # If not on any log, player drowns
            if not on_log:
                return True  # Game over
            
            # Check if player was pushed off screen by log
            if player.x < 0 or player.x + player.size > SCREEN_WIDTH:
                return True  # Game over
        
        return False  # Player is safe
    
    def draw(self, surface):
        """Draw all lanes with camera offset"""
        for lane in self.lanes:
            # Calculate screen position based on camera
            screen_y = lane.rect.y - self.camera_y
            
            # Only draw if on screen
            if -TILE_SIZE <= screen_y <= SCREEN_HEIGHT:
                # Draw lane
                pygame.draw.rect(surface, lane.color, (0, screen_y, SCREEN_WIDTH, TILE_SIZE))
                
                # Draw cars
                if lane.type == 'ROAD':
                    for car in lane.cars:
                        car_screen_y = car.y - self.camera_y
                        # Update car's drawing position temporarily for voxel rendering
                        original_y = car.y
                        car.y = car_screen_y
                        car.draw(surface)
                        car.y = original_y  # Restore world position
                
                # Draw logs
                elif lane.type == 'RIVER':
                    for log in lane.logs:
                        log_screen_y = log.y - self.camera_y
                        # Update log's drawing position temporarily for voxel rendering
                        original_y = log.y
                        log.y = log_screen_y
                        log.draw(surface)
                        log.y = original_y  # Restore world position


def draw_menu(surface, menu_cars):
    """Draw the menu screen with title, instructions, and background cars"""
    # Fill background with green
    surface.fill(GREEN)
    
    # Draw some decorative road lanes in the background
    for i in range(3):
        lane_y = 150 + i * 120
        pygame.draw.rect(surface, DARK_GRAY, (0, lane_y, SCREEN_WIDTH, TILE_SIZE))
    
    # Update and draw background cars
    for car in menu_cars:
        car.update()
        car.draw(surface)
        
        # Reset car position if it goes off screen
        if car.direction > 0 and car.x > SCREEN_WIDTH:
            car.x = -car.width
        elif car.direction < 0 and car.x + car.width < 0:
            car.x = SCREEN_WIDTH
    
    # Semi-transparent overlay for better text readability
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(120)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Draw title
    title_font = pygame.font.Font(None, 92)
    title_text = title_font.render('CROSSY ROAD', True, YELLOW)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    
    # Draw title shadow for depth
    shadow_text = title_font.render('CROSSY ROAD', True, DARK_GRAY)
    shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 - 76))
    surface.blit(shadow_text, shadow_rect)
    surface.blit(title_text, title_rect)
    
    # Draw instruction text
    instruction_text = font.render('Press SPACE to Start', True, WHITE)
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    surface.blit(instruction_text, instruction_rect)
    
    # Draw controls text
    controls_font = pygame.font.Font(None, 28)
    controls_text = controls_font.render('Use Arrow Keys to Move', True, WHITE)
    controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    surface.blit(controls_text, controls_rect)


def draw_ui(surface, score):
    """Draw the score UI at the top of the screen"""
    score_text = font.render(f'Score: {score}', True, WHITE)
    surface.blit(score_text, (10, 10))


def draw_game_over(surface, score):
    """Draw game over screen"""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Game over text
    game_over_text = large_font.render('GAME OVER', True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    surface.blit(game_over_text, game_over_rect)
    
    # Score text
    score_text = font.render(f'Final Score: {score}', True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    surface.blit(score_text, score_rect)
    
    # Restart instruction
    restart_text = font.render('Press R to Restart', True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    surface.blit(restart_text, restart_rect)
    
    # Menu instruction
    menu_text = font.render('Press M for Menu', True, WHITE)
    menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
    surface.blit(menu_text, menu_rect)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y  # World Y position
        self.color = YELLOW
        self.dark_color = DARK_YELLOW
        self.size = TILE_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.score = 0  # Track highest lane reached
        self.highest_y = y  # Track highest Y position (lower/more negative values = further up)
        
        # Hop animation properties
        self.is_hopping = False
        self.hop_progress = 0  # 0.0 to 1.0
        self.hop_speed = 0.15  # How fast the hop completes (higher = faster)
        
        # Facing direction: 'up', 'down', 'left', 'right'
        self.facing = 'up'  # Default facing up
    
    def move(self, dx, dy):
        """Move player by dx, dy tiles in world space"""
        new_x = self.x + dx * TILE_SIZE
        new_y = self.y + dy * TILE_SIZE
        
        # Update facing direction
        if dx < 0:
            self.facing = 'left'
        elif dx > 0:
            self.facing = 'right'
        elif dy < 0:
            self.facing = 'up'
        elif dy > 0:
            self.facing = 'down'
        
        # Keep player within horizontal bounds
        if dx != 0:  # Horizontal movement
            if 0 <= new_x <= SCREEN_WIDTH - self.size:
                self.x = new_x
                self.rect.x = self.x
                # Trigger hop animation
                self.is_hopping = True
                self.hop_progress = 0
        
        # Vertical movement
        if dy != 0:
            self.y = new_y
            self.rect.y = self.y
            # Trigger hop animation
            self.is_hopping = True
            self.hop_progress = 0
            
            if dy < 0:  # Moving up (negative Y in world space)
                # Update score when moving up
                if self.y < self.highest_y:
                    self.highest_y = self.y
                    self.score += 1
    
    def update(self):
        """Update hop animation"""
        if self.is_hopping:
            self.hop_progress += self.hop_speed
            if self.hop_progress >= 1.0:
                self.hop_progress = 1.0
                self.is_hopping = False
    
    def get_hop_offset(self):
        """Calculate the vertical offset for the hop animation using sine wave"""
        if not self.is_hopping:
            return 8  # Default voxel depth
        
        # Use sine wave for smooth hop animation
        # sin goes from 0 -> 1 -> 0 over the range 0 -> pi
        hop_height = math.sin(self.hop_progress * math.pi) * 12  # Max additional height of 12 pixels
        return 8 + hop_height  # Base depth of 8 + animation offset
    
    def get_screen_y(self, camera_y):
        """Get player's Y position on screen based on camera"""
        return self.y - camera_y
    
    def reset(self, x, y):
        """Reset player to starting position"""
        self.x = x
        self.y = y
        self.rect.x = self.x
        self.rect.y = self.y
        self.score = 0
        self.highest_y = y
        self.is_hopping = False
        self.hop_progress = 0
        self.facing = 'up'
    
    def draw(self, surface, camera_y):
        """Draw the chicken player on the screen with camera offset and voxel effect"""
        screen_y = self.y - camera_y
        hop_offset = self.get_hop_offset()
        
        # Body dimensions (larger, main body)
        body_width = self.size * 0.75
        body_height = self.size * 0.6
        body_x = self.x + (self.size - body_width) / 2
        body_y = screen_y + self.size * 0.3
        
        # Head dimensions (smaller, on top of body)
        head_size = self.size * 0.5
        
        # Head position changes based on facing direction
        head_offset_x = 0
        head_offset_y = 0
        
        if self.facing == 'up':
            head_offset_y = -head_size * 0.3  # Head slightly forward (up)
        elif self.facing == 'down':
            head_offset_y = head_size * 0.3  # Head slightly back (down)
        elif self.facing == 'left':
            head_offset_x = -head_size * 0.4  # Head to the left
        elif self.facing == 'right':
            head_offset_x = head_size * 0.4  # Head to the right
        
        head_x = self.x + (self.size - head_size) / 2 + head_offset_x
        head_y = screen_y + self.size * 0.1 + head_offset_y
        
        # Comb dimensions (tiny red rectangle on top of head)
        comb_width = head_size * 0.3
        comb_height = head_size * 0.25
        comb_x = head_x + (head_size - comb_width) / 2 + head_offset_x * 0.5
        comb_y = head_y - comb_height * 0.5 + head_offset_y * 0.5
        
        # Draw body (white with light gray shadow)
        draw_voxel_rect(surface, int(body_x), int(body_y), 
                       int(body_width), int(body_height), 
                       WHITE, (200, 200, 200), depth=int(hop_offset))
        
        # Draw head (white with light gray shadow)
        draw_voxel_rect(surface, int(head_x), int(head_y), 
                       int(head_size), int(head_size), 
                       WHITE, (200, 200, 200), depth=int(hop_offset))
        
        # Draw comb (red with dark red shadow)
        draw_voxel_rect(surface, int(comb_x), int(comb_y), 
                       int(comb_width), int(comb_height), 
                       RED, DARK_RED, depth=int(hop_offset * 0.8))
        
        # Define orange color for beak
        ORANGE = (255, 165, 0)
        DARK_ORANGE = (200, 120, 0)
        
        # Beak dimensions and position (changes based on facing)
        beak_width = head_size * 0.2
        beak_height = head_size * 0.15
        
        if self.facing == 'left':
            # Beak points left
            beak_x = head_x - beak_width * 0.8
            beak_y = head_y + head_size * 0.5 - beak_height / 2
        elif self.facing == 'right':
            # Beak points right
            beak_x = head_x + head_size - beak_width * 0.2
            beak_y = head_y + head_size * 0.5 - beak_height / 2
        elif self.facing == 'up':
            # Beak points up/forward
            beak_x = head_x + head_size * 0.5 - beak_width / 2
            beak_y = head_y - beak_height * 0.5
        else:  # down
            # Beak points down/back
            beak_x = head_x + head_size * 0.5 - beak_width / 2
            beak_y = head_y + head_size - beak_height * 0.5
        
        # Draw beak (small orange voxel)
        draw_voxel_rect(surface, int(beak_x), int(beak_y), 
                       int(beak_width), int(beak_height), 
                       ORANGE, DARK_ORANGE, depth=int(hop_offset * 0.6))
        
        # Draw eyes (small black squares on the sides of the head)
        eye_size = 3
        # Calculate the top of the head (accounting for voxel depth)
        head_top_y = head_y - hop_offset
        
        if self.facing == 'left':
            # Show one eye on the left side
            eye_x = head_x + head_size * 0.15
            eye_y = head_top_y + head_size * 0.35
            pygame.draw.rect(surface, BLACK, (int(eye_x), int(eye_y), eye_size, eye_size))
        elif self.facing == 'right':
            # Show one eye on the right side
            eye_x = head_x + head_size * 0.85 - eye_size
            eye_y = head_top_y + head_size * 0.35
            pygame.draw.rect(surface, BLACK, (int(eye_x), int(eye_y), eye_size, eye_size))
        else:  # up or down - show both eyes
            # Left eye
            eye_x_left = head_x + head_size * 0.25
            eye_y = head_top_y + head_size * 0.35
            pygame.draw.rect(surface, BLACK, (int(eye_x_left), int(eye_y), eye_size, eye_size))
            # Right eye
            eye_x_right = head_x + head_size * 0.75 - eye_size
            pygame.draw.rect(surface, BLACK, (int(eye_x_right), int(eye_y), eye_size, eye_size))


def main():
    # Create player in world space at bottom of screen
    start_x = SCREEN_WIDTH // 2 - TILE_SIZE // 2
    start_y = SCREEN_HEIGHT - TILE_SIZE * 3  # Start near bottom
    player = Player(start_x, start_y)
    
    # Create lane manager with player's starting position
    lane_manager = LaneManager(start_y)
    
    # Game state
    game_state = STATE_MENU
    
    # Create dummy cars for menu background
    menu_cars = []
    for i in range(6):
        car_y = 150 + (i // 2) * 120 + 5
        car_speed = random.randint(2, 4)
        car_direction = 1 if i % 2 == 0 else -1
        car_x = random.randint(0, SCREEN_WIDTH) if car_direction > 0 else random.randint(0, SCREEN_WIDTH)
        menu_cars.append(Car(car_x, car_y, car_speed, car_direction))
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle movement with arrow keys (KEYDOWN for grid-based movement)
            if event.type == pygame.KEYDOWN:
                if game_state == STATE_MENU:
                    # Start game when SPACE is pressed
                    if event.key == pygame.K_SPACE:
                        game_state = STATE_PLAYING
                        # Reset game when starting from menu
                        player.reset(start_x, start_y)
                        lane_manager = LaneManager(start_y)
                
                elif game_state == STATE_GAMEOVER:
                    # Handle restart
                    if event.key == pygame.K_r:
                        # Reset game and continue playing
                        player.reset(start_x, start_y)
                        lane_manager = LaneManager(start_y)
                        game_state = STATE_PLAYING
                    elif event.key == pygame.K_m:
                        # Return to menu
                        game_state = STATE_MENU
                        player.reset(start_x, start_y)
                        lane_manager = LaneManager(start_y)
                
                elif game_state == STATE_PLAYING:
                    # Normal game controls
                    if event.key == pygame.K_LEFT:
                        player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0)
                    elif event.key == pygame.K_UP:
                        player.move(0, -1)  # Negative Y = move up
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1)  # Positive Y = move down
        
        # Update game based on state
        if game_state == STATE_PLAYING:
            # Update camera to follow player
            lane_manager.update_camera(player.y)
            
            # Update player animation
            player.update()
            
            # Update game state
            lane_manager.update()  # Update all lanes and cars
            
            # Handle river logic (player must be on log or drown)
            if lane_manager.handle_river_logic(player):
                game_state = STATE_GAMEOVER
            
            # Check for collisions with cars
            if lane_manager.check_collision(player.rect):
                game_state = STATE_GAMEOVER
            
            # Check if player fell off the bottom of the screen
            if player.get_screen_y(lane_manager.camera_y) > SCREEN_HEIGHT:
                game_state = STATE_GAMEOVER
        
        # Render based on state
        if game_state == STATE_MENU:
            draw_menu(screen, menu_cars)
        
        elif game_state == STATE_PLAYING:
            # Fill background
            screen.fill(GREEN)
            
            # Draw lanes and cars with camera offset
            lane_manager.draw(screen)
            
            # Draw player with camera offset
            player.draw(screen, lane_manager.camera_y)
            
            # Draw UI
            draw_ui(screen, player.score)
        
        elif game_state == STATE_GAMEOVER:
            # Keep the game screen visible in background
            screen.fill(GREEN)
            lane_manager.draw(screen)
            player.draw(screen, lane_manager.camera_y)
            draw_ui(screen, player.score)
            
            # Draw game over overlay
            draw_game_over(screen, player.score)
        
        # Update display
        pygame.display.flip()
        
        # Maintain FPS
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()