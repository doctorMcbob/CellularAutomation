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
from random import randint

import os
import sys

import pygame
from pygame import Surface, Rect
from pygame.locals import *


with open("neat.save", "r") as f:
    savelist = f.read().splitlines()

PW = 16
W, H = 63, 63
col = [(255, 255, 255), (0, 0, 0)]
tobin = lambda n, b: (('0' * b) + (bin(n))[2:])[-b:]

pygame.init()
SCREEN = pygame.display.set_mode(((W * 2)* PW  ,(H + 5) * PW))
pygame.display.set_caption("``` ^^^ ~~~ +++ === --- ... ,,, ___ /\\ ___ ,,, ... --- === +++ ~~~ ^^^ ```")
CLOCK = pygame.time.Clock()

HEL = pygame.font.SysFont("helvetica", PW)
live = True
play = False

num = 0

timer = 300 if "-t" not in sys.argv else int(sys.argv[sys.argv.index("-t") + 1])

STACK = []
FIRST_DUP = None

ROT_SYM, HORIZ_SYM, VERT_SYM = False, False, False
RECORD_MODE = False

BTN_POSITIONS = {
    "rotation": ((PW*80, PW*35), (PW*5, PW*2)),
    "horiz": ((PW*86, PW*35), (PW*4, PW*2)),
    "vert": ((PW*91, PW*35), (PW*4, PW*2)),
    "record": ((PW*96, PW*35), (PW*4, PW*2)),
}

def pack(grid): return "".join(["".join(row) for row in grid])
def unpack(string): return [list(string[i*W:(i+1)*W]) for i in range(H)]

# look it makes sense to me okay
def rotate_8bit(slot): return "".join([slot[i] for i in [5, 3, 0, 6, 1, 7, 4, 2]])
def flip_8bit_horiz(slot): return "".join([slot[i] for i in [2, 1, 0, 4, 3, 7, 6, 5]])
def flip_8bit_vert(slot): return "".join([slot[i] for i in [5, 6, 7, 3, 4, 0, 1, 2]])

def color(slot, state):
    r = int("".join([slot[i] for i in [5, 3, 0, 1, 2]]), 2) * 8
    g = int("".join([slot[i] for i in [1, 2, 4, 7, 6]]), 2) * 8
    b = int("".join([slot[i] for i in [7, 6, 5, 3, 0]]), 2) * 8

    if state == 1:
        r = max(0, r - 128)
        g = max(0, g - 128)
        b = max(0, b - 128)

    return (255-r, 255-g, 255-b)

def color2(slot, state):
    density = sum([int(n) for n in slot])
    thrd = 8 / 3
    r = 20 + (density               ) * (256 / 8)
    g = 190 + (density +   thrd      ) * (256 / 8)
    b = 210  + (density + ( thrd * 2 )) * (256 / 8)
    r %= 255
    g %= 255
    b %= 255
    r = int(r)
    g = int(g)
    b = int(b)
    if any((r, g, b)): print(r, g, b)
    return (r, g, b) if state == 0 else (255-r, 255-g, 255-b)

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
            if rand: cell = str(randint(0, 1))
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
            pygame.draw.rect(surf, color2(nbrs((x, y), grid), slot), Rect((x*PW+1, y*PW+1), (PW-2, PW-2)))
    return surf

