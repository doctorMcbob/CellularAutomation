import pygame
from pygame.locals import *
from pygame.rect import Rect
from pygame import Surface

from random import randint
from copy import deepcopy

import sys
import os

PW = 4 if "-pw" not in sys.argv else int(sys.argv[sys.argv.index("-pw") + 1])
W = 400 if "-w" not in sys.argv else int(sys.argv[sys.argv.index("-w") + 1])
H = 240 if "-h" not in sys.argv else int(sys.argv[sys.argv.index("-h") + 1])

col = [(255, 255, 255), (0, 0, 0)]
tobin8 = lambda n: (bin(n))[2:10][::-1] + '00000000'
tobin3 = lambda n: (bin(n))[2:5][::-1] + '000'
starting_seed = "random"

STARTING_SEEDS = {
    "right":['0',]*(W) + ['1'],
    "left":['1',] + ['0',]*(W),
    "center": ['0',]*(W//2) + ['1',] + ['0',]*(W//2),
    "random": [str(randint(0, 2)) for _ in range(W+1)],
}

pygame.init()
SCREEN = pygame.display.set_mode(((W+1) * PW, PW * H))
pygame.display.set_caption("Rule 110 loop")

live = True
rule = 0 if "-r" not in sys.argv else int(sys.argv[sys.argv.index("-r") + 1])
PAUSE = False
LENGTH = 1

surf = Surface(SCREEN.get_size())
surf.fill((255, 255, 255))

tape = deepcopy(STARTING_SEEDS[starting_seed])

clock = pygame.time.Clock()

def reset():
    global tape, surf, LENGTH
    pygame.display.set_caption("Rule {} loop".format(rule))
    tape = deepcopy(STARTING_SEEDS[starting_seed])
    surf = Surface(SCREEN.get_size())
    surf.fill((255, 255, 255))
    LENGTH = 0

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

def next_layer(last, rule):
    rule = tobase(3, rule)
    new = []
    for i in range(len(last)):
        nums = [int(last[(i-1)%len(last)]), int(last[i]), int(last[(i+1)%len(last)])]
        new.append(int(rule[avg(nums)]))
    return new
        
def draw_next(tape, surf):
    surf.blit(surf, (0, 0-PW))
    for i, slot in enumerate(tape):
        pygame.draw.rect(surf, getcol(3, int(slot)), Rect((i*PW, surf.get_height() - PW), (PW, PW)))
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
                    s = "pics/totalistic.{}.{}.png".format(str(rule), starting_seed)
                    print(s)
                    pygame.image.save(pic, s)

    if not PAUSE:
        draw_next(tape, surf)
        tape = next_layer(tape, rule)
        LENGTH += 1
    
    SCREEN.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(40)

