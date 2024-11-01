import pygame
from genetic_algorithm import GABrain  # Import the GA class
from Player import Player
from Platform import Platform
import json
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

# Define gradient colors (top and bottom)
color_top = (186, 223, 255)  # Lighter blue (top)
color_bottom = (104, 183, 252)  # Darker blue (bottom)


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


def save_platforms(platforms):
    """Save platforms to a file."""
    platform_data = [
        {"x": platform.rect.x, "y": platform.rect.y, "width": platform.rect.width, "height": platform.rect.height}
        for platform in platforms
    ]
    with open("platforms.json", "w") as file:
        json.dump(platform_data, file, indent=4)
    print("Platforms saved successfully.")


def save_game_state():
    """Save both platforms and genetic algorithm state."""
    save_platforms(platforms)
    ga_brain.save_population("population.json")
    print("Game state saved successfully.")


def draw_menu(screen, selected_option):
    """Draw the pause menu."""
    screenW = pygame.display.Info().current_w
    screenH = pygame.display.Info().current_h
    font = pygame.font.Font(None, 36)
    options = ["Save Game State", "Exit Game"]

    # Background overlay
    menu_rect = pygame.Surface((screenW, screenH), pygame.SRCALPHA)
    menu_rect.fill((0, 0, 0, 180))  # Black transparent overlay
    screen.blit(menu_rect, (0, 0))

    # Draw menu options
    for i, option in enumerate(options):
        color = (255, 255, 255) if i == selected_option else (150, 150, 150)
        text = font.render(option, True, color)
        screen.blit(text, (screenW // 2 - text.get_width() // 2, screenH // 2 + i * 40 - 20))


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


# Main game loop
running = True
generation = 0
is_menu_open = False
selected_option = 0  # 0 for Save Game State, 1 for Exit Game

# Create a player
player = Player()

# Create camera
camera = Camera(2000, 1000)

# Create platforms
platforms = pygame.sprite.Group()
platform_y = camera.height + 100
bottom_platform = Platform(0, platform_y, camera.width, 20)
platforms.add(bottom_platform)
platforms.add(Platform(0, 100, 10, camera.height))
platforms.add(Platform(camera.width - 10, 100, 10, camera.height))

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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            elif event.key == pygame.K_ESCAPE:
                is_menu_open = not is_menu_open
            elif event.key == pygame.K_SPACE:
                player.jump()

            # Menu navigation and selection
            if is_menu_open:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 2
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 2
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        save_game_state()  # Save platforms and GA state
                    elif selected_option == 1:
                        running = False

    # === Genetic Algorithm Logic ===
    for agent in ga_brain.population:
        fitness = ga_brain.calculate_fitness(agent)

    if generation % 10 == 0:
        ga_brain.evolve()
        generation += 1
    # === End of Genetic Algorithm Logic ===

    # Draw background and sprites
    draw_gradient(screen, color_top, color_bottom, SCREEN_WIDTH, SCREEN_HEIGHT)
    for platform in platforms:
        platform.draw(screen, camera)
    player.draw(screen, camera)

    if is_menu_open:
        draw_menu(screen, selected_option)

    pygame.display.flip()

pygame.quit()
