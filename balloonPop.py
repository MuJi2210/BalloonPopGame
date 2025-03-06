import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FONT_SMALL = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
FONT_LARGE = pygame.font.SysFont("Comic Sans MS", 60, bold=True)

sky_image = pygame.image.load('sky_background.jpg')
sky_image = pygame.transform.scale(sky_image, (WIDTH, HEIGHT))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balloon Pop")

BALLOON_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (75, 0, 130)]

balloons = []
balloon_count = 1000

for i in range(balloon_count):
    size = random.randint(40, 70)
    x = random.randint(0, WIDTH - size)
    y = HEIGHT + 50 * i
    color = random.choice(BALLOON_COLORS)
    balloons.append({"rect": pygame.Rect(x, y, size, int(size * 1.2)), "color": color, "speed": random.randint(3, 7)})

def draw_text(text, font, color, x, y, outline_color=None, shadow=False, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    
    if outline_color:
        outline_offset = 2
        for dx, dy in [(-outline_offset, 0), (outline_offset, 0), (0, -outline_offset), (0, outline_offset)]:
            screen.blit(font.render(text, True, outline_color), text_rect.move(dx, dy))
    if shadow:
        screen.blit(font.render(text, True, (50, 50, 50)), text_rect.move(3, 3))
    screen.blit(text_surface, text_rect)

def draw_balloon_string(balloon):
    start_x, start_y = balloon["rect"].centerx, balloon["rect"].bottom
    points = []
    for i in range(20):
        x_offset = 10 * math.sin(i * 0.3 * math.pi)
        points.append((start_x + x_offset, start_y + i * 5))
    pygame.draw.lines(screen, BLACK, False, points, 2)

def draw_balloon(balloon):
    rect = balloon["rect"]
    color = balloon["color"]
    pygame.draw.ellipse(screen, color, rect)
    
    highlight_color = (min(color[0] + 100, 255), min(color[1] + 100, 255), min(color[2] + 100, 255))
    highlight_rect = pygame.Rect(rect.x + rect.width // 4, rect.y + rect.height // 6, rect.width // 3, rect.height // 3)
    pygame.draw.ellipse(screen, highlight_color, highlight_rect)

def pop_effect(x, y):
    particles = []
    for _ in range(15):
        particle_x = x + random.randint(-15, 15)
        particle_y = y + random.randint(-15, 15)
        velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
        lifetime = random.randint(20, 40)
        particles.append({"pos": [particle_x, particle_y], "velocity": velocity, "color": random.choice(BALLOON_COLORS), "lifetime": lifetime})
    
    for particle in particles:
        pygame.draw.circle(screen, particle["color"], (int(particle["pos"][0]), int(particle["pos"][1])), random.randint(2, 5))
        particle["pos"][0] += particle["velocity"][0]
        particle["pos"][1] += particle["velocity"][1]
        particle["lifetime"] -= 1

speed = 4
running = True
start_ticks = pygame.time.get_ticks()
time_limit = 30000

score = 0
game_over = False

while running:
    screen.blit(sky_image, (0, 0))
    elapsed_time = pygame.time.get_ticks() - start_ticks
    time_left = max(0, (time_limit - elapsed_time) // 1000)

    draw_text(f"Time: {time_left}s", FONT_SMALL, WHITE, WIDTH - 200, 30, outline_color=BLACK)
    draw_text(f"Score: {score}", FONT_SMALL, WHITE, 30, 30, outline_color=BLACK)

    if game_over:
        draw_text("Game Over!", FONT_LARGE, RED, WIDTH // 2, HEIGHT // 2 - 80, outline_color=BLACK, center=True)
        draw_text(f"Final Score: {score}", FONT_LARGE, WHITE, WIDTH // 2, HEIGHT // 2, outline_color=BLACK, center=True)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                for balloon in balloons[:]:
                    if balloon["rect"].collidepoint(event.pos):
                        balloons.remove(balloon)
                        score += 1
                        pop_effect(event.pos[0], event.pos[1])
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        for balloon in balloons:
            balloon["rect"].y -= balloon["speed"]
            draw_balloon_string(balloon)
            draw_balloon(balloon)

    if elapsed_time >= time_limit and not game_over:
        game_over = True

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
