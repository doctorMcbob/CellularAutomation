"""
Same thesis as totalistic.py but 2d on a grid
"""
import pygame
from pygame import Surface, Rect
from pygame.locals import *

from random import randint
from copy import deepcopy

import os
import sys

with open("totalneat.save", "r") as f:
    savelist = f.read().splitlines()

PW = 16
W, H = 63, 63

pygame.init()
SCREEN = pygame.display.set_mode((PW * W + PW * 4, PW * H + PW * 8))
pygame.display.set_caption("``` ^^^ ~~~ +++ === --- ... ,,, ___ /\\ ___ ,,, ... --- === +++ ~~~ ^^^ ```")
CLOCK = pygame.time.Clock()
FLIP = False

HEL = pygame.font.SysFont("helvetica", PW)
live = True
play = False

num = 0

timer = 300 if "-t" not in sys.argv else int(sys.argv[sys.argv.index("-t") + 1])

STACK = []
FIRST_DUP = None

def getcol(base, n):
    unit = 255 // (base - 1)
    c = max(0, 255 - unit * n)
    return (c, c, c)

def tobase(base, n):
    if n == 0: return '0' * 17
    tern = []
    while n:
        n, r = divmod(n, base)
        tern.append(str(r))
    tern =  '0' * 17 + ''.join(tern[::-1])
    tern = tern[::-1]
    return tern[:17][::-1]

def nbrs(pos, grid):
    X, Y = pos
    ret = []
    for _y in range(Y-1, Y+2)[::-1]:
        for _x in range(X-1, X+2):
            if (X, Y) == (_x, _y): continue
            ret.append(grid[_y % H][_x % W])
    return ret

def fresh_start(W, H, rand=False):
    grid = []
    for y in range(H):
        grid.append([])
        for x in range(W):
            if rand: cell = str(randint(0, 1))
            else: cell = 0 if (x, y) != (W // 2, H // 2) else 1
            grid[-1].append(cell)
    return grid

def apply_rule(rule, grid):
    rule = tobase(3, rule)
    new = []
    for y, line in enumerate(grid):
        new.append([])
        for x, slot in enumerate(line):
            n = nbrs((x, y), grid)
            new[-1].append(int(rule[sum(n)]))
    return new

def drawn_grid(grid):
    surf = Surface((W * PW, H * PW))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line):
            n = nbrs((x, y), grid)
            col = getcol(3, int(slot)) if not FLIP else getcol(17, sum(n))
            pygame.draw.rect(surf, (50, 50, 50), Rect((x*PW, y*PW), (PW, PW)))
            pygame.draw.rect(surf, col, Rect((x*PW+1, y*PW+1), (PW-2, PW-2)))
    return surf

def drawn_mini(grid):
    surf = Surface((W * 8, H * 8))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line):
            pygame.draw.rect(surf, getcol(3, int(slot)), Rect((x*8, y*8), (8, 8)))
    return surf

