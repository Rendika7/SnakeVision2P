import pygame, sys, random, os
from pygame.locals import *

pygame.init()

# Window & Grid Setup
WINDOWWIDTH = 960  # Ukuran diperbesar
WINDOWHEIGHT = 600
CELLSIZE = 20
CELLWIDTH = WINDOWWIDTH // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Arah
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
HEAD = 0

# Game Window
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
pygame.display.set_caption('2 Player Snake')

# Load Assets
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
apple_img = pygame.image.load(os.path.join(ASSET_DIR, "apple.png"))
strawberry_img = pygame.image.load(os.path.join(ASSET_DIR, "strawberry.png"))
grape_img = pygame.image.load(os.path.join(ASSET_DIR, "grape.png"))

EAT_SOUND = pygame.mixer.Sound(os.path.join(ASSET_DIR, "eat.wav"))
DIE_SOUND = pygame.mixer.Sound(os.path.join(ASSET_DIR, "die.mp3"))

# Item definitions
ITEMS = [
    {"name": "apple", "img": apple_img, "score": 10},
    {"name": "strawberry", "img": strawberry_img, "score": 15},
    {"name": "grape", "img": grape_img, "score": 20},
]

# Get Random Apple
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
    msg = BASICFONT.render('Press Any Key To Start 2-Player Snake', True, BLACK)
    rect = msg.get_rect()
    rect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    DISPLAYSURF.blit(msg, rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                return

def runGame():
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    snake1 = [{'x': startx, 'y': starty}, {'x': startx-1, 'y': starty}, {'x': startx-2, 'y': starty}]
    snake2 = [{'x': startx, 'y': starty+5}, {'x': startx-1, 'y': starty+5}, {'x': startx-2, 'y': starty+5}]
    dir1 = RIGHT
    dir2 = RIGHT
    item = getRandomItem()
    score1 = 0
    score2 = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_w and dir1 != DOWN: dir1 = UP
                elif event.key == K_s and dir1 != UP: dir1 = DOWN
                elif event.key == K_a and dir1 != RIGHT: dir1 = LEFT
                elif event.key == K_d and dir1 != LEFT: dir1 = RIGHT
                elif event.key == K_UP and dir2 != DOWN: dir2 = UP
                elif event.key == K_DOWN and dir2 != UP: dir2 = DOWN
                elif event.key == K_LEFT and dir2 != RIGHT: dir2 = LEFT
                elif event.key == K_RIGHT and dir2 != LEFT: dir2 = RIGHT

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
            if (snake[HEAD]['x'] < 0 or snake[HEAD]['x'] >= CELLWIDTH or
                snake[HEAD]['y'] < 0 or snake[HEAD]['y'] >= CELLHEIGHT):
                DIE_SOUND.play()
                pygame.time.wait(1500)
                return

        DISPLAYSURF.fill(WHITE)
        drawSnake(snake1, GREEN)
        drawSnake(snake2, BLUE)
        drawItem(item)
        drawGrid()

        # Skor dengan background
        scoreText1 = BASICFONT.render(f'P1: {score1}', True, WHITE, GREEN)
        scoreText2 = BASICFONT.render(f'P2: {score2}', True, WHITE, BLUE)
        DISPLAYSURF.blit(scoreText1, (10, 10))
        DISPLAYSURF.blit(scoreText2, (WINDOWWIDTH - 120, 10))

        pygame.display.update()
        FPSCLOCK.tick(10)

if __name__ == '__main__':
    showStartScreen()
    while True:
        runGame()