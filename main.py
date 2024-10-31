import pygame
from Player import Player
from Platform import Platform
import json
import math

GRID_SIZE = 20
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 30


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


def save_platforms(platforms):
    """Save platforms to a file."""
    platform_data = [
        {"x": platform.rect.x, "y": platform.rect.y, "width": platform.rect.width, "height": platform.rect.height}
        for platform in platforms
    ]
    with open("platforms.json", "w") as file:
        json.dump(platform_data, file)
    print("Platforms saved successfully.")

def draw_menu(screen):
    """Draw the pause menu."""
    screenW = pygame.display.Info().current_w
    screenH = pygame.display.Info().current_h
    font = pygame.font.Font(None, 36)
    options = ["Save Platforms", "Exit Game"]

    # Background overlay
    menu_rect = pygame.Surface((screenW, screenH), pygame.SRCALPHA)
    menu_rect.fill((0, 0, 0, 180))  # Black transparent overlay
    screen.blit(menu_rect, (0, 0))

    # Draw menu options
    for i, option in enumerate(options):
        color = (255, 255, 255) if i == selected_option else (150, 150, 150)
        text = font.render(option, True, color)
        screen.blit(text, (screenW // 2 - text.get_width() // 2, screenH // 2 + i * 40 - 20))


# Camera class
class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Adjust the entity position relative to the camera
        return entity.rect.move(self.camera_rect.topleft)

    def update(self, target):
        # Center the camera on the player
        x = -target.rect.centerx + SCREEN_WIDTH // 2
        y = -target.rect.centery + SCREEN_HEIGHT // 2

        # Clamp the camera within the level bounds
        x = min(0, x)  # Left boundary
        y = min(0, y)  # Top boundary
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right boundary
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom boundary

        self.camera_rect = pygame.Rect(x, y, self.width, self.height)


# Convert mouse position to world position considering the camera's offset
def get_world_position(mouse_pos, camera):
    # Adjust the mouse position by subtracting the camera's top-left offset
    return (
            mouse_pos[0] - camera.camera_rect.topleft[0],
            mouse_pos[1] - camera.camera_rect.topleft[1]
            )


if __name__ == '__main__':

    pygame.init()

    is_menu_open = False
    selected_option = 0  # 0 for Save Platforms, 1 for Exit Game

    # Set up display
    screenInfo = pygame.display.Info()
    screen_width = screenInfo.current_w
    screen_height = screenInfo.current_h
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
                    is_menu_open = not is_menu_open

                # Handle menu navigation and selection if the menu is open
                if is_menu_open:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % 2
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % 2
                    elif event.key == pygame.K_RETURN:  # Select option
                        if selected_option == 0:  # Save Platforms
                            save_platforms(platforms)
                            is_menu_open = False  # Close menu after saving
                        elif selected_option == 1:  # Exit Game
                            running = False  # Exit game loop
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
            draw_menu(screen)  # Display the menu
        pygame.display.flip()

    pygame.quit()

