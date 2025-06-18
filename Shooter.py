import pygame
import sys
import os

# --- Setup ---
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2D Shooter")
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)

# --- Load Assets ---
def load_male_character():
    base_path = os.path.join("assets", "characters", "male")

    head = pygame.Surface((40, 40), pygame.SRCALPHA)
    body = pygame.Surface((40, 50), pygame.SRCALPHA)
    arm = pygame.Surface((15, 30), pygame.SRCALPHA)
    leg = pygame.Surface((20, 25), pygame.SRCALPHA)

    pygame.draw.ellipse(head, (255, 220, 180), head.get_rect())
    pygame.draw.rect(body, (50, 100, 200), body.get_rect())
    pygame.draw.rect(arm, (50, 100, 200), arm.get_rect())
    pygame.draw.rect(leg, (30, 30, 30), leg.get_rect())

    return head, body, arm, leg

def draw_character(x, y, head, body, arm, leg):
    # Draw body and head
    screen.blit(body, (x, y))
    screen.blit(head, (x, y - 40))

    # Left arm with gun
    screen.blit(arm, (x - 10, y))
    
    # Draw gun in left hand as a small dark rectangle
    gun_rect = pygame.Rect(x - 25, y + 10, 15, 5)  # Positioned relative to the left arm
    pygame.draw.rect(screen, (20, 20, 20), gun_rect)

    # Right arm
    flipped_arm = pygame.transform.flip(arm, True, False)
    screen.blit(flipped_arm, (x + 30, y))

    # Legs
    screen.blit(leg, (x + 5, y + 45))
    screen.blit(pygame.transform.flip(leg, True, False), (x + 15, y + 45))



# --- Welcome Screen ---
def draw_welcome_screen():
    title_font = pygame.font.SysFont("impact", 72)
    subtitle_font = pygame.font.SysFont("arial", 28)
    alpha = 255
    fade_out = True

    # Gradient background
    background = pygame.Surface((screen_width, screen_height))
    for y in range(screen_height):
        color = (25 + y // 30, 25 + y // 40, 40 + y // 20)
        pygame.draw.line(background, color, (0, y), (screen_width, y))

    waiting = True
    while waiting:
        screen.blit(background, (0, 0))

        # UI Panel
        pygame.draw.rect(screen, (50, 50, 70), (150, 100, 500, 400), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 130), (150, 100, 500, 400), 4, border_radius=10)

        # Title Text
        title = title_font.render("2D SHOOTER", True, (255, 255, 255))
        title_shadow = title_font.render("2D SHOOTER", True, (0, 0, 0))
        screen.blit(title_shadow, (screen_width//2 - title.get_width()//2 + 2, 128))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 125))

        # Glowing Click to Play
        click_text = subtitle_font.render("CLICK TO PLAY", True, (135, 206, 250))
        click_surface = click_text.copy()
        click_surface.set_alpha(alpha)
        screen.blit(click_surface, (screen_width // 2 - click_surface.get_width() // 2, 350))

        if fade_out:
            alpha -= 5
            if alpha <= 50:
                fade_out = False
        else:
            alpha += 5
            if alpha >= 255:
                fade_out = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

        pygame.display.update()
        clock.tick(30)

# --- Bullet Class ---
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 15, y, 10, 5)
        self.speed = -10

    def move(self):
        self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect)

# --- Enemy Class ---
class Enemy:
    def __init__(self, player_x, player_y):
        self.size = (40, 60)  # Size of the enemy
        self.speed = 3
        self.color = (200, 50, 50)

        # Spawn farther to the left of the player
        spawn_offset = 800  # Distance from the player
        self.rect = pygame.Rect(player_x - spawn_offset, player_y, *self.size)

    def move(self):
        self.rect.x += self.speed  # Move right

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)
        pygame.draw.circle(surface, (0, 0, 0), self.rect.center, 10)
        pygame.draw.line(surface, (0, 0, 0), self.rect.center, (self.rect.centerx + 15, self.rect.centery))



# --- Main Game Loop ---
def run_game():
    head, body, arm, leg = load_male_character()
    player_x, player_y = screen_width - 140, 400
    player_speed = 5

    bullets = []
    enemies = []
    spawn_timer = 0
    score = 0

    running = True
    while running:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullets.append(Bullet(player_x + 15, player_y + 10))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed

        player_x = max(0, min(screen_width - 40, player_x))

        # Spawn enemies from just to the left of the player (moving right)
        spawn_timer += 1
        if spawn_timer > 60:  # Adjust spawn rate here
            enemies.append(Enemy(player_x, player_y))  # Create an enemy near the player
            spawn_timer = 0

        # Update bullets
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.right < 0:
                bullets.remove(bullet)

        # Update enemies
        for enemy in enemies[:]:
            enemy.move()

            # Check if the enemy collides with the player (end game on collision)
            if enemy.rect.colliderect(pygame.Rect(player_x, player_y, 40, 60)):  # If the enemy hits the player
                print("Game Over!")
                pygame.quit()
                sys.exit()

            # Remove enemies that go off the screen (to the right)
            if enemy.rect.left > screen_width:  # If the enemy has moved off-screen (right side)
                enemies.remove(enemy)

        # Bullet & Enemy collision
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 5
                    break

        # Draw character
        draw_character(player_x, player_y, head, body, arm, leg)

        # Draw bullets and enemies
        for bullet in bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        # Draw score
        font = pygame.font.SysFont("arial", 24)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()
  

# --- Start the Game ---
draw_welcome_screen()
run_game()
