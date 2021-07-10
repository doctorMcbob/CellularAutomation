"""
I started reading stephan wolframs A New Kind of Science
He talked about a spin on this type of cellular automata that was following a totalistic color system

basically there are 3 states, black gray and white.

the rule then tells what state to become not from the orientation of the cells, but the average color of the neighbors.

im imagening doing it like based on the sum of the neighbors.
  for example if we let 0, 1, 2 be black gray and white respectively
  2 2 2 as the maximum and 0 0 0 as the minimum we simply map out 0 through 6 as our rule

[vision]
               (i)
cells = [... 2, 1, 1, ...]

rule = "001022"

cells[i] = int(
               rule[
                    sum(
                        cells[i-1:i+1]
                        )
                    ]
               )
"""
import pygame
from pygame.locals import *
from pygame.rect import Rect
from pygame import Surface

PW = 8
W, H = 160, 90

def getcol(base, n):
    unit = 255 // (base - 1)
    c = max(0, 255 - unit * n)
    return (c, c, c)

def tobase(base, n):
    if n == 0: return '0000000'
    tern = []
    while n:
        n, r = divmod(n, base)
        tern.append(str(r))
    tern =  '0000000' + ''.join(tern[::-1])
    tern = tern[::-1]
    return tern[:7]

def avg(nums):
    average = sum(nums) / len(nums)
    return int(average*3)

def drawn_rule(rule):
    surf = Surface((PW * 4 * 8, PW * 2))
    surf.fill((255, 255, 255))
    rule = tobase(3, rule)
    for i, b in enumerate(rule):
        pygame.draw.rect(surf, (0, 0, 0), Rect((i*(PW*4), 0), (PW, PW)))
        pygame.draw.rect(surf, getcol(7, i), Rect((i*(PW*4)+1, 1), (PW-2, PW-2)))
        pygame.draw.rect(surf, (0, 0, 0), Rect(((i*(PW*4))+PW, 0), (PW, PW)))
        pygame.draw.rect(surf, getcol(7, i), Rect(((i*(PW*4))+PW+1, 1), (PW-2, PW-2)))
        pygame.draw.rect(surf, (0, 0, 0), Rect(((i*(PW*4))+(PW*2), 0), (PW, PW)))
        pygame.draw.rect(surf, getcol(7, i), Rect(((i*(PW*4))+(PW*2)+1, 1), (PW-2, PW-2)))
        pygame.draw.rect(surf, (0, 0, 0), Rect(((i*(PW*4))+PW, PW), (PW, PW)))
        pygame.draw.rect(surf, getcol(3, int(b)), Rect(((i*(PW*4))+PW+1, PW+1), (PW-2, PW-2)))
    return surf

def next_layer(grid, rule):
    rule = tobase(3, rule)
    last = grid[-1]
    grid.append([])
    for i in range(len(last)):
        grid[-1].append(int(rule[avg(last[max(0, i-1):i+2])]))

def drawn(rule):
    grid = [[0,]*(W//2) + [1] + [0,]*(W//2)]
    for i in range(H): next_layer(grid, rule)
    surf = pygame.Surface(((W+1)*PW, H*PW))
    for y, line in enumerate(grid):
        for x, slot in enumerate(line):
            pygame.draw.rect(surf, (0, 0, 0), Rect((x*PW, y*PW), (PW, PW)))
            pygame.draw.rect(surf, getcol(3, int(slot)), Rect((x*PW+1, y*PW+1), (PW-2, PW-2)))
    return surf

pygame.init()
SCREEN = pygame.display.set_mode(((W + 1) * PW, PW * H))
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
    SCREEN.blit(HEL.render(str(num) + " : " + tobase(3, num), 0, (0, 0, 0)), (0, PW*2))
    SCREEN.blit(drawn(num), (0, PW*(4+origH-scroll)))
    pygame.display.update()
    
