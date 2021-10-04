import pygame
from pygame import Surface, Rect
from pygame.locals import *

from pathlib import Path
import os
import sys

pygame.init()

PW = 32
W, H = 16, 16

path = Path(".") / "bin"
name = sys.argv[-1]

token = None
def load(name):
    global token
    try:
        with open(path/name, "r") as f:
            token = eval(f.read())
    except IOError:
        pass

def save(name):
    if not name: return
    with open(path/name, "w") as f:
        f.write(repr(token))


if name in os.listdir(path):
    load(name)

if not token:
    token = [0 for _ in range(W*H)]

SCREEN = pygame.display.set_mode((W*PW, (H+4)*PW))
pygame.display.set_caption("Token Drawer")

HEL16 = pygame.font.SysFont("Helvetica", 16)

surf = Surface((W*PW, H*PW))
cursor = [0, 0]

def expect_key(expected=[]):
    while True:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN:
                if expected:
                    if e.key in expected:
                        return e.key
                else:
                    return e.key

ALPHABET_KEY_MAP = {
    K_a: "a", K_b: "b", K_c: "c", K_d: "d", K_e: "e",
    K_f: "f", K_g: "g", K_h: "h", K_i: "i", K_j: "j",
    K_k: "k", K_l: "l", K_m: "m", K_n: "n", K_o: "o",
    K_p: "p", K_q: "q", K_r: "r", K_s: "s", K_t: "t",
    K_u: "u", K_v: "v", K_w: "w", K_x: "x", K_y: "y",
    K_z: "z", K_SPACE: " ", K_UNDERSCORE: "_",
    K_0: "0", K_1: "1", K_2: "2", K_3: "3", K_4: "4",
    K_5: "5", K_6: "6", K_7: "7", K_8: "8", K_9: "9",
    K_PLUS: "+", K_MINUS: "-", K_COLON: ":",
}

def get_text_input(pos):
    string = ''
    while True:
        surf = Surface((128, 16))
        surf.fill((230, 230, 230))
        surf.blit(HEL16.render(string, 0, (0, 0, 0)), (0, 0))
        SCREEN.blit(surf, pos)
        pygame.display.update()

        inp = expect_key()
        if inp == K_ESCAPE: return False
        if inp == K_BACKSPACE: string = string[:-1]
        if inp == K_RETURN: return string
        
        if pygame.key.get_mods() & KMOD_SHIFT:
            if inp in ALPHABET_KEY_MAP:
                string = string + ALPHABET_KEY_MAP[inp].upper()
        elif inp in ALPHABET_KEY_MAP:
            string = string + ALPHABET_KEY_MAP[inp]


def draw_cursor():
    pygame.draw.line(SCREEN, (255, 0, 0),
                     (PW*cursor[0], PW*cursor[1]),
                     (PW*cursor[0]+PW, PW*cursor[1]+PW))

def draw_token():
    for i, t in enumerate(token):
        x = i % W
        y = i // W
        pygame.draw.rect(surf,
                         [(1, 255, 1), (0, 0, 0), (255, 255, 255)][t],
                         Rect((x*PW, y*PW), (PW, PW)))


while __name__ == """__main__""":
    SCREEN.fill((200, 200, 200))
    draw_token()
    SCREEN.blit(surf, (0, 0))
    draw_cursor()
    inp = expect_key()

    if inp == K_UP: cursor[1] = (cursor[1] - 1) % H
    if inp == K_DOWN: cursor[1] = (cursor[1] + 1) % H
    if inp == K_LEFT: cursor[0] = (cursor[0] - 1) % W
    if inp == K_RIGHT: cursor[0] = (cursor[0] + 1) % W

    if inp == K_SPACE:
        token[(cursor[1]*W)+cursor[0]] = (token[(cursor[1]*W)+cursor[0]]+1) % 3

    if inp == K_RETURN:
        SCREEN.blit(HEL16.render("SAVE: ", 0, (0, 0, 0)), (0, PW*H))
        save(get_text_input((0, PW*(H+1))))

    if inp == K_BACKSPACE:
        SCREEN.blit(HEL16.render("LOAD: ", 0, (0, 0, 0)), (0, PW*H))
        load(get_text_input((0, PW*(H+1))))

    
