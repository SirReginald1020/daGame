import pygame
from genetic_algorithm import GABrain  # Import the GA class
from genetic_algorithm import GABrain  # Import the GA class
import math

GRID_SIZE = 20
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 30

# Initialize Pygame and display
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("daGame")

# Initialize GA brain
ga_brain = GABrain(
    population_size=10, 
    mutation_rate=0.1, 
    crossover_rate=0.7, 
    sequence_length=100, 
    goal_x=1000  # Adjust based on your level's goal position
)
# Initialize Pygame and display
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("daGame")

# Initialize GA brain
ga_brain = GABrain(
    population_size=10, 
    mutation_rate=0.1, 
    crossover_rate=0.7, 
    sequence_length=100, 
    goal_x=1000  # Adjust based on your level's goal position
)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load the sprite sheet
        self.frames = []
        for i in range(1, 11):
            frame = pygame.image.load(f"sprites/Running/Sprite-0001-lilGuyRunning{i}.png")
            frame = pygame.transform.scale(frame, (frame.get_width() * 4, frame.get_height() * 4))
            self.frames.append(frame)

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = pygame.Rect(0, 0, 34, 57)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.vel_y = 0
        self.speed = 5
        self.jumping = False
        self.flipped = False  # Track whether the player is moving left or right

        # Animation timing
        self.animation_timer = 0
        self.animation_speed = 3.5  # Adjust this for faster/slower animation speed

    def animate(self):
        # Update frame based on time
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_timer = 0

        # Get current frame and flip it if moving left
        frame = self.frames[self.current_frame]
        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)

        # Update image with the current frame
        self.image = frame

    def update(self, platforms):
        moving = False
        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.flipped = True  # Moving left
            self.animate()
            moving = True
        elif keys[pygame.K_d]:
            self.rect.x += self.speed
            self.flipped = False  # Moving right
            self.animate()
            moving = True

        if not moving:
            self.current_frame = 0  # Set to the first frame (idle)
            frame = self.frames[self.current_frame]
            if self.flipped:
                frame = pygame.transform.flip(frame, True, False)  # Flip if last facing left
            self.image = frame

        # Check for horizontal collisions
        self.horizontal_collisions(platforms)

        # Gravity and vertical movement
        self.vel_y += 1  # Gravity
        self.rect.y += self.vel_y

        # Check for vertical collisions
        self.vertical_collisions(platforms)

    def jump(self):
        if not self.jumping:
            self.vel_y = -15
            self.jumping = True

    def horizontal_collisions(self, platforms):
        # Check for collisions when moving left or right
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in hits:
            # Moving right; hit the left side of a platform
            if self.rect.right > hit.rect.left > self.rect.left:
                self.rect.right = hit.rect.left
            # Moving left; hit the right side of a platform
            elif self.rect.left < hit.rect.right < self.rect.right:
                self.rect.left = hit.rect.right

    def vertical_collisions(self, platforms):
        # Check for collisions when falling or jumping
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            if self.vel_y > 0:  # Falling down
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.jumping = False  # Can jump again
            elif self.vel_y < 0:  # Jumping up
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0

    def draw(self, screen, camera):
        offset_position = camera.apply(self).move(-15, -7)
        screen.blit(self.image, offset_position)


def draw_gradient(screen, color_top, color_bottom, width, height):
    """Draw a vertical gradient from color_top to color_bottom."""
    for y in range(height):
        factor = y / height
        r = int(color_top[0] + factor * (color_bottom[0] - color_top[0]))
        g = int(color_top[1] + factor * (color_bottom[1] - color_top[1]))
        b = int(color_top[2] + factor * (color_bottom[2] - color_top[2]))
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))


def create_platform(start_pos, end_pos):
    """Create a platform between start_pos and end_pos."""
    start_pos = snap_to_grid(start_pos, GRID_SIZE)
    end_pos = snap_to_grid(end_pos, GRID_SIZE)
    x = min(start_pos[0], end_pos[0])
    y = min(start_pos[1], end_pos[1])
    width = abs(start_pos[0] - end_pos[0])
    height = abs(start_pos[1] - end_pos[1])
    return Platform(x, y, width, height)


