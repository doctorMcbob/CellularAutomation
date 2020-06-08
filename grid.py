"""
lemme just throw a docstring up here

keys:
  RETURN   |   type number for rule
  SPACE    |   play, pause
  r        |   random rule

soon ill put in drawing cells and customizing rules


essentially the same as the linear cellular automata,
but instead of the 3 cells above, its the 8 cells surrounding

rules are a binary number between 0 and 2^256

neighboring cells are converted to binary

0 0 1
1   0
0 1 1

becomes 00110011 becomes 51

then the 51(th) index of the binary rule becomes the cells value in the next generation


2^2^8 or 2^256 possible rules (thats a lot!)

TO DO LIST
[] save interesting rules to file
[] mouse functionality for drawing
[] rule "builder"
... all 256 possible permutations visualised
    in a GUI so you can set the exact rule you want
"""
import pygame
from pygame import Surface, Rect
from pygame.locals import *

from random import randint

PW = 16
W, H = 81, 42
col = [(255, 255, 255), (0, 0, 0)]
tobin = lambda n, b: (('0' * b) + (bin(n))[2:])[-b:]

def nbrs(pos, grid):
    X, Y = pos
    ret = ""
    for _y in range(Y-1, Y+2):
        for _x in range(X-1, X+2):
            if (X, Y) == (_x, _y): continue
            ret = grid[_y % H][_x % W] + ret
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
    rule = tobin(rule, 256)[::-1]
    new = []
    for y, line in enumerate(grid):
        new.append([])
        for x, slot in enumerate(line):
            n = nbrs((x, y), grid)
            new[-1].append(rule[int(n, 2)])
    return new

def drawn_grid(grid):
    surf = Surface((W * PW, H * PW))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line):
            pygame.draw.rect(surf, (50, 50, 50), Rect((x*PW, y*PW), (PW, PW)))
            pygame.draw.rect(surf, col[int(slot)], Rect((x*PW+1, y*PW+1), (PW-2, PW-2)))
    return surf
            
numkeys = {K_0:"0",K_1:"1",K_2:"2",K_3:"3",K_4:"4",K_5:"5",K_6:"6",K_7:"7",K_8:"8",K_9:"9"}
def get_num():
    n = ""
    while True:
        surf = Surface((W*PW, PW))
        surf.fill((150, 150, 150))
        surf.blit(HEL.render(n, 0, (0, 0, 0)), (0, 0))
        SCREEN.blit(surf, (0, PW))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
            if e.type == KEYDOWN:
                if e.key in numkeys: n += numkeys[e.key]
                if e.key == K_BACKSPACE: n = n[:-1]
                if e.key == K_RETURN: return int(n) if n else 0

pygame.init()
SCREEN = pygame.display.set_mode((W * PW, (H + 2) * PW))
pygame.display.set_caption("``` ^^^ ~~~ +++ === --- ... ,,, ___ /\\ ___ ,,, ... --- === +++ ~~~ ^^^ ```")
CLOCK = pygame.time.Clock()

HEL = pygame.font.SysFont("helvetica", PW)
live = True
play = True

def new(n=False):
    global num, grid, t
    num = n or randint(0, 2**256)
    grid = fresh_start(W, H)
    t = 0

new()

while live:
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: live = False
        if e.type == KEYDOWN:
            if e.key == K_r: new()
            if e.key == K_SPACE: play = not play
            if e.key == K_RETURN: new(get_num())
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(HEL.render("Rule " + str(num), 0, (0, 0, 0)), (0, 0))
    SCREEN.blit(drawn_grid(grid), (0, PW * 2))
    pygame.display.update()
    if play:
        t += CLOCK.tick(30)
        if t > 300:
            t = 0
            grid = apply_rule(num, grid)
