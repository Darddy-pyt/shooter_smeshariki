#Создай собственный Шутер!
from pygame import *
from random import randint, choice
import time as tm

# Инициализация модулей
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# Константы
WIDTH, HEIGHT = 700, 500
back_img = 'смешарики.jpg'
img_igrok = 'крош.png'
img_enemy = 'лысяшь.png'
img_potron = 'молока.jpg'
buff_types = ['марковка.jpg', 'смефно.jpg']  # Изображения баффов

# Настройки игры
score = 0
lost = 0
max_lost = 3
max_score = 10

# Инициализация шрифтов
font.init()
font2 = font.Font(None, 36)
win = font2.render("ТЫ ВЫЙГРАЛ !", True, (255, 255, 255))
lose = font2.render("ТЫ проиграл ЛОШАРА", True, (180, 180, 180))
buff_font = font.Font(None, 24)
difficulty_font = font.Font(None, 48)

# Классы игровых объектов
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed

        if keys[K_RIGHT] and self.rect.x < WIDTH - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_potron, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > HEIGHT:
            self.rect.x = randint(80, WIDTH - 80)
            self.rect.y = 0
            lost += 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

class Buff(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()

# Создание игрового окна
screen = display.set_mode((WIDTH, HEIGHT))
background = transform.scale(image.load(back_img), (WIDTH, HEIGHT))
display.set_caption("Футел")

# Создание игровых объектов
ship = Player(img_igrok, 5, HEIGHT - 100, 80, 100, 10)
monsters = sprite.Group()
bullets = sprite.Group()
buffs = sprite.Group()

# Выбор сложности и режима игры
def choose_difficulty():
    global difficulty, max_lost, max_score
    difficulty = None
    while difficulty is None:
        screen.blit(background, (0, 0))
        text = difficulty_font.render("Выберите сложность:", True, (255, 255, 255))
        screen.blit(text, (150, 100))
        
        easy_text = font2.render("Легко", True, (0, 255, 0))
        screen.blit(easy_text, (250, 200))
        
        medium_text = font2.render("Средне", True, (255, 255, 0))
        screen.blit(medium_text, (250, 250))
        
        hard_text = font2.render("Сложно", True, (255, 0, 0))
        screen.blit(hard_text, (250, 300))
        
        display.update()
        
        for e in event.get():
            if e.type == QUIT:
                exit()
            elif e.type == MOUSEBUTTONDOWN:
                if 250 < e.pos[0] < 350 and 200 < e.pos[1] < 230:
                    difficulty = "easy"
                    max_lost = 5
                    max_score = 15
                elif 250 < e.pos[0] < 350 and 250 < e.pos[1] < 280:
                    difficulty = "medium"
                    max_lost = 3
                    max_score = 10
                elif 250 < e.pos[0] < 350 and 300 < e.pos[1] < 330:
                    difficulty = "hard"
                    max_lost = 1
                    max_score = 5

    # Выбор режима игры
    global game_mode
    game_mode = None
    while game_mode is None:
        screen.blit(background, (0, 0))
        text = difficulty_font.render("Выберите режим игры:", True, (255, 255, 255))
        screen.blit(text, (150, 100))
        
        score_text = font2.render("На счёт", True, (0, 255, 0))
        screen.blit(score_text, (250, 200))
        
        infinite_text = font2.render("Бесконечный", True, (255, 255, 0))
        screen.blit(infinite_text, (250, 250))
        
        display.update()
        
        for e in event.get():
            if e.type == QUIT:
                exit()
            elif e.type == MOUSEBUTTONDOWN:
                if 250 < e.pos[0] < 350 and 200 < e.pos[1] < 230:
                    game_mode = "score"
                elif 250 < e.pos[0] < 350 and 250 < e.pos[1] < 280:
                    game_mode = "infinite"
                    max_lost = 1000  # Для бесконечного режима

    # Создание врагов в зависимости от сложности
    global monsters
    monsters.empty()
    for i in range(1, 6):
        if difficulty == "easy":
            monster = Enemy(img_enemy, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 3))
        elif difficulty == "medium":
            monster = Enemy(img_enemy, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 6))
        elif difficulty == "hard":
            monster = Enemy(img_enemy, randint(80, WIDTH - 80), -40, 80, 50, randint(3, 8))
        monsters.add(monster)

