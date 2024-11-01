import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        screenInfo = pygame.display.Info()
        screen_width = screenInfo.current_w
        screen_height = screenInfo.current_h
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
        self.speed = 4.5
        self.jumping = False
        self.flipped = False  # Track whether the player is moving left or right

        # Animation timing
        self.animation_timer = 0
        self.animation_speed = 5  # Higher = Slower animation speed

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
        self.vel_y += 0.35  # Gravity
        self.rect.y += self.vel_y

        # Check for vertical collisions
        self.vertical_collisions(platforms)

    def jump(self):
        if not self.jumping:
            self.vel_y = -11
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
