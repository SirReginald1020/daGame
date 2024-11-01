import pygame
from genetic_algorithm import GABrain  # Import the GA class
from Player import Player
from Platform import Platform
from Camera import Camera
import json
import os
import math

GRID_SIZE = 40
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


def save_platforms(platforms, filename):
    """Save platforms to a file with the given filename."""
    platform_data = [
        {"x": platform.rect.x, "y": platform.rect.y, "width": platform.rect.width, "height": platform.rect.height}
        for platform in platforms
    ]
<<<<<<< HEAD
    with open("platforms.json", "w") as file:
        json.dump(platform_data, file, indent=4)
    print("Platforms saved successfully.")
=======
    if not os.path.exists("Levels"):
        os.mkdir("Levels")
    file_path = os.path.join("Levels", filename + ".json")
    with open(file_path, "w") as file:
        json.dump(platform_data, file)
    print(f"Platforms saved successfully as {filename}.json")
    global level_files
    level_files = [f for f in os.listdir("Levels") if f.endswith(".json")]
>>>>>>> 0d78d4860518dcc2353d8f27bf890d541b153067


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
<<<<<<< HEAD
    options = ["Save Game State", "Exit Game"]
=======
    options = ["Save Platforms", "Load Level", "Exit Game"]
>>>>>>> 0d78d4860518dcc2353d8f27bf890d541b153067

    # Background overlay
    menu_rect = pygame.Surface((screenW, screenH), pygame.SRCALPHA)
    menu_rect.fill((0, 0, 0, 180))  # Black transparent overlay
    screen.blit(menu_rect, (0, 0))

    # Draw menu options
    for i, option in enumerate(options):
        color = (255, 255, 255) if i == selected_option else (150, 150, 150)
        text = font.render(option, True, color)
        screen.blit(text, (screenW // 2 - text.get_width() // 2, screenH // 2 + i * 40 - 20))


<<<<<<< HEAD
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
=======
def load_platforms_from_file(filename, platforms):
    """Load platforms from a JSON file and add them to the platforms group."""
    with open(filename, "r") as file:
        platform_data = json.load(file)

    # Clear existing platforms
    platforms.empty()

    # Add loaded platforms
    for data in platform_data:
        platform = Platform(data["x"], data["y"], data["width"], data["height"])
        platforms.add(platform)
    print(f"Loaded platforms from {filename}")


def draw_load_menu(screen, level_files, selected_level_index):
    """Draw the load level submenu."""
    screenW = pygame.display.Info().current_w
    screenH = pygame.display.Info().current_h
    font = pygame.font.Font(None, 36)

    # Background overlay
    load_menu_rect = pygame.Surface((screenW, screenH), pygame.SRCALPHA)
    load_menu_rect.fill((0, 0, 0, 180))  # Black transparent overlay
    screen.blit(load_menu_rect, (0, 0))

    # Draw level file options
    for i, filename in enumerate(level_files):
        color = (255, 255, 255) if i == selected_level_index else (150, 150, 150)
        text = font.render(filename, True, color)
        screen.blit(text, (screenW // 2 - text.get_width() // 2, screenH // 2 + i * 40 - 20))

def draw_text_input(screen, filename_input):
    """Draw the text input box for saving a file."""
    screenW = pygame.display.Info().current_w
    screenH = pygame.display.Info().current_h
    font = pygame.font.Font(None, 36)
    input_box = pygame.Surface((screenW, screenH), pygame.SRCALPHA)
    input_box.fill((0, 0, 0, 180))
    screen.blit(input_box, (0, 0))

    prompt_text = font.render("Enter level name:", True, (255, 255, 255))
    filename_text = font.render(filename_input, True, (255, 255, 255))

    # Center the prompt and filename on the screen
    screen.blit(prompt_text, (screenW // 2 - prompt_text.get_width() // 2, screenH // 2 - 40))
    screen.blit(filename_text, (screenW // 2 - filename_text.get_width() // 2, screenH // 2))
>>>>>>> 0d78d4860518dcc2353d8f27bf890d541b153067


def get_world_position(mouse_pos, camera):
    return (
        mouse_pos[0] - camera.camera_rect.topleft[0],
        mouse_pos[1] - camera.camera_rect.topleft[1]
    )

# Global variable(s)
if os.path.exists("Levels"):
    level_files = [f for f in os.listdir("Levels") if f.endswith(".json")]
else:
    level_files = None

# Main game loop
running = True
generation = 0
is_menu_open = False
selected_option = 0  # 0 for Save Game State, 1 for Exit Game

# Create a player
player = Player()

<<<<<<< HEAD
# Create camera
camera = Camera(2000, 1000)
=======
    is_menu_open = False
    is_load_menu_open = False
    selected_option = 0  # 0 for Save Platforms, 1 for Load Level, 2 for Exit Game
    selected_level_index = 0
    filename_input = ""
    is_text_input = False
    # Retrieve list of JSON files in Levels directory
>>>>>>> 0d78d4860518dcc2353d8f27bf890d541b153067

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

<<<<<<< HEAD
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
=======
    # Create a player
    player = Player()

    # Create camera
    camera = Camera(2000, 1000)

    # Create platforms
    platforms = pygame.sprite.Group()

    is_drawing = False
    start_pos = None  # Starting position for the platform creation
    current_platform = None  # The platform being created

    # Add the player to a sprite group
    all_sprites = pygame.sprite.Group()
    # all_sprites.add(player)
    all_sprites.add(platforms)

    # Create a platform at the bottom of the camera's initial view
    platform_y = camera.height + 100  # Adjust for platform height
    bottom_platform = Platform(0, platform_y, camera.width, 20)
    # Add the bottom platform to the platforms group
    platforms.add(bottom_platform)
    platforms.add(Platform(0, 100, 10, camera.height))
    platforms.add(Platform(camera.width - 10, 100, 10, camera.height))

    # Full-screen state variable
    is_fullscreen = True

    # Main game loop
    running = True
    while running:
        clock.tick(60)
        camera.update(player)
        player.update(platforms)
        # Event handling
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # Toggle the menu with Escape key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if is_text_input:
                        is_text_input = False  # Exit text input if in text input mode
                    elif is_load_menu_open:
                        is_load_menu_open = False
                    else:
                        is_menu_open = not is_menu_open

                # Handle text input for filename
                elif is_text_input:
                    if event.key == pygame.K_RETURN:
                        # Save platforms with the entered filename
                        save_platforms(platforms, filename_input)
                        filename_input = ""  # Clear filename input
                        is_text_input = False  # Exit text input mode
                        is_menu_open = False  # Close menu after saving
                    elif event.key == pygame.K_BACKSPACE:
                        filename_input = filename_input[:-1]  # Remove last character
                    elif event.key == pygame.K_SPACE:
                        filename_input += " "
                    else:
                        filename_input += event.unicode  # Append character to filename

                # Handle menu navigation and selection if the menu is open
                if is_menu_open and not is_load_menu_open:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % 3
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Save Platforms
                            is_text_input = True  # Enter text input mode
                        elif selected_option == 1:  # Load Level
                            is_load_menu_open = True
                            selected_level_index = 0  # Reset to first level
                        elif selected_option == 2:  # Exit Game
                            running = False
                elif is_menu_open and is_load_menu_open:
                    if event.key == pygame.K_DOWN:
                        selected_level_index = (selected_level_index + 1) % len(level_files)
                    elif event.key == pygame.K_UP:
                        selected_level_index = (selected_level_index - 1) % len(level_files)
                    elif event.key == pygame.K_RETURN:
                        # Load the selected level
                        selected_file = os.path.join("Levels", level_files[selected_level_index])
                        load_platforms_from_file(selected_file, platforms)
                        is_load_menu_open = False  # Close load menu after loading
                        is_menu_open = False  # Close main menu after loading
            # Toggle full-screen when F11 is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
>>>>>>> 0d78d4860518dcc2353d8f27bf890d541b153067
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

<<<<<<< HEAD
    pygame.display.flip()
=======
                # Reset drawing state
                is_drawing = False
                start_pos = None
                end_pos = None

            # Right mouse button pressed (delete platform)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = get_world_position(pygame.mouse.get_pos(), camera)  # Adjust for camera offset
                for platform in platforms:
                    if platform.rect.collidepoint(mouse_pos):
                        platforms.remove(platform)
                        break  # Stop after deleting one platform

        # Draw blue gradient background
        draw_gradient(screen, color_top, color_bottom, screen_width, screen_height)

        # Update all sprites
        all_sprites.update(platforms)
        player.update(platforms)

        # Drawing
        # screen.fill((255, 255, 255))  # Fill the screen with white
        # pygame.draw.rect(screen, (255, 0, 0), player.rect, 1)  # Red rectangle, thickness of 2
        # all_sprites.draw(screen)
        for platform in platforms:
            platform.draw(screen, camera)
        player.draw(screen, camera)

        # Draw the platform preview last to avoid layering issues
        if is_drawing:
            # Get the current mouse position in screen space (no need for world conversion)
            mouse_pos = pygame.mouse.get_pos()

            snapped_start_pos = snap_to_grid(draw_start_pos, GRID_SIZE)
            snapped_mouse_pos = snap_to_grid(mouse_pos, GRID_SIZE)

            # Calculate the preview rectangle using the start position in screen space
            preview_rect = pygame.Rect(
                min(snapped_start_pos[0], snapped_mouse_pos[0]),
                min(snapped_start_pos[1], snapped_mouse_pos[1]),
                abs(snapped_mouse_pos[0] - snapped_start_pos[0]),
                abs(snapped_mouse_pos[1] - snapped_start_pos[1]),
            )

            # Draw the platform preview directly on the screen
            pygame.draw.rect(screen, (0, 255, 0), preview_rect, 2)
        if is_menu_open:
            if is_text_input:
                draw_text_input(screen, filename_input)  # Show text input prompt
            elif is_load_menu_open:
                draw_load_menu(screen, level_files, selected_level_index)
            else:
                draw_menu(screen)
        pygame.display.flip()

    pygame.quit()
>>>>>>> 0d78d4860518dcc2353d8f27bf890d541b153067

pygame.quit()
