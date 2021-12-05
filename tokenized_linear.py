import pygame
from pygame.locals import *
from pygame.rect import Rect
from pygame import Surface

from tokens import tokens as tk

import sys

PW = 16
W, H = 80, 80
col = [(255, 255, 255), (0, 0, 0)]
tobin8 = lambda n: (bin(n))[2:10][::-1] + '00000000'
tobin3 = lambda n: (bin(n))[2:5][::-1] + '000'

def drawn_rule(rule):
    surf = Surface((PW * 4 * 8, PW * 2))
    surf.fill((255, 255, 255))
    binary = tobin8(rule)
    for i, b in enumerate(binary):
        cell = tobin3(i)
        pygame.draw.rect(surf, (0, 0, 0), Rect((i*(PW*4), 0), (PW, PW)))
        pygame.draw.rect(surf, col[int(cell[2])], Rect((i*(PW*4)+1, 1), (PW-2, PW-2)))
        pygame.draw.rect(surf, (0, 0, 0), Rect(((i*(PW*4))+PW, 0), (PW, PW)))
        pygame.draw.rect(surf, col[int(cell[1])], Rect(((i*(PW*4))+PW+1, 1), (PW-2, PW-2)))
        pygame.draw.rect(surf, (0, 0, 0), Rect(((i*(PW*4))+(PW*2), 0), (PW, PW)))
        pygame.draw.rect(surf, col[int(cell[0])], Rect(((i*(PW*4))+(PW*2)+1, 1), (PW-2, PW-2)))
        pygame.draw.rect(surf, (0, 0, 0), Rect(((i*(PW*4))+PW, PW), (PW, PW)))
        pygame.draw.rect(surf, col[int(b)], Rect(((i*(PW*4))+PW+1, PW+1), (PW-2, PW-2)))
    return surf

def next_layer(grid, rule):
    rule = tobin8(rule)
    last = ['0',] + grid[-1] + ['0',]
    grid.append([])
    for i in range(1, len(last)-1):
        grid[-1].append(str(rule[int("0b"+"".join(last[i-1:i+2]), 2)]))

def drawn(rule):
    grid = [['0',]*W + ['1'] + ['0',]*W]
    for i in range(H): next_layer(grid, rule)
    surf = pygame.Surface(((W+1)*PW, H*PW))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line[W//2:W//2 + W + 1]):
            idx = x + W//2
            name = "000" + slot if y == 0 else "".join(grid[y-1][max(0, idx-1):idx+2])+slot
            tk.draw_token(surf, name, (x*PW, y*PW), PW=1)
    return surf

pygame.init()
SCREEN = pygame.display.set_mode(((min(80, W)+1) * PW, PW * min(40, H)))
pygame.display.set_caption(".,.,.,.,.,..,..,.,.,.,.`][`.,.,.,.,.,.,.,.,.,.,.,.,.")
HEL = pygame.font.SysFont("helvetica", PW * 2)
live = "-pic" not in sys.argv
num = 0
scroll = H
origH = H
img = drawn(num)
while live:
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: live = False
        if e.type == KEYDOWN:
            if e.key == K_LEFT:
                num = max(0, num - 1)
                img = drawn(num)
            if e.key == K_RIGHT:
                num += 1
                img = drawn(num)
            if e.key == K_DOWN: scroll -= 1
            if e.key == K_UP: scroll += 1
    if scroll > H:
        H += 1
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(drawn_rule(num), (0, 0))
    SCREEN.blit(HEL.render(str(num) + " : " + tobin8(num)[:8], 0, (0, 0, 0)), (0, PW*2))
    SCREEN.blit(img, (0, PW*(4+origH-scroll)))
    pygame.display.update()

if "-pic" in sys.argv:
    try:
        num = int(sys.argv[-1])
        pygame.image.save(drawn(num), "tokenized/"+str(num)+".png")
    except ValueError:
        while num < 256:
            pygame.image.save(drawn(num), "tokenized/"+str(num)+".png")
            num += 1
