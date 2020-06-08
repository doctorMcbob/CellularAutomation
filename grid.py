"""
lemme just throw a docstring up here

keys:
  SPACE    |   play, pause
  r        |   random rule

soon ill put in drawing cells and customizing rules

rules are a binary representation of the 8 neighboring cells

0 1 2
3   4
5 6 7

2^2^8 possible rules (thats a lot!)
"""
import pygame
from pygame import Surface, Rect
from pygame.locals import *

from random import randint

PW = 16
W, H = 81, 40
col = [(255, 255, 255), (0, 0, 0)]
tobin = lambda n, b: ((bin(n))[2:][::-1] + ('0' * b))[:b]

def nbrs(pos, grid):
    X, Y = pos
    ret = ""
    for _y in range(Y-1, Y+2):
        for _x in range(X-1, X+2):
            if (X, Y) == (_x, _y): continue
            ret += grid[_y % H][_x % W]
    return ret

def fresh_start(W, H, rand=False):
    grid = []
    for y in range(H):
        grid.append([])
        for x in range(W):
            if rand: cell = "0" if randint(0, 1) else "1"
            else: cell = "0" if (x, y) != (W // 2, H // 2) else "1"
            grid[-1].append(cell)
    return grid

def apply_rule(rule, grid):
    rule = tobin(rule, 256)
    new = []
    for y, line in enumerate(grid):
        new.append([])
        for x, slot in enumerate(line):
            n = nbrs((x, y), grid)
            new[-1].append(rule[int("0b"+n, 2)])
    return new

def drawn_grid(grid):
    surf = Surface((W * PW, H * PW))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line):
            pygame.draw.rect(surf, (50, 50, 50), Rect((x*PW, y*PW), (PW, PW)))
            pygame.draw.rect(surf, col[int(slot)], Rect((x*PW+1, y*PW+1), (PW-2, PW-2)))
    return surf
            

pygame.init()
SCREEN = pygame.display.set_mode((81 * PW, 42* PW))
pygame.display.set_caption("~~~ ... ___ /\\ ___ ... ~~~")
CLOCK = pygame.time.Clock()

HEL = pygame.font.SysFont("helvetica", PW)
live = True
play = True

num = randint(0, 2**256)
grid = fresh_start(W, H)
t = 0

def new_random():
    global num, grid, t
    num = randint(0, 2**256)
    grid = fresh_start(W, H)
    t = 0

while live:
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: live = False
        if e.type == KEYDOWN:
            if e.key == K_r: new_random()
            if e.key == K_SPACE: play = not play
            
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(HEL.render("Rule " + str(num), 0, (0, 0, 0)), (0, 0))
    SCREEN.blit(drawn_grid(grid), (0, PW * 2))
    pygame.display.update()
    if play:
        t += CLOCK.tick(30)
        if t > 300:
            t = 0
            grid = apply_rule(num, grid)
