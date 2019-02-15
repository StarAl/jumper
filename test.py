import pygame
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLCDNumber, QLabel, QLineEdit, QMainWindow, QInputDialog, QFontDialog
from pygame import *
import random
import os

pygame.init()

FPS = 50
WIDTH = 500
HEIGHT = 550

pygame.mixer.music.load('1.mp3')
pygame.mixer.music.play(-1)

init()
window = display.set_mode((WIDTH, HEIGHT))
display.set_caption('Jumping')
clock = time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image: ', name)
        raise SystemExit
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["В разработке"]

    fon = pygame.transform.scale(load_image('sky.jpg'), (WIDTH, HEIGHT))
    window.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        window.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return
        pygame.display.flip()
        clock.tick(FPS)



class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class player():
    def __init__(self):
        self.stand1 = image.load('stand1.png')
        self.fall = image.load('fall.png')
        self.jump_right = image.load('jump.png')
        self.jump_left = transform.flip(self.jump_right, True, False)
        self.stand = image.load('stand.png')

        self.reset()
    def reset(self):
        self.speed_x = 0
        self.speed_y = 0
        self.max_speed_x = 5
        self.max_speed_y = 15
        self.x_jumping = 0.5
        self.img = self.jump_right
        self.jump_speed = 15

        player_size = 7
        self.width, self.height = 7 * player_size, 12 * player_size
        self.scale = player_size

        self.x = (WIDTH - self.width) / 2
        self.y = HEIGHT - self.height

    def update(self, p):
        self.side_control()
        self.physics(p)
        self.move()
        self.show()

        self.x += self.speed_x
        self.y -= self.speed_y

        return (self.img, (self.x, self.y, self.width, self.height))

    def physics(self, p):

        on = False

        for colour, rect in p:
            x, y, w, h = rect

            if self.x + self.width / 2 > x and self.x - self.width / 2 < x + w:

                if self.y + self.height >= y and self.y + self.height <= y + h:

                    if self.speed_y < 0:
                        on = True

        if not on and not self.y >= HEIGHT - self.height:
            self.speed_y -= 0.5
        elif on:
            self.speed_y = self.jump_speed
        else:
            self.y = HEIGHT - self.height
            self.speed_x = 0
            self.speed_y = 0
            if self.x != (WIDTH - self.width) / 2:
                if self.x > (WIDTH - self.width) / 2:
                    self.x = max((WIDTH - self.width) / 2, self.x - 6)
                else:
                    self.x = min((WIDTH - self.width) / 2, self.x + 6)

            else:
                keys = key.get_pressed()
                if keys[K_SPACE]:
                    self.speed_y = self.jump_speed

    def side_control(self):
        if self.x + self.width < 0:
            self.x = WIDTH - self.scale
        if self.x > WIDTH:
            self.x = -self.width

    def show(self):
        if self.speed_y > 0:
            if self.speed_x > 0:
                self.img = self.jump_right
            elif self.speed_x < 0:
                self.img = self.jump_left
        else:
            self.img = self.fall

    def slow_character(self):
        if self.speed_x < 0: self.speed_x = min(0, self.speed_x + self.x_jumping / 6)
        if self.speed_x > 0: self.speed_x = max(0, self.speed_x - self.x_jumping / 6)

    def move(self):
        keys = key.get_pressed()

        if not self.y >= HEIGHT - self.height:

            if keys[K_LEFT] and keys[K_RIGHT]:
                self.slow_character()
            elif keys[K_LEFT]:
                self.speed_x -= self.x_jumping
            elif keys[K_RIGHT]:
                self.speed_x += self.x_jumping
            else:
                self.slow_character()

            self.speed_x = max(-self.max_speed_x, min(self.max_speed_x, self.speed_x))
            self.speed_y = max(-self.max_speed_y, min(self.max_speed_y, self.speed_y))


platform_spacing = 100


class Platform_Manager:
    def __init__(self):
        self.platforms = []
        self.spawns = 0
        self.start_spawn = HEIGHT

        scale = 3
        self.width, self.height = 24 * scale, 6 * scale

    def update(self):
        self.spawner()
        return self.manage()

    def spawner(self):
        if HEIGHT - info['screen_y'] > self.spawns * platform_spacing:
            self.spawn()

    def spawn(self):
        y = self.start_spawn - self.spawns * platform_spacing
        x = random.randint(-self.width, WIDTH)

        self.platforms.append(Platform(x, y, random.choice([1, -1])))
        self.spawns += 1

    def manage(self):
        u = []
        b = []
        for i in self.platforms:
            i.move()
            i.change_direction()
            b.append(i.show())

            if i.on_screen():
                u.append(i)

        self.platforms = u
        return b


class Platform:
    def __init__(self, x, y, direction):
        self.platform = image.load('sky.png')
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 2
        size = 3
        self.width, self.height = 25 * size, 6 * size #   Изменение параметров платформ!!!!!!!!!!!!!!!!!!!

    def move(self):
        self.x += self.speed * self.direction
        self.change_direction()

    def change_direction(self):
        if self.x <= 0:
            self.direction = 1
        if self.x + self.width >= WIDTH:
            self.direction = -1

    def on_screen(self):
        if self.y > info['screen_y'] + HEIGHT:
            return False
        return True

    def show(self):
        return ((255, 255, 255), (self.x, self.y, self.width, self.height))


def blit_images(x):
    for i in x:
        window.blit(transform.scale(i[0], (i[1][2], i[1][3])), (i[1][0], i[1][1] - info['screen_y']))


def event_loop():
    for loop in event.get():
        if loop.type == KEYDOWN:
            if loop.key == K_ESCAPE:
                quit()
        if loop.type == QUIT:
            quit()


f = font.SysFont('', 60)



def show_score(score, pos):
    message = f.render(str(round(score)), True, (255, 0, 0))
    rect = message.get_rect()

    if pos == 0:
        x = WIDTH - rect.width - 300
    else:
        x = 10
    y = rect.height + 10

    window.blit(message, (x, y))


info = {
    'screen_y': 0,
    'score': 0,
    'high_score': 0
}


BackGround = Background('background.jpg', [0, 0])
stick_man = player()
platform_manager = Platform_Manager()

while True:


    event_loop()

    platform_blit = platform_manager.update()
    stick_blit = stick_man.update(platform_blit)
    info['screen_y'] = min(min(0, stick_blit[1][1] - HEIGHT * 0.4), info['screen_y'])
    info['score'] = (-stick_blit[1][1] + 470) / 50

    if stick_blit[1][1] - 470 > info['screen_y']:
        info['score'] = 0
        info['screen_y'] = 0
        stick_man = player()
        platform_manager = Platform_Manager()

    clock.tick(60)

    window.fill((255, 255, 255))
    window.blit(BackGround.image, BackGround.rect)

    blit_images([stick_blit])

    for x in platform_blit:
        i = list(x)
        i[1] = list(i[1])
        i[1][1] -= info['screen_y']
        draw.rect(window, i[0], i[1])

    info['high_score'] = max(info['high_score'], info['score'])


    show_score(info['score'], 1)
    show_score(info['high_score'], 0)

    pygame.display.flip()
    all_sprites.draw(window)

    clock.tick(200)


    display.update()
pygame.quit()