def drawn_rule_seg(average, val=0):
    surf = Surface((PW * 1.5, PW * 1.5))
    surf.fill((255, 255, 255))
    x, y = (0, 2)
    for i in range(8):
        pygame.draw.rect(surf, (50, 50, 50), Rect((x*(PW//2), y*(PW//2)), (PW//2, PW//2)))
        if (x, y) == (1, 1):
            pygame.draw.rect(surf, getcol(3, val), Rect((x*(PW//2)+1, y*(PW//2)+1), ((PW//2)-2, (PW//2)-2)))
            x += 1
            pygame.draw.rect(surf, (50, 50, 50), Rect((x*(PW//2), y*(PW//2)), (PW//2, PW//2)))
        pygame.draw.rect(surf, getcol(17, average), Rect((x*(PW//2)+1, y*(PW//2)+1), ((PW//2)-2, (PW//2)-2)))
        x += 1
        if x == 3:
            x = 0
            y -= 1
    return surf

def drawn_rule(rule):
    rule = tobase(3, rule)
    surf = Surface((PW *2*17, PW *1.5))
    surf.fill((255, 255, 255))
    for i in range(17):
        surf.blit(drawn_rule_seg(i, int(rule[i])), (i * (PW//2) * 4, 0))
    return surf


def rule_click(base=3, corner=(PW*2, PW*2)):
    global num, FIRST_DUP, STACK
    pygame.display.update()
    x, y = pygame.mouse.get_pos()
    cx, cy = corner
    if not( cx < x < cx + PW*2*17 and cy < y < cy + PW*1.5 ):
        return
    rule = list(tobase(base, num))
    idx = x // (PW * 2) - 1
    rule[idx] = str((int(rule[idx]) + 1) % base)
    num = int(''.join(rule), base)
    FIRST_DUP = None
    STACK = []

        
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
    return (x // PW) - 2, (y // PW) - 4


def save_interesting(n):
    with open("totalneat.save", "a") as f:
        f.write(str(n)+"\n")
    savelist.append(str(n))


def new(n=-1):
    global num, grid, t, FIRST_DUP, STACK
    num = n if n >=0 else randint(0, 3 ** 17)
    grid = fresh_start(W, H)
    t = 0
    FIRST_DUP = None
    STACK = []

def load_interesting():
    global FIRST_DUP, STACK
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(HEL.render("number between 0 and " + str(len(savelist)-1), 0, (0, 0, 0)), (0, 0))
    for i in range(len(savelist)):
        SCREEN.blit(HEL.render(str(i) + " : " + str(savelist[i]), 0, (0, 0, 0)), (0, PW*2+(i*PW)))
    pygame.display.update()
    n = get_num()
    if n < len(savelist):
        new(int(savelist[n]))
    FIRST_DUP = None
    STACK = []
        
new(0)

while live:
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: live = False
        if e.type == KEYDOWN:
            if e.key == K_r: new()
            if e.key == K_d: new(0)
            if e.key == K_c:
                grid = fresh_start(W, H)
            if e.key == K_s: save_interesting(num)
            if e.key == K_l: load_interesting()
            if e.key == K_TAB: FLIP = not FLIP
            if e.key == K_SPACE: play = not play
            if e.key == K_RETURN: new(get_num())
            if e.key in [K_BACKSPACE, K_LEFT] and STACK:
                grid = STACK.pop()
            if e.key == K_RIGHT:
                layer = deepcopy(grid)
                if layer in STACK and not FIRST_DUP:
                    FIRST_DUP = (STACK.index(layer), len(STACK))
                STACK.append(layer)
                grid = apply_rule(num, grid)
        if e.type == MOUSEBUTTONDOWN:
            x, y = get_mouse_logical()
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = (grid[y][x] + 1) % 3
                FIRST_DUP = None
                STACK = []
            else:
                rule_click()
            
    SCREEN.fill((255, 255, 255))
    if str(num) in savelist: SCREEN.blit(HEL.render("Rule " + str(num) + " (S)", 0, (0, 0, 0)), (0, 0))
    else: SCREEN.blit(HEL.render("Rule " + str(num), 0, (0, 0, 0)), (0, 0))
    SCREEN.blit(drawn_grid(grid), (PW * 2, PW * 4))
    SCREEN.blit(drawn_rule(num), (PW * 2, PW * 2))
    if FIRST_DUP:
        SCREEN.blit(HEL.render("First Repeating: frame " + str(FIRST_DUP[0]) + " repeats on frame " + str(FIRST_DUP[1]), 0, (0, 0, 0)), (0, PW * 38))
    SCREEN.blit(HEL.render("Frame: " + str(len(STACK)), 0, (0, 0, 0)), (0, PW * 37))
    pygame.display.update()

    if play:
        t += CLOCK.tick(30)
        if t > timer:
            if "-c" in sys.argv:
                if not os.path.isdir("totalisticpics/"+str(num)): os.mkdir("totalisticpics/"+str(num))
                pygame.image.save(drawn_mini(grid), "totalisticpics/"+str(num)+"/"+str(len(STACK))+".png")
            t = 0
            layer = deepcopy(grid)
            if layer in STACK and not FIRST_DUP:
                FIRST_DUP = (STACK.index(layer), len(STACK))
            STACK.append(layer)
            prev = grid
            grid = apply_rule(num, grid)

