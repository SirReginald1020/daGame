import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


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