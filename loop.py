import pygame
from pygame.locals import *
from pygame.rect import Rect
from pygame import Surface

from random import randint
from copy import deepcopy

import sys
import os

PW = 2 if "-pw" not in sys.argv else int(sys.argv[sys.argv.index("-pw") + 1])
W = 640 if "-w" not in sys.argv else int(sys.argv[sys.argv.index("-w") + 1])
H = 480 if "-h" not in sys.argv else int(sys.argv[sys.argv.index("-h") + 1])
col = [(255, 255, 255), (0, 0, 0)]
tobin8 = lambda n: (bin(n))[2:10][::-1] + '00000000'
tobin3 = lambda n: (bin(n))[2:5][::-1] + '000'
starting_seed = "random"

STARTING_SEEDS = {
    "right":['0',]*(W) + ['1'],
    "left":['1',] + ['0',]*(W),
    "center": ['0',]*(W//2) + ['1',] + ['0',]*(W//2),
    "random": [str(randint(0, 1)) for _ in range(W+1)],
}

pygame.init()
SCREEN = pygame.display.set_mode(((W+1) * PW, PW * H))
pygame.display.set_caption("Rule 110 loop")

live = __name__ == "__main__"
rule = 110 if "-r" not in sys.argv else int(sys.argv[sys.argv.index("-r") + 1])

PAUSE = False
LENGTH = 1

surf = Surface(SCREEN.get_size())
surf.fill((255, 255, 255))

tape = deepcopy(STARTING_SEEDS[starting_seed])

clock = pygame.time.Clock()

def reset():
    global tape, surf
    pygame.display.set_caption("Rule {} loop".format(rule))
    tape = deepcopy(STARTING_SEEDS[starting_seed])
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

def snapshot(rule, length):
    try:
        surf = Surface((SCREEN.get_width(), length * PW))
    except pygame.error:
        print("Too Large")
        return False
    
    tape = deepcopy(STARTING_SEEDS[starting_seed])
    for i in range(length):
        draw_next(tape, surf)
        tape = next_layer(tape, rule)

    return surf

while live:
    for e in pygame.event.get():
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE): live = False

        if e.type == KEYDOWN:
            if e.key == K_LEFT:
                rule -= 1
                reset()
            if e.key == K_RIGHT:
                rule += 1
                reset()
            if e.key == K_d:
                starting_seed = "random"
                reset()
            if e.key == K_l:
                starting_seed = "left"
                reset()
            if e.key == K_c:
                starting_seed = "center"
                reset()
            if e.key == K_r:
                starting_seed = "right"
                reset()

            if e.key == K_SPACE:
                PAUSE = not PAUSE

            if e.key == K_RETURN:
                pic = snapshot(rule, LENGTH)
                if pic:
                    if not os.path.isdir("pics/"): os.mkdir("pics/")
                    s = "pics/linear.{}.{}.png".format(str(rule), starting_seed)
                    print(s)
                    pygame.image.save(pic, s)

    if not PAUSE:
        tape = next_layer(tape, rule)
        draw_next(tape, surf)
        LENGTH += 1
    
    SCREEN.blit(surf, (0, 0))
    pygame.display.update()
#    clock.tick(40)

