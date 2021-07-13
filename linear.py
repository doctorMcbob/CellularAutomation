import pygame
from pygame.locals import *
from pygame.rect import Rect
from pygame import Surface

PW = 8
W, H = 160, 90
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
    grid = [['0',]*(W//2) + ['1'] + ['0',]*(W//2)]
    for i in range(H): next_layer(grid, rule)
    surf = pygame.Surface(((W+1)*PW, H*PW))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line):
            pygame.draw.rect(surf, (0, 0, 0), Rect((x*PW, y*PW), (PW, PW)))
            pygame.draw.rect(surf, col[int(slot)], Rect((x*PW+1, y*PW+1), (PW-2, PW-2)))
    return surf

pygame.init()
SCREEN = pygame.display.set_mode(((W+1) * PW, PW * H))
pygame.display.set_caption(".,.,.,.,.,..,..,.,.,.,.`][`.,.,.,.,.,.,.,.,.,.,.,.,.")
HEL = pygame.font.SysFont("helvetica", PW * 2)
live = True
num = 0
scroll = H
origH = H
while live:
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: live = False
        if e.type == KEYDOWN:
            if e.key == K_LEFT: num = max(0, num - 1)
            if e.key == K_RIGHT: num += 1
            if e.key == K_DOWN: scroll -= 1
            if e.key == K_UP: scroll += 1
    if scroll > H:
        H += 1
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(drawn_rule(num), (0, 0))
    SCREEN.blit(HEL.render(str(num) + " : " + tobin8(num), 0, (0, 0, 0)), (0, PW*2))
    SCREEN.blit(drawn(num), (0, PW*(4+origH-scroll)))
    pygame.display.update()

    