def draw_buttons(dest, btn_positions=BTN_POSITIONS):
    btn_bools = {
        "vert": VERT_SYM,
        "horiz": HORIZ_SYM,
        "rotation": ROT_SYM,
        "record": RECORD_MODE
    }
    for name in btn_positions:
        pos, dim = btn_positions[name]
        pygame.draw.rect(dest, (50, 50, 50), Rect(pos, dim))
        pygame.draw.rect(dest, col[btn_bools[name]], Rect((pos[0]+1, pos[1]+1), (dim[0]-2, dim[1]-2)))
        dest.blit(HEL.render(name, 0, col[not btn_bools[name]]), (pos[0] + dim[0]//4, pos[1]+dim[1]//4))

def drawn_mini(grid):
    surf = Surface((W * 8, H * 8))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line):
            pygame.draw.rect(surf, color2(nbrs((x, y), grid), slot), Rect((x*8, y*8), (8, 8)))
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

def btn_click(btn_positions=BTN_POSITIONS):
    global ROT_SYM, HORIZ_SYM, VERT_SYM, RECORD_MODE
    pygame.display.update()
    x, y = pygame.mouse.get_pos()

    for name in btn_positions:
        if Rect(btn_positions[name]).collidepoint((x, y)):
            if name == "rotation": ROT_SYM = not ROT_SYM
            if name == "horiz": HORIZ_SYM = not HORIZ_SYM
            if name == "vert": VERT_SYM = not VERT_SYM
            if name == "record": RECORD_MODE = not RECORD_MODE
            

def rule_click(corner=(PW*80, PW*2)):
    global num, FIRST_DUP, STACK
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

    value = x + (y*16)
    
    if rule[value] == "0":
        num += 2 ** value
    else:
        num -= 2 ** value
    
    rule = tobin(num, 256)[::-1]
    if ROT_SYM:
        v = value
        for _ in range(3):
            _v = rotate_8bit(tobin(v, 8))
            v = int(_v, 2)
            if rule[v] == rule[value] or v == value: continue
            if rule[v] == "0":
                num += 2 ** v
            else:
                num -= 2 ** v

    rule = tobin(num, 256)[::-1]
    if HORIZ_SYM:
        _v = flip_8bit_horiz(tobin(value, 8))
        v = int(_v, 2)
        if rule[v] != rule[value] and v != value:
            if rule[v] == "0":
                num += 2 ** v
            else:
                num -= 2 ** v
                
    rule = tobin(num, 256)[::-1]
    if VERT_SYM:
        _v = flip_8bit_vert(tobin(value, 8))
        v = int(_v, 2)
        if rule[v] != rule[value] and v != value: 
            if rule[v] == "0":
                num += 2 ** v
            else:
                num -= 2 ** v

    rule = tobin(num, 256)[::-1]
    if HORIZ_SYM and VERT_SYM:
        _v = flip_8bit_horiz(tobin(value, 8))
        _v2 = flip_8bit_vert(_v)
        v = int(_v2, 2)
        if rule[v] != rule[value] and v != int(_v, 2) != value: 
            if rule[v] == "0":
                num += 2 ** v
            else:
                num -= 2 ** v

        
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
    return (x // PW) - 2, (y // PW) - 2


def save_interesting(n):
    with open("neat.save", "a") as f:
        f.write(str(n)+"\n")
    savelist.append(str(n))


def new(n=-1):
    global num, grid, t, FIRST_DUP, STACK
    num = n if n >= 0 else randint(0, 2**256)
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
            if e.key == K_c: grid = fresh_start(W, H)
            if e.key == K_s: save_interesting(num)
            if e.key == K_l: load_interesting()
            if e.key == K_SPACE: play = not play
            if e.key == K_RETURN: new(get_num())
            if e.key in [K_BACKSPACE, K_LEFT] and STACK: grid = unpack(STACK.pop())
            if e.key == K_RIGHT:
                layer = pack(grid)
                if layer in STACK and not FIRST_DUP:
                    FIRST_DUP = (STACK.index(layer), len(STACK))
                STACK.append(layer)
                grid = apply_rule(num, grid)

        if e.type == MOUSEBUTTONDOWN:
            x, y = get_mouse_logical()
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = "1" if grid[y][x] == "0" else "0"
                FIRST_DUP = None
                STACK = []
            else:
                rule_click()
                btn_click()
            
    SCREEN.fill((255, 255, 255))
    if str(num) in savelist: SCREEN.blit(HEL.render("Rule " + str(num) + " (S)", 0, (0, 0, 0)), (0, 0))
    else: SCREEN.blit(HEL.render("Rule " + str(num), 0, (0, 0, 0)), (0, 0))
    SCREEN.blit(drawn_grid(grid), (PW * 2, PW * 2))
    SCREEN.blit(drawn_rule(num), (PW * 80, PW * 2))
    if FIRST_DUP:
        SCREEN.blit(HEL.render("First Repeating: frame " + str(FIRST_DUP[0]) + " repeats on frame " + str(FIRST_DUP[1]), 0, (0, 0, 0)), (PW*80, PW * 56))
    SCREEN.blit(HEL.render("Frame: " + str(len(STACK)), 0, (0, 0, 0)), (PW*80, PW * 55))
    draw_buttons(SCREEN)
    pygame.display.update()

    if play:
        t += CLOCK.tick(30)
        if t > timer:
            if "-c" in sys.argv:
                if not os.path.isdir("colorpics/"+str(num)): os.mkdir("colorpics/"+str(num))
                pygame.image.save(drawn_mini(grid), "colorpics/"+str(num)+"/"+str(len(STACK))+".png")
            t = 0
            layer = pack(grid)
            if layer in STACK and not FIRST_DUP:
                FIRST_DUP = (STACK.index(layer), len(STACK))
            STACK.append(layer)
            grid = apply_rule(num, grid)

