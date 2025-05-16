import pygame
import random
import math
import os
import json
import uuid
from datetime import datetime

pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
FONT_SMALL = pygame.font.SysFont("Arial", 24, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Arial", 32, bold=True)
FONT_LARGE = pygame.font.SysFont("Arial", 48, bold=True)

# Load sounds
try:
    pop_sound = pygame.mixer.Sound('pop.wav.mp3')
    background_music = pygame.mixer.Sound('background.wav.mp3')
    menu_music = pygame.mixer.Sound('menu.wav.mp3')
    has_sound = True
except:
    print("Sound files not found. Continuing without sound.")
    has_sound = False

# Load or create background
try:
    sky_image = pygame.image.load('sky_background.jpg')
    sky_image = pygame.transform.scale(sky_image, (WIDTH, HEIGHT))
except:
    sky_image = pygame.Surface((WIDTH, HEIGHT))
    sky_image.fill((135, 206, 235))  # Sky blue fallback

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balloon Pop")

# Game colors and settings
BALLOON_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (75, 0, 130)]
DIFFICULTIES = {
    "easy": {"min_speed": 1, "max_speed": 3, "speed_increase": 0.5},
    "medium": {"min_speed": 2, "max_speed": 5, "speed_increase": 1},
    "hard": {"min_speed": 3, "max_speed": 7, "speed_increase": 1.5}
}

