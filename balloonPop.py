import pygame
import random

pygame.init()

WIDTH, HEIGHT = 500, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FONT = pygame.font.SysFont("Arial", 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balloon Pop")

balloons = []
balloon_count = 1000

for i in range(balloon_count):
    x = random.randint(0, WIDTH - 30)
    y = HEIGHT + 40 * i
    balloons.append(pygame.Rect(x, y, 30, 40))

speed = 3
running = True
start_ticks = pygame.time.get_ticks()
time_limit = 30000

score = 0
game_over = False

while running:
    screen.fill(WHITE)

    elapsed_time = pygame.time.get_ticks() - start_ticks
    time_left = max(0, (time_limit - elapsed_time) // 1000)

    timer_text = FONT.render(f"Time: {time_left}s", True, (0, 0, 0))
    score_text = FONT.render(f"Score: {score}", True, (0, 0, 0))
    
    screen.blit(timer_text, (WIDTH - 150, 20))
    screen.blit(score_text, (20, 20))

    if game_over:
        game_over_text = FONT.render("Game Over!", True, (0, 0, 0))
        final_score_text = FONT.render(f"Final Score: {score}", True, (0, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        screen.blit(final_score_text, (WIDTH // 2 - 130, HEIGHT // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                for balloon in balloons[:]:
                    if balloon.collidepoint(event.pos):
                        balloons.remove(balloon)
                        score += 1
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        for balloon in balloons:
            balloon.y -= speed
            pygame.draw.ellipse(screen, RED, balloon)

    if elapsed_time >= time_limit and not game_over:
        game_over = True

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
