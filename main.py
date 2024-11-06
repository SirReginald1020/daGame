import pygame
import torch
from Player import Player
from Platform import Platform
from Camera import Camera
from genetic_algorithm import GABrain  # Import the GA class
import json
import os
import math
import csv
import datetime
import time



GRID_SIZE = 40  # For placing platforms
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # For some maths, mainly for non-fullscreen display
FPS = 60  # Game speed, everything is tied to frames, higher=more calcs
pygame.init()


def save_game_state():
    """Save both platforms and genetic algorithm state."""
    # \/ Commented this out because we have different functionality for it, change back if I misunderstand it
    # save_platforms(platforms)
    ga_brain.save_population("population.json")
    print("Game state saved successfully.")


def draw_gradient(screen, color_top, color_bottom, width, height):
    """Draw a vertical gradient from color_top to color_bottom."""
    for y in range(height):
        # Calculate the interpolation factor between top and bottom colors
        factor = y / height


        # Interpolate between top and bottom colors
        r = int(color_top[0] + factor * (color_bottom[0] - color_top[0]))
        g = int(color_top[1] + factor * (color_bottom[1] - color_top[1]))
        b = int(color_top[2] + factor * (color_bottom[2] - color_top[2]))


        # Draw a horizontal line with the calculated color
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
    if not os.path.exists("Levels"):
        os.mkdir("Levels")
    file_path = os.path.join("Levels", filename + ".json")
    with open(file_path, "w") as file:
        json.dump(platform_data, file)
    print(f"Platforms saved successfully as {filename}.json")
    global level_files
    level_files = [f for f in os.listdir("Levels") if f.endswith(".json")]
    

def save_population_with_prompt(ga_brain, filename_input):
    """Save the GA population with a specified filename."""
    file_path = os.path.join(POPULATIONS_DIR, filename_input + ".json")
    ga_brain.save_population(file_path)
    print(f"Population saved successfully as {filename_input}.json")


def load_population_files():
    """Get a list of available population files."""
    return [f for f in os.listdir(POPULATIONS_DIR) if f.endswith(".json")]


def load_population_from_file(ga_brain, filename):
    """Load the GA population from a specified file."""
    file_path = os.path.join(POPULATIONS_DIR, filename)
    ga_brain.load_population(file_path)
    print(f"Population loaded successfully from {filename}")