# Game state
class GameState:
    def __init__(self):
        self.reset()
        self.scores = []
        self.player_name = ""
        self.name_input_active = False
        self.load_scores()
        self.music_playing = None
        
    def reset(self):
        self.balloons = []
        self.balloon_count = 20
        self.balloons_popped = 0
        self.level = 1
        self.target_balloons = 10
        self.current_difficulty = "medium"  # Reset to default
        self.score = 0
        self.paused = False
        self.game_over = False
        self.player_id = str(uuid.uuid4())
        self.skipped = False
        self.name_input_active = False  # Add this line
            
    def load_scores(self):
        if os.path.exists('scores.json'):
            try:
                with open('scores.json', 'r') as file:
                    self.scores = json.load(file)
                    # Ensure all scores have required fields
                    for score in self.scores:
                        if 'name' not in score:
                            score['name'] = 'Anonymous'
                        if 'difficulty' not in score:
                            score['difficulty'] = 'medium'
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                self.scores = []
        else:
            self.scores = []
    
    def save_scores(self):
        with open('scores.json', 'w') as file:
            json.dump(self.scores, file)
    
    def add_score(self):
        if not self.skipped and self.player_name.strip():  # Only save if not skipped and name entered
            self.scores.append({
                "player_id": self.player_id,
                "name": self.player_name,
                "score": self.score,
                "level": self.level,
                "difficulty": self.current_difficulty,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.scores.sort(key=lambda x: x["score"], reverse=True)
            self.save_scores()
    
    def play_music(self, track):
        if not has_sound:
            return
            
        if self.music_playing == track:
            return
            
        # Stop any currently playing music
        pygame.mixer.stop()
        
        if track == "menu":
            menu_music.play(-1)  # -1 means loop indefinitely
            menu_music.set_volume(0.5)
            self.music_playing = "menu"
        elif track == "game":
            background_music.play(-1)
            background_music.set_volume(0.3)
            self.music_playing = "game"
        elif track is None:
            pygame.mixer.stop()
            self.music_playing = None

# Utility functions
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

def draw_button(text, rect, color, hover_color, text_color=WHITE):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    
    pygame.draw.rect(screen, hover_color if is_hovered else color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    draw_text(text, FONT_MEDIUM, text_color, rect.centerx, rect.centery, center=True)
    
    return is_hovered and pygame.mouse.get_pressed()[0]

def draw_header(state):
    # Header background
    header_rect = pygame.Rect(0, 0, WIDTH, 60)
    pygame.draw.rect(screen, (70, 70, 70), header_rect)
    pygame.draw.line(screen, BLACK, (0, 60), (WIDTH, 60), 2)
    
    # Game title on left
    draw_text("Balloon Pop", FONT_MEDIUM, WHITE, 20, 30)
    
    # Pause and skip buttons on right
    pause_btn = pygame.Rect(WIDTH - 180, 10, 80, 40)
    skip_btn = pygame.Rect(WIDTH - 90, 10, 80, 40)
    
    if draw_button("Pause" if not state.paused else "Resume", pause_btn, 
                  DARK_GRAY, GRAY):
        state.paused = not state.paused
        if has_sound and not state.paused and state.music_playing == "game":
            background_music.set_volume(0.3)
        elif has_sound and state.paused and state.music_playing == "game":
            background_music.set_volume(0.1)
    
    if draw_button("Skip", skip_btn, (255, 165, 0), (255, 200, 0)):
        state.game_over = True
        state.skipped = True
        return "game_over"
    
    return None

# Balloon functions
def create_balloon(state, x=None, y=None):
    size = random.randint(40, 70)
    x = random.randint(0, WIDTH - size) if x is None else x
    y = HEIGHT + 50 if y is None else y
    color = random.choice(BALLOON_COLORS)
    settings = DIFFICULTIES[state.current_difficulty]
    min_speed = settings["min_speed"] + state.level * settings["speed_increase"]
    max_speed = settings["max_speed"] + state.level * settings["speed_increase"]
    return {
        "rect": pygame.Rect(x, y, size, int(size * 1.2)),
        "color": color,
        "speed": random.uniform(min_speed, max_speed),
        "popped": False
    }

def draw_balloon(balloon):
    rect = balloon["rect"]
    color = balloon["color"]
    pygame.draw.ellipse(screen, color, rect)
    
    highlight_color = (min(color[0] + 100, 255), min(color[1] + 100, 255), min(color[2] + 100, 255))
    highlight_rect = pygame.Rect(rect.x + rect.width // 4, rect.y + rect.height // 6, rect.width // 3, rect.height // 3)
    pygame.draw.ellipse(screen, highlight_color, highlight_rect)

def draw_balloon_string(balloon):
    start_x, start_y = balloon["rect"].centerx, balloon["rect"].bottom
    points = []
    for i in range(20):
        x_offset = 10 * math.sin(i * 0.3 * math.pi)
        points.append((start_x + x_offset, start_y + i * 5))
    pygame.draw.lines(screen, BLACK, False, points, 2)

def pop_effect(x, y, state):
    if has_sound:
        pop_sound.play()
    
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

# Screen functions
def draw_name_input_screen(state):
    screen.blit(sky_image, (0, 0))
    
    # Title
    draw_text("Enter Your Name", FONT_LARGE, BLACK, WIDTH // 2, 150, center=True)
    
    # Input box
    input_rect = pygame.Rect(WIDTH // 2 - 200, 250, 400, 60)
    pygame.draw.rect(screen, WHITE, input_rect)
    pygame.draw.rect(screen, BLACK, input_rect, 2)
    
    # Display current name
    name_text = state.player_name if state.player_name else "Type your name here"
    name_color = BLACK if state.player_name else GRAY
    draw_text(name_text, FONT_MEDIUM, name_color, WIDTH // 2, 280, center=True)
    
    # Submit button
    submit_btn = pygame.Rect(WIDTH // 2 - 100, 350, 200, 50)
    if draw_button("Submit", submit_btn, GREEN, (100, 255, 100), BLACK):
        if state.player_name.strip():  # Only proceed if name isn't empty
            return "manual"
    
    return "name_input"

def draw_manual_screen(state):
    screen.blit(sky_image, (0, 0))
    
    # Title
    draw_text("How to Play", FONT_LARGE, RED, WIDTH // 2, 50, outline_color=BLACK, center=True)
    
    # Instructions
    instructions = [
        "Welcome to Balloon Pop!",
        "",
        "Objective:",
        "- Pop as many balloons as you can before time runs out",
        "- Each popped balloon gives you 1 point",
        "",
        "Gameplay:",
        "- Click on balloons to pop them",
        "- Higher levels mean faster balloons",
        "- Complete targets to advance levels",
        "",
        "Controls:",
        "- Pause: Temporarily stop the game",
        "- Skip: End current game early"
    ]
    
    for i, line in enumerate(instructions):
        y_pos = 120 + i * 30
        if i == 0:  # First line (title)
            draw_text(line, FONT_MEDIUM, BLUE, WIDTH // 2, y_pos, center=True)
        elif line and line[0] == "-":  # Bullet points
            draw_text(line, FONT_SMALL, BLACK, WIDTH // 2 - 250, y_pos)
        elif line:  # Section headers
            draw_text(line, FONT_SMALL, (0, 100, 0), WIDTH // 2 - 250, y_pos)
    
    # Continue button
    continue_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
    if draw_button("Continue", continue_btn, GREEN, (100, 255, 100), BLACK):
        return "start"
    
    return "manual"

def draw_start_screen(state):
    state.play_music("menu")
    screen.blit(sky_image, (0, 0))
    draw_text("Balloon Pop!", FONT_LARGE, RED, WIDTH // 2, 150, outline_color=BLACK, center=True)
    
    # Difficulty buttons
    easy_btn = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)
    medium_btn = pygame.Rect(WIDTH // 2 - 150, 320, 300, 50)
    hard_btn = pygame.Rect(WIDTH // 2 - 150, 390, 300, 50)
    
    if draw_button("Easy", easy_btn, GREEN, (100, 255, 100), BLACK):
        state.current_difficulty = "easy"
    if draw_button("Medium", medium_btn, BLUE, (100, 100, 255), WHITE):
        state.current_difficulty = "medium"
    if draw_button("Hard", hard_btn, RED, (255, 100, 100), WHITE):
        state.current_difficulty = "hard"
    
    # Highlight selected difficulty
    if state.current_difficulty == "easy":
        pygame.draw.rect(screen, BLACK, easy_btn.inflate(10, 10), 3, border_radius=15)
    elif state.current_difficulty == "medium":
        pygame.draw.rect(screen, BLACK, medium_btn.inflate(10, 10), 3, border_radius=15)
    else:
        pygame.draw.rect(screen, BLACK, hard_btn.inflate(10, 10), 3, border_radius=15)
    
    # Start and score buttons
    start_btn = pygame.Rect(WIDTH // 2 - 150, 470, 300, 60)
    scores_btn = pygame.Rect(WIDTH // 2 - 150, 550, 300, 60)
    
    if draw_button("Start Game", start_btn, (100, 100, 255), (150, 150, 255)):
        state.play_music("game")
        return "game"
    if draw_button("High Scores", scores_btn, (255, 165, 0), (255, 200, 0)):
        return "scores"
    
    return "start"

def draw_scores_screen(state):
    screen.blit(sky_image, (0, 0))
    draw_text("High Scores", FONT_LARGE, RED, WIDTH // 2, 50, outline_color=BLACK, center=True)
    
    # Table header
    header_y = 120
    draw_text("Name", FONT_MEDIUM, BLACK, WIDTH // 2 - 200, header_y)
    draw_text("Score", FONT_MEDIUM, BLACK, WIDTH // 2 - 50, header_y)
    draw_text("Level", FONT_MEDIUM, BLACK, WIDTH // 2 + 100, header_y)
    draw_text("Difficulty", FONT_MEDIUM, BLACK, WIDTH // 2 + 250, header_y)
    
    # Scores list
    if not state.scores:
        draw_text("No scores yet!", FONT_MEDIUM, BLACK, WIDTH // 2, HEIGHT // 2, center=True)
    else:
        for i, score in enumerate(state.scores[:10]):  # Show top 10 scores
            y_pos = header_y + 50 + i * 40
            draw_text(f"{i+1}.", FONT_SMALL, BLACK, WIDTH // 2 - 250, y_pos)
            draw_text(score.get('name', 'Anonymous')[:12], FONT_SMALL, BLACK, WIDTH // 2 - 200, y_pos)
            draw_text(str(score['score']), FONT_SMALL, BLACK, WIDTH // 2 - 50, y_pos)
            draw_text(str(score['level']), FONT_SMALL, BLACK, WIDTH // 2 + 100, y_pos)
            draw_text(score.get('difficulty', 'medium').capitalize(), FONT_SMALL, BLACK, WIDTH // 2 + 250, y_pos)
    
    # Back button
    back_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
    if draw_button("Back", back_btn, RED, (255, 100, 100)):
        return "start"
    
    return "scores"

def draw_game_screen(state, elapsed_time, total_time):
    screen.blit(sky_image, (0, 0))
    
    # Draw header with title and buttons
    header_result = draw_header(state)
    if header_result:
        return header_result
    
    # Game info below header
    time_left = max(0, (total_time - elapsed_time) // 1000)
    draw_text(f"Score: {state.score}", FONT_SMALL, WHITE, 20, 80)
    draw_text(f"Time: {time_left}s", FONT_SMALL, WHITE, WIDTH - 150, 80)
    draw_text(f"Level: {state.level}", FONT_SMALL, WHITE, 20, HEIGHT - 40)
    draw_text(f"Target: {state.target_balloons - state.balloons_popped}", FONT_SMALL, WHITE, WIDTH - 150, HEIGHT - 40)
    
    if state.paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        draw_text("PAUSED", FONT_LARGE, WHITE, WIDTH // 2, HEIGHT // 2, center=True)
        return "game"
    
    # Update and draw balloons (under the header)
    for balloon in state.balloons[:]:
        if not state.paused and not balloon["popped"]:
            balloon["rect"].y -= balloon["speed"]
        
        # Only draw if below header (y > 60)
        if balloon["rect"].y > 60:
            draw_balloon_string(balloon)
            draw_balloon(balloon)
        
        if balloon["rect"].bottom < 60:  # Changed from 0 to 60 (header height)
            state.balloons.remove(balloon)
    
    # Create new balloons if needed (starting below visible area)
    if len(state.balloons) < state.balloon_count + state.level * 2 and not state.paused:
        state.balloons.append(create_balloon(state))
    
    # Check level progression
    if state.balloons_popped >= state.target_balloons and not state.paused:
        state.level += 1
        state.target_balloons += 5
        state.balloons_popped = 0
    
    # Check game over
    if elapsed_time >= total_time and not state.paused:
        state.game_over = True
        return "game_over"
    
    return "game"

def draw_game_over_screen(state):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    box_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 200, 500, 400)
    pygame.draw.rect(screen, WHITE, box_rect, border_radius=20)
    pygame.draw.rect(screen, BLACK, box_rect, 3, border_radius=20)
    
    draw_text("GAME OVER", FONT_LARGE, RED, WIDTH // 2, HEIGHT // 2 - 150, center=True)
    
    y_offset = HEIGHT // 2 - 80
    draw_text(f"Player: {state.player_name}", FONT_MEDIUM, BLACK, WIDTH // 2, y_offset, center=True)
    draw_text(f"Final Score: {state.score}", FONT_MEDIUM, BLACK, WIDTH // 2, y_offset + 50, center=True)
    draw_text(f"Final Level: {state.level}", FONT_MEDIUM, BLACK, WIDTH // 2, y_offset + 100, center=True)
    
    # Buttons
    play_again_btn = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 50, 200, 50)
    main_menu_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 50, 200, 50)
    
    if draw_button("Play Again", play_again_btn, GREEN, (100, 255, 100), BLACK):
        state.reset()
        state.play_music("game")
        game_start_time = pygame.time.get_ticks()  # Reset timer
        return "game"
    if draw_button("Main Menu", main_menu_btn, RED, (255, 100, 100), WHITE):
        state.reset()
        state.play_music("menu")
        return "start"
    
    return "game_over"

# Main game loop
def main():
    clock = pygame.time.Clock()
    state = GameState()
    current_screen = "name_input"  # Start with name input
    game_start_time = 0
    total_game_time = 30000  # 30 seconds
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_screen == "game":
                    if not state.paused:
                        for balloon in state.balloons[:]:
                            if balloon["rect"].collidepoint(event.pos) and balloon["rect"].y > 60:  # Only pop balloons below header
                                balloon["popped"] = True
                                state.balloons.remove(balloon)
                                state.score += 1
                                state.balloons_popped += 1
                                pop_effect(event.pos[0], event.pos[1], state)
                elif current_screen == "name_input":
                    # Activate text input
                    state.name_input_active = True
            elif event.type == pygame.KEYDOWN and state.name_input_active:
                if event.key == pygame.K_RETURN:
                    state.name_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    state.player_name = state.player_name[:-1]
                else:
                    # Limit name length and only allow certain characters
                    if len(state.player_name) < 15 and event.unicode.isalnum():
                        state.player_name += event.unicode
        
        # Screen transitions
        if current_screen == "name_input":
            current_screen = draw_name_input_screen(state)
        elif current_screen == "manual":
            current_screen = draw_manual_screen(state)
        elif current_screen == "start":
            current_screen = draw_start_screen(state)
        elif current_screen == "scores":
            current_screen = draw_scores_screen(state)
        elif current_screen == "game":
            if game_start_time == 0:  # First frame of game
                game_start_time = pygame.time.get_ticks()
            elapsed_time = pygame.time.get_ticks() - game_start_time
            current_screen = draw_game_screen(state, elapsed_time, total_game_time)
        elif current_screen == "game_over":
            if state.game_over:
                state.add_score()
                state.game_over = False
            result = draw_game_over_screen(state)
            if result == "game":
                game_start_time = pygame.time.get_ticks()
                current_screen = "game"
            elif result == "start":
                current_screen = "start"
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()