"""
lemme just throw a docstring up here

keys:
  RETURN   |   type number for rule
  SPACE    |   play, pause
  r        |   random rule
  c        |   clear (reset board)
  s        |   save rule

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
[x] save interesting rules to file
[x] load interesting
[x] mouse functionality for drawing
[x] rule "builder"
... all 256 possible permutations visualised
    in a GUI so you can set the exact rule you want

REDUX; i want a display on screen that shows the rule visualised at all times, make the grid smaller to fit it
then you can alter the rule as it goes easily

rule loader as well

"""
import pygame
from pygame import Surface, Rect
from pygame.locals import *

from random import randint

with open("neat.save", "r") as f:
    savelist = f.read().splitlines()

PW = 16
W, H = 33, 33
col = [(255, 255, 255), (0, 0, 0)]
tobin = lambda n, b: (('0' * b) + (bin(n))[2:])[-b:]

def nbrs(pos, grid):
    X, Y = pos
    ret = ""
    for _y in range(Y-1, Y+2)[::-1]:
        for _x in range(X-1, X+2):
            if (X, Y) == (_x, _y): continue
            ret = grid[_y % H][_x % W] + ret
    return ret[::-1]


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


def drawn_rule_seg(bit, on=False):
    surf = Surface((PW * 1.5, PW * 1.5))
    surf.fill((255, 255, 255))
    x, y = (0, 2)
    for i in bit:
        pygame.draw.rect(surf, (50, 50, 50), Rect((x*(PW//2), y*(PW//2)), (PW//2, PW//2)))
        if (x, y) == (1, 1):
            pygame.draw.rect(surf, [(255, 255, 255), (50, 150, 50)][int(on)], Rect((x*(PW//2)+1, y*(PW//2)+1), ((PW//2)-2, (PW//2)-2)))
            x += 1
            pygame.draw.rect(surf, (50, 50, 50), Rect((x*(PW//2), y*(PW//2)), (PW//2, PW//2)))

        pygame.draw.rect(surf, col[int(i)], Rect((x*(PW//2)+1, y*(PW//2)+1), ((PW//2)-2, (PW//2)-2)))

        x += 1
        if x == 3:
            x = 0
            y -= 1

    return surf


def drawn_rule(rule):
    rule = tobin(rule, 256)[::-1]
    surf = Surface((PW * 4 * 8, PW * 4 * 8))
    surf.fill((255, 255, 255))
    x, y = 0, 0
    for i in range(256):
        b = tobin(i, 8)

        surf.blit(drawn_rule_seg(b, "1" == rule[i]), (x * (PW//2) * 4, y * (PW//2) * 4))
        
        x += 1
        if x == 16:
            x = 0
            y += 1

    return surf


def rule_click(corner=(PW*40, PW*2)):
    global num
    pygame.display.update()
    x, y = pygame.mouse.get_pos()
    cx, cy = corner
    if not( cx < x < cx+PW*4*8 and cy < y < cy+PW*4*8 ):
        return
    rule = tobin(num, 256)[::-1]
    x -= cx
    y -= cy
    x = x // (PW // 2)
    y = y // (PW // 2)
    x = x // 4
    y = y // 4

    if rule[x + (y*16)] == "0":
        num += 2 ** (x + (y * 16))
    else:
        num -= 2 ** (x + (y * 16))
    
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


def get_mouse_logical():
    pygame.display.update()
    x, y = pygame.mouse.get_pos()
    return (x // PW) - 2, (y // PW) - 2


def save_interesting(n):
    with open("neat.save", "a") as f:
        f.write(str(n)+"\n")
    savelist.append(str(n))

pygame.init()
SCREEN = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("``` ^^^ ~~~ +++ === --- ... ,,, ___ /\\ ___ ,,, ... --- === +++ ~~~ ^^^ ```")
CLOCK = pygame.time.Clock()

HEL = pygame.font.SysFont("helvetica", PW)
live = True
play = False

num = 0

def new(n=-1):
    global num, grid, t
    num = n if n >= 0 else randint(0, 2**256)
    grid = fresh_start(W, H)
    t = 0

def load_interesting():
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(HEL.render("number between 0 and " + str(len(savelist)-1), 0, (0, 0, 0)), (0, 0))
    for i in range(len(savelist)):
        SCREEN.blit(HEL.render(str(i) + " : " + str(savelist[i]), 0, (0, 0, 0)), (0, PW*2+(i*PW)))
    pygame.display.update()
    n = get_num()
    if n < len(savelist):
        new(int(savelist[n]))

new(0)

while live:
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: live = False
        if e.type == KEYDOWN:
            if e.key == K_r: new()
            if e.key == K_c: grid = fresh_start(W, H)
            if e.key == K_s: save_interesting(num)
            if e.key == K_l: load_interesting()
            if e.key == K_SPACE: play = not play
            if e.key == K_RETURN: new(get_num())

        if e.type == MOUSEBUTTONDOWN:
            x, y = get_mouse_logical()
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = "1" if grid[y][x] == "0" else "0"
            else:
                rule_click()
            
    SCREEN.fill((255, 255, 255))
    if str(num) in savelist: SCREEN.blit(HEL.render("Rule " + str(num) + " (S)", 0, (0, 0, 0)), (0, 0))
    else: SCREEN.blit(HEL.render("Rule " + str(num), 0, (0, 0, 0)), (0, 0))
    SCREEN.blit(drawn_grid(grid), (PW * 2, PW * 2))
    SCREEN.blit(drawn_rule(num), (PW * 40, PW * 2))
    pygame.display.update()
    if play:
        t += CLOCK.tick(30)
        if t > 300:
            t = 0
            grid = apply_rule(num, grid)