choose_difficulty()

last_fired = tm.time()
running = True
finish = False
ship_protected = False
buff_message = ""

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if tm.time() - last_fired >= 0.7:
                    fire_sound.play()
                    ship.fire()
                    last_fired = tm.time()

            elif e.key == K_ESCAPE:
                running = False
            elif e.key == K_p:
                paused = True
                mixer.music.pause()
                while paused:
                    text_pause = font2.render("Пауза", 1, (255, 0, 0))
                    screen.blit(text_pause, (250, 250))
                    display.update()

                    for e in event.get():
                        if e.type == QUIT:
                            paused = False
                        elif e.type == KEYDOWN:
                            if e.key == K_p:
                                paused = False
                                mixer.music.unpause()

            elif e.key == K_BACKSPACE:
                score = 0
                lost = 0
                finish = False

                ship.rect.x = 5
                buffs.empty()  # Очистить баффы
                buff_message = ""
                choose_difficulty()

    if not finish:
        screen.blit(background, (0, 0))

        text = font2.render("Счёт:" + str(score), 1, (255, 255, 255))
        screen.blit(text, (10, 20))

        text_lose = font2.render("Пропущено:" + str(lost), 1, (255, 255, 255))
        screen.blit(text_lose, (10, 50))

        ship.update()
        monsters.update()
        bullets.update()
        buffs.update()

        ship.reset()
        monsters.draw(screen)
        bullets.draw(screen)
        buffs.draw(screen)

        # Создание баффов реже
        if randint(1, 200) < 5:  # Появляются реже
            buff_image = choice(buff_types)
            buff = Buff(buff_image, randint(0, WIDTH - 50), 0, 50, 50, 2)
            buffs.add(buff)

        # Проверка столкновений с врагами
        if sprite.spritecollide(ship, monsters, False) and not ship_protected:
            if game_mode == "score":
                finish = True
                screen.blit(lose, (200, 200))
            elif game_mode == "infinite":
                ship.rect.x = 5

        # Проверка столкновений с баффами
        collides_buff = sprite.spritecollide(ship, buffs, True)
        for buff in collides_buff:
            if buff.image == image.load('марковка.jpg'):
                ship.speed += 10  # Увеличение скорости на 10
                buff_message = "Поднят бафф: Увеличение скорости"
                print("Скорость увеличена!")
            elif buff.image == image.load('смефно.jpg'):
                ship_protected = True
                buff_message = "Поднят бафф: Временная защита"
                if lost > 0:  # Уменьшение счетчика пропущенных врагов
                    lost -= 1
                protection_time = tm.time()
                while tm.time() - protection_time < 5 and running:
                    # Защита активна
                    for e in event.get():
                        if e.type == QUIT:
                            running = False
                    display.update()
                    time.delay(100)
                ship_protected = False

        # Отображение сообщения о баффе
        if buff_message:
            buff_text = buff_font.render(buff_message, True, (255, 255, 255))
            screen.blit(buff_text, (10, 80))
            if tm.time() % 2 < 1:  # Мигание текста
                buff_text = buff_font.render(buff_message, True, (0, 0, 0))
                screen.blit(buff_text, (10, 80))
            tm.sleep(0.01)  # Задержка для мигания
            if tm.time() % 5 < 1:  # Сброс сообщения через 5 секунд
                buff_message = ""

        # Проверка столкновений с пулями и врагами
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            if difficulty == "easy":
                monster = Enemy(img_enemy, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 3))
            elif difficulty == "medium":
                monster = Enemy(img_enemy, randint(80, WIDTH - 80), -40, 80, 50, randint(1, 6))
            elif difficulty == "hard":
                monster = Enemy(img_enemy, randint(80, WIDTH - 80), -40, 80, 50, randint(3, 8))
            monsters.add(monster)

        if game_mode == "score" and score >= max_score:
            finish = True
            screen.blit(win, (200, 200))

        display.update()

    time.delay(40)
    #test