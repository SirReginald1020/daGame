import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # If the entity has a 'rect' attribute, use it; otherwise, assume entity is a Rect itself
        if hasattr(entity, 'rect'):
            return entity.rect.move(self.camera_rect.topleft)
        else:
            return entity.move(self.camera_rect.topleft)

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

    def follow(self, target):
        """Centers the camera on the target position, keeping it within level boundaries."""
        self.camera_rect.center = (target.rect.x, target.rect.y)

        # Constrain the camera within level boundaries if needed
        self.camera_rect.clamp_ip(self.camera_rect)
