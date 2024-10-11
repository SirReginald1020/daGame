import pygame
import math

GRID_SIZE = 20

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

    def draw(self, screen):
        # Draw the image 10 pixels to the left of the rect
        screen.blit(self.image, (self.rect.x - 15, self.rect.y - 7 ))


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


if __name__ == '__main__':

    pygame.init()

    # Set up display
    screenInfo = pygame.display.Info()
    screen_width = screenInfo.current_w
    screen_height = screenInfo.current_h - 55
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("daGame")

    # Define gradient colors (top and bottom)
    color_top = (186, 223, 255)  # Lighter blue (top)
    color_bottom = (104, 183, 252)  # Darker blue (bottom)

    # Set up clock
    clock = pygame.time.Clock()

    # Create a player
    player = Player()

    # Create platforms
    platforms = pygame.sprite.Group()

    is_drawing = False
    start_pos = None  # Starting position for the platform creation
    current_platform = None  # The platform being created

    platforms.add(Platform(100, 500, 200, 20))
    platforms.add(Platform(400, 400, 200, 20))
    platforms.add(Platform(250, 300, 200, 30))
    # box
    platforms.add(Platform(0, screen_height - 10, screen_width, 10))
    # platforms.add(Platform(0, 0, 800, 10))
    platforms.add(Platform(0, 0, 10, screen_height-10))
    platforms.add(Platform(screen_width - 10, 0, 10, screen_height - 10))

    # Add the player to a sprite group
    all_sprites = pygame.sprite.Group()
    # all_sprites.add(player)
    all_sprites.add(platforms)

    # Main game loop
    running = True
    while running:
        clock.tick(60)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

            # Left mouse button pressed (start drawing a platform)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                start_pos = pygame.mouse.get_pos()
                is_drawing = True

            # Left mouse button released (finish drawing the platform)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and is_drawing:
                end_pos = pygame.mouse.get_pos()
                platform = create_platform(start_pos, end_pos)
                platforms.add(platform)
                is_drawing = False

            # Right mouse button pressed (delete platform)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                # Check if any platforms collide with the mouse position
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
        platforms.draw(screen)
        player.draw(screen)

        # If drawing, show the preview of the platform
        if is_drawing:
            current_pos = pygame.mouse.get_pos()
            temp_platform = create_platform(start_pos, current_pos)
            pygame.draw.rect(screen, (0, 255, 0), temp_platform.rect, 2)  # Draw platform preview

        pygame.display.flip()

    pygame.quit()

