import pygame
from pygame.locals import *
from pygame import Surface, Rect

from pathlib import Path
import os

tokenpath = Path(os.path.dirname(os.path.abspath(__file__))) / "bin"
keyboardpath = tokenpath / "keyboard"

TOKENS = {}
KEYBOARD = {}
KEYBOARD_MAP = {
    K_a: "a", K_b: "b", K_c: "c", K_d: "d", K_e: "e",
    K_f: "f", K_g: "g", K_h: "h", K_i: "i", K_j: "j",
    K_k: "k", K_l: "l", K_m: "m", K_n: "n", K_o: "o",
    K_p: "p", K_q: "q", K_r: "r", K_s: "s", K_t: "t",
    K_u: "u", K_v: "v", K_w: "w", K_x: "x", K_y: "y",
    K_z: "z", 
    K_0: "0", K_1: "1", K_2: "2", K_3: "3", K_4: "4",
    K_5: "5", K_6: "6", K_7: "7", K_8: "8", K_9: "9",
    K_PLUS: "plus", K_MINUS: "minus", K_COLON: "colon",
    K_SPACE: "base", K_AT: "at", K_EXCLAIM: "exclamation",
    K_AMPERSAND: "ampersand", K_QUOTE: "singlequote",
    K_QUOTEDBL: "doublequote", K_HASH: "hash", K_DOLLAR: "dollar",
    K_LEFTPAREN: "openparenth", K_RIGHTPAREN: "closeparanth",
    K_ASTERISK: "star", K_COMMA: "comma", K_PERIOD: "period",
    K_SLASH: "slash", K_SEMICOLON: "semicolon", K_LESS: "lessthan",
    K_GREATER: "greaterthan",  K_EQUALS: "equals", K_QUESTION: "question",
    K_LEFTBRACKET: "openbracket", K_RIGHTBRACKET: "closebracket",
    K_BACKSLASH: "backslash",
}

for token in os.listdir(tokenpath):
    try:
        with open(tokenpath/token, "r") as f:
            TOKENS[token] = eval(f.read())
    except:
        continue

for token in os.listdir(keyboardpath):
    try:
        with open(keyboardpath/token, "r") as f:
            TOKENS[token] = eval(f.read())
    except:
        continue

def draw_token(dest, name, pos, colorkey=(1, 255, 1), col1=(0, 0, 0), col2=(255, 255, 255), PW=1):
    tokenpool = TOKENS
    if name in KEYBOARD:
        tokenpool = KEYBOARD
    for i, t in enumerate(tokenpool[name]):
        x, y = i % 16, i // 16
        if t != 0:
            pygame.draw.rect(dest,
                             [colorkey, col1, col2][t],
                             Rect((pos[0] + x*PW, pos[1] + y*PW),
                                  (PW, PW)))


if __name__ == """__main__""":
    pygame.init()
    PW = 2
    SCREEN = pygame.display.set_mode((PW*16*16, PW*16*16))
    pygame.display.set_caption("text demo")
    
    COLORS = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), (255, 255, 0), (0, 255, 255)]
    c1, c2 = 0, 1
    
    text = []
    
    while True:
        SCREEN.fill((0, 0, 0))
        for i, c in enumerate(text):
            pos = ((i % 16)*PW*16, (i // 16)*PW*16)
            draw_token(SCREEN, c, pos, col1=COLORS[c1], col2=COLORS[c2], PW=PW)

        print(text)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE: quit()
                if e.key == K_BACKSPACE: text = text[:-1]

                if e.key in KEYBOARD_MAP:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        text.append(KEYBOARD_MAP[e.key].upper())
                    else:
                        text.append(KEYBOARD_MAP[e.key])

                if e.key == K_LEFT: c1 = (c1 - 1) % len(COLORS)
                if e.key == K_RIGHT: c1 = (c1 + 1) % len(COLORS)
                if e.key == K_UP: c2 = (c2 - 1) % len(COLORS)
                if e.key == K_DOWN: c2 = (c2 + 1) % len(COLORS)
