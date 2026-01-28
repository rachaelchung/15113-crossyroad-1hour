import pygame
import sys
import random

# This file contains preserved game logic. I was concerned about ruining things when adding visuals, so I saved this as a backup.

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
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
GREEN = (34, 139, 34)
DARK_GRAY = (70, 70, 70)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
BROWN = (139, 69, 19)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crossy Road")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)


class Car:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 2  # Cars are 2 tiles wide
        self.height = TILE_SIZE - 4  # Slightly smaller than lane height
        self.speed = speed
        self.direction = direction  # 1 for right, -1 for left
        self.color = RED
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
        """Draw the car"""
        pygame.draw.rect(surface, self.color, self.rect)


class Log:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 3  # Logs are 3 tiles wide (larger than cars)
        self.height = TILE_SIZE - 4  # Slightly smaller than lane height
        self.speed = speed
        self.direction = direction  # 1 for right, -1 for left
        self.color = BROWN
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
        """Draw the log"""
        pygame.draw.rect(surface, self.color, self.rect)



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
                        pygame.draw.rect(surface, car.color, (car.x, car_screen_y, car.width, car.height))
                
                # Draw logs
                elif lane.type == 'RIVER':
                    for log in lane.logs:
                        log_screen_y = log.y - self.camera_y
                        pygame.draw.rect(surface, log.color, (log.x, log_screen_y, log.width, log.height))


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



class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y  # World Y position
        self.color = YELLOW
        self.size = TILE_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.score = 0  # Track highest lane reached
        self.highest_y = y  # Track highest Y position (lower/more negative values = further up)
    
    def move(self, dx, dy):
        """Move player by dx, dy tiles in world space"""
        new_x = self.x + dx * TILE_SIZE
        new_y = self.y + dy * TILE_SIZE
        
        # Keep player within horizontal bounds
        if dx != 0:  # Horizontal movement
            if 0 <= new_x <= SCREEN_WIDTH - self.size:
                self.x = new_x
                self.rect.x = self.x
        
        # Vertical movement
        if dy != 0:
            self.y = new_y
            self.rect.y = self.y
            
            if dy < 0:  # Moving up (negative Y in world space)
                # Update score when moving up
                if self.y < self.highest_y:
                    self.highest_y = self.y
                    self.score += 1
    
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
    
    def draw(self, surface, camera_y):
        """Draw the player on the screen with camera offset"""
        screen_y = self.y - camera_y
        pygame.draw.rect(surface, self.color, (self.x, screen_y, self.size, self.size))


def main():
    # Create player in world space at bottom of screen
    start_x = SCREEN_WIDTH // 2 - TILE_SIZE // 2
    start_y = SCREEN_HEIGHT - TILE_SIZE * 3  # Start near bottom
    player = Player(start_x, start_y)
    
    # Create lane manager with player's starting position
    lane_manager = LaneManager(start_y)
    
    # Game state
    game_over = False
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle movement with arrow keys (KEYDOWN for grid-based movement)
            if event.type == pygame.KEYDOWN:
                if game_over:
                    # Handle restart
                    if event.key == pygame.K_r:
                        # Reset game
                        player.reset(start_x, start_y)
                        lane_manager = LaneManager(start_y)
                        game_over = False
                else:
                    # Normal game controls
                    if event.key == pygame.K_LEFT:
                        player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0)
                    elif event.key == pygame.K_UP:
                        player.move(0, -1)  # Negative Y = move up
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1)  # Positive Y = move down
        
        if not game_over:
            # Update camera to follow player
            lane_manager.update_camera(player.y)
            
            # Update game state
            lane_manager.update()  # Update all lanes and cars
            
            # Handle river logic (player must be on log or drown)
            if lane_manager.handle_river_logic(player):
                game_over = True
            
            # Check for collisions with cars
            if lane_manager.check_collision(player.rect):
                game_over = True
            
            # Check if player fell off the bottom of the screen
            if player.get_screen_y(lane_manager.camera_y) > SCREEN_HEIGHT:
                game_over = True
        
        # Fill background
        screen.fill(GREEN)
        
        # Draw lanes and cars with camera offset
        lane_manager.draw(screen)
        
        # Draw player with camera offset
        player.draw(screen, lane_manager.camera_y)
        
        # Draw UI
        draw_ui(screen, player.score)
        
        # Draw game over screen if needed
        if game_over:
            draw_game_over(screen, player.score)
        
        # Update display
        pygame.display.flip()
        
        # Maintain FPS
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()