def snap_to_grid(pos, grid_size):
    """Round the position to the nearest grid point."""
    x = round(pos[0] / grid_size) * grid_size
    y = round(pos[1] / grid_size) * grid_size
    return (x, y)


class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera_rect.topleft)

    def update(self, target):
        x = -target.rect.centerx + SCREEN_WIDTH // 2
        y = -target.rect.centery + SCREEN_HEIGHT // 2
        x = min(0, x)  # Left boundary
        y = min(0, y)  # Top boundary
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right boundary
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom boundary
        self.camera_rect = pygame.Rect(x, y, self.width, self.height)


def get_world_position(mouse_pos, camera):
    return (
        mouse_pos[0] - camera.camera_rect.topleft[0],
        mouse_pos[1] - camera.camera_rect.topleft[1]
    )
        mouse_pos[0] - camera.camera_rect.topleft[0],
        mouse_pos[1] - camera.camera_rect.topleft[1]
    )


# Main game loop
running = True
generation = 0
# Main game loop
running = True
generation = 0

# Define gradient colors (top and bottom)
color_top = (186, 223, 255)  # Lighter blue (top)
color_bottom = (104, 183, 252)  # Darker blue (bottom)
# Define gradient colors (top and bottom)
color_top = (186, 223, 255)  # Lighter blue (top)
color_bottom = (104, 183, 252)  # Darker blue (bottom)

# Create a player
player = Player()
# Create a player
player = Player()

# Create camera
camera = Camera(2000, 1000)
# Create camera
camera = Camera(2000, 1000)

# Create platforms
platforms = pygame.sprite.Group()
platform_y = camera.height + 100
bottom_platform = Platform(0, platform_y, camera.width, 20)
platforms.add(bottom_platform)
platforms.add(Platform(0, 100, 10, camera.height))
platforms.add(Platform(camera.width - 10, 100, 10, camera.height))
# Create platforms
platforms = pygame.sprite.Group()
platform_y = camera.height + 100
bottom_platform = Platform(0, platform_y, camera.width, 20)
platforms.add(bottom_platform)
platforms.add(Platform(0, 100, 10, camera.height))
platforms.add(Platform(camera.width - 10, 100, 10, camera.height))

# Full-screen state variable
is_fullscreen = True
# Full-screen state variable
is_fullscreen = True

while running:
    clock = pygame.time.Clock()
    clock.tick(60)
    camera.update(player)
    player.update(platforms)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            if is_fullscreen:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                is_fullscreen = False
            else:
                screen = pygame.display.set_mode((screen.get_width(), screen.get_height()), pygame.FULLSCREEN)
                is_fullscreen = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()
while running:
    clock = pygame.time.Clock()
    clock.tick(60)
    camera.update(player)
    player.update(platforms)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            if is_fullscreen:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                is_fullscreen = False
            else:
                screen = pygame.display.set_mode((screen.get_width(), screen.get_height()), pygame.FULLSCREEN)
                is_fullscreen = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()

    # === Genetic Algorithm Logic ===
    for agent in ga_brain.population:
        fitness = ga_brain.calculate_fitness(agent)

    if generation % 10 == 0:
        ga_brain.evolve()
        generation += 1
    # === End of Genetic Algorithm Logic ===
    # === Genetic Algorithm Logic ===
    for agent in ga_brain.population:
        fitness = ga_brain.calculate_fitness(agent)

    if generation % 10 == 0:
        ga_brain.evolve()
        generation += 1
    # === End of Genetic Algorithm Logic ===

    # Draw blue gradient background
    draw_gradient(screen, color_top, color_bottom, SCREEN_WIDTH, SCREEN_HEIGHT)
    all_sprites = pygame.sprite.Group(player)
    all_sprites.update(platforms)
    # Draw blue gradient background
    draw_gradient(screen, color_top, color_bottom, SCREEN_WIDTH, SCREEN_HEIGHT)
    all_sprites = pygame.sprite.Group(player)
    all_sprites.update(platforms)

    # Draw platforms and player
    for platform in platforms:
        platform.draw(screen, camera)
    player.draw(screen, camera)
    # Draw platforms and player
    for platform in platforms:
        platform.draw(screen, camera)
    player.draw(screen, camera)

    pygame.display.flip()
    pygame.display.flip()

pygame.quit()
pygame.quit()
