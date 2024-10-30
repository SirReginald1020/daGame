import pygame
import math

GRID_SIZE = 20
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 30


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
        self.rect.center = (screen_width // 2, screen_height // 2)
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

    # def draw(self, screen):
    #     # Draw the image 10 pixels to the left of the rect
    #     screen.blit(self.image, (self.rect.x - 15, self.rect.y - 7 ))

    def draw(self, screen, camera):
        offset_position = camera.apply(self).move(-15, -7)  # Adjust for your desired offset
        screen.blit(self.image, offset_position)


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


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))  # Green color for the platform
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))


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

        pygame.display.flip()

    pygame.quit()

