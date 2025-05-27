import pygame
import sys
import random
import os
import socket
import threading
from pygame.locals import *

pygame.init()

# Window & Grid Setup
WINDOWWIDTH = 960
WINDOWHEIGHT = 600
CELLSIZE = 20
CELLWIDTH = WINDOWWIDTH // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Directions
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
HEAD = 0

# Pygame Setup
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
pygame.display.set_caption('UDP 2 Player Snake')

# Assets
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
EAT_SOUND = pygame.mixer.Sound(os.path.join(ASSET_DIR, "eat.wav"))
DIE_SOUND = pygame.mixer.Sound(os.path.join(ASSET_DIR, "die.mp3"))

# Items
apple_img = pygame.image.load(os.path.join(ASSET_DIR, "apple.png"))
strawberry_img = pygame.image.load(os.path.join(ASSET_DIR, "strawberry.png"))
grape_img = pygame.image.load(os.path.join(ASSET_DIR, "grape.png"))

ITEMS = [
    {"name": "apple", "img": apple_img, "score": 10},
    {"name": "strawberry", "img": strawberry_img, "score": 15},
    {"name": "grape", "img": grape_img, "score": 20},
]

# Global directions updated from UDP input and keyboard
directions = {
    'player1': RIGHT,
    'player2': RIGHT,
}

def getRandomItem():
    item = random.choice(ITEMS)
    pos = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    return {"type": item, "pos": pos}

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, BLACK, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, BLACK, (0, y), (WINDOWWIDTH, y))

def drawSnake(coords, color):
    for c in coords:
        x = c['x'] * CELLSIZE
        y = c['y'] * CELLSIZE
        pygame.draw.rect(DISPLAYSURF, color, pygame.Rect(x, y, CELLSIZE, CELLSIZE))

def drawItem(item):
    img = pygame.transform.scale(item['type']['img'], (CELLSIZE, CELLSIZE))
    x = item['pos']['x'] * CELLSIZE
    y = item['pos']['y'] * CELLSIZE
    DISPLAYSURF.blit(img, (x, y))

def showStartScreen():
    DISPLAYSURF.fill(WHITE)
    msg = BASICFONT.render('Use Keyboard or UDP Controller to Play! Press ESC to Quit', True, BLACK)
    rect = msg.get_rect()
    rect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    DISPLAYSURF.blit(msg, rect)
    pygame.display.update()

def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 9999))
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()
        if msg.startswith('player1:'):
            dir = msg.split(':')[1].lower()
            if dir in [UP, DOWN, LEFT, RIGHT]:
                current = directions['player1']
                # Cegah reverse direction
                if not (current == UP and dir == DOWN or
                        current == DOWN and dir == UP or
                        current == LEFT and dir == RIGHT or
                        current == RIGHT and dir == LEFT):
                    directions['player1'] = dir
        elif msg.startswith('player2:'):
            dir = msg.split(':')[1].lower()
            if dir in [UP, DOWN, LEFT, RIGHT]:
                current = directions['player2']
                if not (current == UP and dir == DOWN or
                        current == DOWN and dir == UP or
                        current == LEFT and dir == RIGHT or
                        current == RIGHT and dir == LEFT):
                    directions['player2'] = dir

def runGame():
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    snake1 = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    snake2 = [{'x': startx, 'y': starty + 5}, {'x': startx - 1, 'y': starty + 5}, {'x': startx - 2, 'y': starty + 5}]
    score1 = 0
    score2 = 0

    item = getRandomItem()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                # Keyboard override untuk player 1 (WASD)
                if event.key == K_w and directions['player1'] != DOWN:
                    directions['player1'] = UP
                elif event.key == K_s and directions['player1'] != UP:
                    directions['player1'] = DOWN
                elif event.key == K_a and directions['player1'] != RIGHT:
                    directions['player1'] = LEFT
                elif event.key == K_d and directions['player1'] != LEFT:
                    directions['player1'] = RIGHT
                # Keyboard override untuk player 2 (Arrow keys)
                elif event.key == K_UP and directions['player2'] != DOWN:
                    directions['player2'] = UP
                elif event.key == K_DOWN and directions['player2'] != UP:
                    directions['player2'] = DOWN
                elif event.key == K_LEFT and directions['player2'] != RIGHT:
                    directions['player2'] = LEFT
                elif event.key == K_RIGHT and directions['player2'] != LEFT:
                    directions['player2'] = RIGHT

        dir1 = directions['player1']
        dir2 = directions['player2']

        def move(snake, direction):
            head = snake[HEAD]
            if direction == UP:
                newY = head['y'] - 1
                if newY < 0:
                    newY = CELLHEIGHT - 1
                newHead = {'x': head['x'], 'y': newY}
            elif direction == DOWN:
                newY = head['y'] + 1
                if newY >= CELLHEIGHT:
                    newY = 0
                newHead = {'x': head['x'], 'y': newY}
            elif direction == LEFT:
                newX = head['x'] - 1
                if newX < 0:
                    newX = CELLWIDTH - 1
                newHead = {'x': newX, 'y': head['y']}
            elif direction == RIGHT:
                newX = head['x'] + 1
                if newX >= CELLWIDTH:
                    newX = 0
                newHead = {'x': newX, 'y': head['y']}
            snake.insert(0, newHead)
            return snake

        snake1 = move(snake1, dir1)
        snake2 = move(snake2, dir2)

        for i, snake in enumerate([snake1, snake2]):
            if snake[HEAD]['x'] == item['pos']['x'] and snake[HEAD]['y'] == item['pos']['y']:
                EAT_SOUND.play()
                if i == 0:
                    score1 += item['type']['score']
                else:
                    score2 += item['type']['score']
                item = getRandomItem()
            else:
                del snake[-1]

        for snake in [snake1, snake2]:
            if snake[HEAD] in snake[1:]:
                DIE_SOUND.play()
                pygame.time.wait(1500)
                return

        DISPLAYSURF.fill(WHITE)
        drawSnake(snake1, GREEN)
        drawSnake(snake2, BLUE)
        drawItem(item)
        drawGrid()

        scoreText1 = BASICFONT.render(f'P1: {score1}', True, WHITE, GREEN)
        scoreText2 = BASICFONT.render(f'P2: {score2}', True, WHITE, BLUE)
        DISPLAYSURF.blit(scoreText1, (10, 10))
        DISPLAYSURF.blit(scoreText2, (WINDOWWIDTH - 120, 10))

        pygame.display.update()
        FPSCLOCK.tick(10)

def main():
    showStartScreen()
    threading.Thread(target=udp_listener, daemon=True).start()
    while True:
        runGame()

if __name__ == '__main__':
    main()
