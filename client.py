import pygame
import random
import sys
import requests

pygame.init()

def reset_game():
    global player_rect, obstacles, score, game_over
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 10, PLAYER_WIDTH, PLAYER_HEIGHT)  # Размещаем игрока в центре
    obstacles = []
    score = 0
    game_over = False

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Этап 3: Игра с таблицей лидеров")
clock = pygame.time.Clock()


SERVER_URL = "https://flask-leaderboard-production-8cc0.up.railway.app"

PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
player_rect = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 10, PLAYER_WIDTH, PLAYER_HEIGHT)
player_speed = 7

OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 50, 50
obstacle_speed = 10
obstacles = []

SPAWN_OBSTACLE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_OBSTACLE, 200)

font = pygame.font.SysFont(None, 36)
score = 0

game_over = False
running = True

player_name = ""
typing_name = True
while typing_name:
    screen.fill((0, 0, 0))
    prompt_text = font.render("Введите имя и нажмите Enter:", True, (255, 255, 255))
    name_text = font.render(player_name, True, (0, 255, 0))
    
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if player_name.strip() != "":
                    typing_name = False
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            else:
                if len(player_name) < 15:
                    player_name += event.unicode

leaderboard = []

reset_game()

while running:
    if not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SPAWN_OBSTACLE:
                x_pos = random.randint(0, WIDTH - OBSTACLE_WIDTH)
                obstacles.append(pygame.Rect(x_pos, 0, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += player_speed

        for obstacle in obstacles[:]:
            obstacle.y += obstacle_speed
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
                score += 1
            if player_rect.colliderect(obstacle):
                game_over = True

                try:
                    requests.post(f"{SERVER_URL}/submit", json={
                        "name": player_name,
                        "score": score
                    }, timeout=2)
                except Exception as e:
                    print("Не удалось отправить результат:", e)

                try:
                    response = requests.get(f"{SERVER_URL}/leaders", timeout=2)
                    leaderboard = response.json()
                except Exception as e:
                    print("Не удалось получить таблицу лидеров:", e)
                    leaderboard = []

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (0, 255, 0), player_rect)
        for obstacle in obstacles:
            pygame.draw.rect(screen, (255, 0, 0), obstacle)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    reset_game()

        screen.fill((0, 0, 0))
        game_over_text = font.render("Game Over! Press ESC to exit.", True, (255, 255, 255))
        final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 - 60))

        leader_title = font.render("Таблица лидеров:", True, (255, 255, 255))
        screen.blit(leader_title, (WIDTH // 2 - leader_title.get_width() // 2, HEIGHT // 2))

        for idx, entry in enumerate(leaderboard):
            entry_text = font.render(f"{idx + 1}. {entry['name']} — {entry['score']}", True, (200, 200, 200))
            screen.blit(entry_text, (WIDTH // 2 - entry_text.get_width() // 2, HEIGHT // 2 + 40 + idx * 30))

        pygame.display.flip()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

pygame.quit()
sys.exit()