def draw_menu(screen):
    """Draw the pause menu."""
    screenW = pygame.display.Info().current_w
    screenH = pygame.display.Info().current_h
    font = pygame.font.Font(None, 36)
    options = ["Save Platforms", "Load Level", "Save GA Population", "Load GA Population", "Exit Game"]

    # Background overlay
    menu_rect = pygame.Surface((screenW, screenH), pygame.SRCALPHA)
    menu_rect.fill((0, 0, 0, 180))  # Black transparent overlay
    screen.blit(menu_rect, (0, 0))

    # Draw menu options
    for i, option in enumerate(options):
        color = (255, 255, 255) if i == selected_option else (150, 150, 150)
        text = font.render(option, True, color)
        screen.blit(text, (screenW // 2 - text.get_width() // 2, screenH // 2 + i * 40 - 20))




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


def draw_grid(screen, grid_size, camera, world_width, world_height):
    """Draw a static grid in world space coordinates, aligned with platform positions and using camera apply."""

    # Draw vertical grid lines using camera.apply for correct alignment
    for x in range(0, world_width, grid_size):
        start_pos = pygame.Rect(x, 0, 1, world_height)  # Vertical line from top to bottom
        start_screen_pos = camera.apply(start_pos)
        pygame.draw.line(screen, (200, 200, 200), start_screen_pos.topleft, start_screen_pos.bottomleft)

    # Draw horizontal grid lines using camera.apply for correct alignment
    for y in range(0, world_height, grid_size):
        start_pos = pygame.Rect(0, y, world_width, 1)  # Horizontal line from left to right
        start_screen_pos = camera.apply(start_pos)
        pygame.draw.line(screen, (200, 200, 200), start_screen_pos.topleft, start_screen_pos.topright)


# Convert mouse position to world position considering the camera's offset
def get_world_position(mouse_pos, camera):
    # Adjust the mouse position by subtracting the camera's top-left offset
    return (
            mouse_pos[0] - camera.camera_rect.topleft[0],
            mouse_pos[1] - camera.camera_rect.topleft[1]
            )


# Function to log the best agent's fitness to a CSV file
import os
import csv


def log_best_agent_to_csv(filename, generation, best_fitness, agent_position):
    """Logs the best agent's data (generation, fitness, position) to a CSV file with headers."""
    # Check if the file already exists or is empty to add a header row
    file_exists = os.path.isfile(filename)
    write_header = not file_exists or os.stat(filename).st_size == 0

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write headers if the file is new or empty
        if write_header:
            writer.writerow(["Generation", "Best Fitness", "Position X", "Position Y"])

        # Log the data
        writer.writerow([generation, best_fitness, agent_position[0], agent_position[1]])


POPULATIONS_DIR = "Populations"
if not os.path.exists(POPULATIONS_DIR):
    os.mkdir(POPULATIONS_DIR)
else:
    PopFiles = load_population_files()


# Global variable(s)
if os.path.exists("Levels"):
    level_files = [f for f in os.listdir("Levels") if f.endswith(".json")]
else:
    os.mkdir("Levels")
    level_files = None

# Establish level to load
defaultLevel = "Mario.json"
defaultLevelPath = "Levels/" + defaultLevel
# Initialize GA brain
ga_brain = GABrain(
    population_size=10,
    mutation_rate=0.1,
    crossover_rate=0.7,
    platforms_file=defaultLevelPath,
    goal_x=7680  # Adjust based on your level's goal position
)


if __name__ == '__main__':
    start_time = time.time()
    # The many variables start here
    is_menu_open = False
    is_load_menu_open = False
    selected_option = 0  # 0 for Save Platforms, 1 for Load Level, 2 for Exit Game
    selected_level_index = 0
    filename_input = ""
    is_text_input = False
    is_population_save_prompt = False
    is_population_load_menu_open = False
    population_filename_input = ""
    selected_population_index = 0
    sortedPopulation = []
    evoCount = 0
    camera_target_player = True

    # Set up display
    screenInfo = pygame.display.Info()
    screen_width = screenInfo.current_w
    screen_height = screenInfo.current_h
    agentFont = pygame.font.Font(None, 24)

    # screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("daGame")

    # Define gradient colors (top and bottom)
    color_top = (186, 223, 255)  # Lighter blue (top)
    color_bottom = (104, 183, 252)  # Darker blue (bottom)

    # Set up clock
    clock = pygame.time.Clock()

    # Create a player
    player = Player()

    # GA Vars
    generation = 0

    # Create camera
    camera = Camera(8000, 1000)

    # Create platforms
    platforms = pygame.sprite.Group()

    load_platforms_from_file(defaultLevelPath, platforms)

    is_drawing = False
    start_pos = None  # Starting position for the platform creation
    current_platform = None  # The platform being created

    # Add the player to a sprite group
    all_sprites = pygame.sprite.Group()
    # all_sprites.add(player)
    all_sprites.add(platforms)

    # Make the default level if there are no levels.
    if not os.path.exists("Levels"):
        platform_y = camera.height + 100  # Adjust for platform height
        bottom_platform = Platform(0, platform_y, camera.width, 20)
        platforms.add(bottom_platform)
        platforms.add(Platform(0, 100, 10, camera.height))
        platforms.add(Platform(camera.width - 10, 100, 10, camera.height))

    # Full-screen state variable
    is_fullscreen = True

    # Main game loop
    debug = False
    running = True
    frames_per_generation = 2400  # Divide by FPS to get time in seconds the GA will run
    while running:
        if debug:
            print(player.rect.x, player.rect.y)
        clock.tick(FPS)
        cam_target = player if camera_target_player else best_agent
        camera.update(cam_target)
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
                    elif is_population_load_menu_open:
                        is_population_load_menu_open = False
                    else:
                        is_menu_open = not is_menu_open
                if event.key == pygame.K_c and not is_text_input:
                    camera_target_player = not camera_target_player  # Toggle between player and lead agent

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

                if is_population_save_prompt:
                    # Handle text input for population filename
                    if event.key == pygame.K_RETURN:
                        save_population_with_prompt(ga_brain, population_filename_input)
                        population_filename_input = ""  # Clear input
                        is_population_save_prompt = False
                        is_menu_open = False
                    elif event.key == pygame.K_BACKSPACE:
                        population_filename_input = population_filename_input[:-1]  # Remove last character
                    else:
                        population_filename_input += event.unicode
                elif is_population_load_menu_open:
                    # Navigate population load menu
                    if event.key == pygame.K_DOWN:
                        selected_population_index = (selected_population_index + 1) % len(population_files)
                    elif event.key == pygame.K_UP:
                        selected_population_index = (selected_population_index - 1) % len(population_files)
                    elif event.key == pygame.K_RETURN:
                        # Load the selected population
                        selected_file = population_files[selected_population_index]
                        load_population_from_file(ga_brain, selected_file)
                        is_population_load_menu_open = False
                        is_menu_open = False


                # Handle menu navigation and selection if the menu is open
                if is_menu_open and not is_load_menu_open:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % 5
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % 5
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Save Platforms
                            is_text_input = True  # Enter text input mode
                        elif selected_option == 1:  # Load Level
                            is_load_menu_open = True
                            selected_level_index = 0  # Reset to first level
                        if selected_option == 2:  # Save GA Population
                            is_population_save_prompt = True
                        elif selected_option == 3:  # Load GA Population
                            population_files = load_population_files()
                            selected_population_index = 0
                            is_population_load_menu_open = True
                        elif selected_option == 4:  # Exit Game
                            # Log the final time
                            final_elapsed_time = time.time() - start_time
                            final_hours = int(final_elapsed_time // 3600)
                            final_minutes = int((final_elapsed_time % 3600) // 60)
                            final_seconds = int(final_elapsed_time % 60)
                            log_entry = (
                                f"Run Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                f"Elapsed Time: {final_hours} hours, {final_minutes} minutes, {final_seconds} seconds\n"
                            )
                            # Write log entry to file
                            with open("run_logs.txt", "a") as log_file:
                                log_file.write(log_entry)
                            print("Run details logged successfully.")
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
                if is_fullscreen:
                    # Switch to windowed mode
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    is_fullscreen = False


                else:
                    # Switch to fullscreen mode
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                    is_fullscreen = True

            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

            # Left mouse button pressed (start drawing a platform)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                start_pos = get_world_position(pygame.mouse.get_pos(), camera)
                draw_start_pos = pygame.mouse.get_pos()
                is_drawing = True


            # Left mouse button released (finish drawing the platform)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and is_drawing:
                end_pos = get_world_position(pygame.mouse.get_pos(), camera)


                # Create the platform with adjusted world coordinates
                platform = create_platform(start_pos, end_pos)


                # Add the new platform to the platforms group
                platforms.add(platform)


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

        # === Genetic Algorithm Logic ===
        for index, agent in enumerate(ga_brain.population):
            agent.update(platforms)
            agent.draw(screen, camera, index, ga_brain.population_size)

        # Find the alpha agent (the one with the highest fitness)
        sorted_population = sorted(
            [(agent, ga_brain.calculate_fitness(agent)) for agent in ga_brain.population],
            key=lambda x: x[1],
            reverse=True
        )
        best_agent, best_fitness = sorted_population[0]

        if generation % frames_per_generation == 0:
            for agent in ga_brain.population:
                fitness = ga_brain.calculate_fitness(agent)
            best_agent, best_fitness = sorted_population[0]
            log_best_agent_to_csv("best_agent_per_evo.csv", evoCount, best_fitness,
                                  (best_agent.rect.x, best_agent.rect.y))
            evoCount += 1
            print(evoCount)
            ga_brain.evolve()
        generation += 1
        # === End of Genetic Algorithm Logic ===


        # Drawing
        for platform in platforms:
            platform.draw(screen, camera)
        player.draw(screen, camera)
        draw_grid(screen, GRID_SIZE, camera, world_width=camera.width, world_height=1100)

        # Draw the platform preview last to avoid layering issues
        if is_drawing:
            # Translate the mouse position into world coordinates
            mouse_pos_world = get_world_position(pygame.mouse.get_pos(), camera)

            # Snap to grid in world coordinates
            snapped_start_pos = snap_to_grid(start_pos, GRID_SIZE)
            snapped_mouse_pos = snap_to_grid(mouse_pos_world, GRID_SIZE)

            # Calculate the preview rectangle using snapped world coordinates
            preview_rect = pygame.Rect(
                min(snapped_start_pos[0], snapped_mouse_pos[0]),
                min(snapped_start_pos[1], snapped_mouse_pos[1]),
                abs(snapped_mouse_pos[0] - snapped_start_pos[0]),
                abs(snapped_mouse_pos[1] - snapped_start_pos[1]),
            )

            # Convert the preview rectangle to screen coordinates using camera
            preview_rect_screen = camera.apply(preview_rect)

            # Draw the preview rectangle on the screen
            pygame.draw.rect(screen, (0, 255, 0), preview_rect_screen, 2)
        if is_menu_open:
            if is_text_input:
                draw_text_input(screen, filename_input)  # Show text input prompt
            elif is_load_menu_open:
                draw_load_menu(screen, level_files, selected_level_index)
            elif is_population_save_prompt:
                draw_text_input(screen, population_filename_input)
            elif is_population_load_menu_open:
                draw_load_menu(screen, population_files, selected_population_index)
            else:
                draw_menu(screen)

        # Draw each agent's coordinates, y changes with each agent and gets reset here
        # This is in screenspace not worldspace.
        text_x = 15
        text_y = 50

        # Display agent coordinates and fitness
        for index, (agent, fitness) in enumerate(sorted_population):
            agent_coords = (agent.rect.x, agent.rect.y)
            color = (0, 0, 255) if index == 0 else (200, 0, 0)  # Blue for the alpha (highest fitness), red for others

            # Render and display each agent's coordinates and fitness
            coordinates_text = agentFont.render(f"Agent {index + 1} \n Action: {agent.action1}, {agent.action2} \n "
                                                f"(x, y): {agent_coords} | Fitness: {fitness:.2f}",
                                                True, color)
            screen.blit(coordinates_text, (text_x, text_y))
            text_y += 15  # Move down for the next agent
        elapsed_time = time.time() - start_time

        # Convert to minutes and seconds format
        hours = int(elapsed_time // 3600)
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        # Render the timer text and display it
        timer_text = agentFont.render(f"Time: {hours:02}:{minutes:02}:{seconds:02}", True, (0, 0, 0))
        screen.blit(timer_text, (1050, 0))  # Display timer in the top-right corner
        pygame.display.flip()

    pygame.quit()
