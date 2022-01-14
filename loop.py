import pygame
from pygame.locals import *
from pygame.rect import Rect
from pygame import Surface

from random import randint
from copy import deepcopy

PW = 1
W, H = 1280, 640
col = [(255, 255, 255), (0, 0, 0)]
tobin8 = lambda n: (bin(n))[2:10][::-1] + '00000000'
tobin3 = lambda n: (bin(n))[2:5][::-1] + '000'

STARTING_SEED = ['0',]*(W) + ['1']
RANDOM_STARTING_SEED = ['0' if randint(0, 12) else '1' for _ in range(W+1)]

pygame.init()
SCREEN = pygame.display.set_mode(((W+1) * PW, PW * H))
pygame.display.set_caption("Rule 110 loop")

live = True
num = 110
RANDOM = True

surf = Surface(SCREEN.get_size())
surf.fill((255, 255, 255))

tape = deepcopy(STARTING_SEED) if RANDOM == False else deepcopy(RANDOM_STARTING_SEED)

clock = pygame.time.Clock()

def reset():
    global tape, surf
    tape = deepcopy(STARTING_SEED) if RANDOM == False else deepcopy(RANDOM_STARTING_SEED)
    surf = Surface(SCREEN.get_size())
    surf.fill((255, 255, 255))

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

def next_layer(last, rule):
    rule = tobin8(rule)
    new = []
    for i in range(len(last)):
        ref = "".join([last[(i-1)%len(last)], last[i], last[(i+1)%len(last)]])
        new.append(str(rule[int("0b"+ref, 2)]))
    return new
        
def draw_next(tape, surf):
    surf.blit(surf, (0, 0-PW))
    for i, slot in enumerate(tape):
        pygame.draw.rect(surf, col[int(slot)], Rect((i*PW, surf.get_height() - PW), (PW, PW)))
    return surf

while live:
    for e in pygame.event.get():
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE): live = False

        if e.type == KEYDOWN:
            if e.key == K_LEFT:
                num -= 1
                reset()
            if e.key == K_RIGHT:
                num += 1
                reset()

    tape = next_layer(tape, num)
    draw_next(tape, surf)
    
    SCREEN.blit(surf, (0, 0))
    pygame.display.update()
#    clock.tick(30)

pygame.quit()

