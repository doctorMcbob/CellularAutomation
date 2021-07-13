"""
lifelike.py

I'm imagening a tool for playing with lifelike cellular automata!
lifelike being defined a such:

 . cells either alive or dead, with 8 neighbors
 . upper bound, cells with more then N living neighbors die out
 . lower bound, cells with less then N living neighbors die out
 . life number, cells with certain numbers of living cells come to life

example: Game of life
 lower bound: 2, 
 upper bound: 3,
 life number: 3

example: other
 lower bound: 2
 upper bound: 5
 life number: 3, 4

Multiple life numbers are allowed, upper bound must be more then lower bound

storing rules...
 00000000:00000000
 bounds       life

game of life:
 01100000:00100000
  ^^        ^
lower/upper |
(2, 3)      life number (3)
"""
#pygame for front
import pygame
from pygame import Surface, Rect
from pygame.locals import *

from random import randint

# board definitions
W, H = 32, 32
PW = 25

# ~~~ RULE ~~~
LOWER_BOUND = 2
UPPER_BOUND = 3
LIFE_NUMBERS = [3]

# state
CELLS = set()
FRAMES = []
PLAY = False
MILI_WAIT = 300

# draw definitions
DRAW_DATA = {
    "screen": None,
    "size"  : (PW*(W+2), PW*(H+5)),
    "board" : (PW*1, PW*4),
    "rule"  : (PW*1, 0),
    "HUD"   : (PW*1, PW*1),
    "font"  : None,
    "colors": {
        "back"  : (255, 255, 255),
        "dead"  : (255, 255, 255),
        "alive" : (0, 0, 0),
        "text"  : (0, 0, 0),
        "grid"  : (50, 50, 50),
    },
}

# rule functions
def nbrs(cell):
    x, y = cell
    for y_ in [y-1, y, y+1]:
        for x_ in [x-1, x, x+1]:
            if (x_, y_) == (x, y): continue
            yield (x_, y_)


def num_nbrs(cell):
    return sum(map(lambda c: c in CELLS, nbrs(cell)))


def apply_rule(cells):
    new = set()
    for y in range(H):
        for x in range(W):
            n = num_nbrs((x, y))
            if ((x, y) in cells
                and ( LOWER_BOUND <= n <= UPPER_BOUND )
                or n in LIFE_NUMBERS):
                new.add((x, y))
    return new


# draw functions
def init():
    pygame.init()
    DRAW_DATA["screen"] = pygame.display.set_mode(DRAW_DATA["size"])
    DRAW_DATA["font"] = pygame.font.SysFont("Helvetica", PW)
    

def drawn_board(cells):
    surf = Surface((H*PW, H*PW))
    surf.fill(DRAW_DATA["colors"]["grid"])
    for y in range(H):
        for x in range(W):
            col = DRAW_DATA["colors"]["alive"] if (x, y) in cells else DRAW_DATA["colors"]["dead"]
            pygame.draw.rect(surf, col,
                             Rect(((x*PW) + 1, (y*PW) + 1), (PW-2, PW-2)))
    pygame.draw.rect(surf, (255, 0, 0), Rect(((PW*W//2)-1, (PW*H//2)-1), (2, 2)))
    return surf


def drawn_rule():
    binary_rule = "".join(map(lambda n: str(int(n in [LOWER_BOUND, UPPER_BOUND])), range(1, 9)))
    binary_rule += ":"
    binary_rule += "".join(map(lambda n: str(int(n in LIFE_NUMBERS)), range(1, 9)))
    dec_rule = str(int(binary_rule[:8], 2)) + ":" + str(int(binary_rule[9:], 2))
    
    return DRAW_DATA["font"].render(binary_rule + "  " + dec_rule, 0, DRAW_DATA["colors"]["text"])


def drawn_HUD():
    surf = Surface((PW*(W-2), PW*2))
    surf.fill(DRAW_DATA["colors"]["back"])
    # bounds
    for n in range(1, 9):
        if n in [LOWER_BOUND, UPPER_BOUND]:
            pygame.draw.rect(surf, DRAW_DATA["colors"]["grid"],
                             Rect(((n-1)*PW, 0), (PW, PW)))
        surf.blit(DRAW_DATA["font"].render(
            str(n), 0, DRAW_DATA["colors"]["text"]), ((n-1)*PW, 0))
    surf.blit(DRAW_DATA["font"].render(
        "Lower / Upper bounds", 0, DRAW_DATA["colors"]["text"]), (PW*10, 0))
    
    # life nums
    for n in range(1, 9):
        if n in LIFE_NUMBERS:
            pygame.draw.rect(surf, DRAW_DATA["colors"]["grid"],
                             Rect(((n-1)*PW, PW), (PW, PW)))
        surf.blit(DRAW_DATA["font"].render(
            str(n), 0, DRAW_DATA["colors"]["text"]), ((n-1)*PW, PW))
    surf.blit(DRAW_DATA["font"].render(
        "Life numbers", 0, DRAW_DATA["colors"]["text"]), (PW*10, PW))
    
    return surf


def draw():
    if DRAW_DATA["screen"] is None: return
    DRAW_DATA["screen"].fill(DRAW_DATA["colors"]["back"])
    DRAW_DATA["screen"].blit(drawn_board(CELLS), DRAW_DATA["board"])
    DRAW_DATA["screen"].blit(drawn_HUD(), DRAW_DATA["HUD"])
    DRAW_DATA["screen"].blit(drawn_rule(), DRAW_DATA["rule"])
    pygame.display.update()


# click functions
def relative_click(click_pos, name):
    x, y = click_pos
    x_off, y_off = DRAW_DATA[name]
    return x-x_off, y-y_off

def board_click(click_pos):
    x, y = relative_click(click_pos, "board")
    pos = (x // PW, y // PW)
    if pos in CELLS: CELLS.remove(pos)
    else: CELLS.add(pos)


def HUD_click(click_pos):
    global LOWER_BOUND, UPPER_BOUND
    x, y = relative_click(click_pos, "HUD")
    if x > PW*8: return False
    n = (x // PW) + 1
    # bounds
    if y < PW:
        low, high = False, False
        if not n > UPPER_BOUND: low = True
        if not n < LOWER_BOUND: high = True
        if low: LOWER_BOUND = n
        if high: UPPER_BOUND = n
    # life
    elif y >= PW:
        if n in LIFE_NUMBERS:
            LIFE_NUMBERS.remove(n)
        else:
            LIFE_NUMBERS.append(n)
    return True


# other
def randomize():
    new = set()
    for y in range(H):
        for x in range(W):
            if randint(0, 1):
                new.add((x, y))
    return new
            
if __name__ == """__main__""":
    init()

    live = True
    clock = pygame.time.Clock()
    mili = 0
    while live:
        mili += clock.tick()
        draw()

        if PLAY == True and mili > MILI_WAIT and CELLS:
            mili = 0
            FRAMES.append(CELLS)
            CELLS = apply_rule(CELLS)
        
        for e in pygame.event.get():
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
                live = False

            if e.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                bx, by = DRAW_DATA["board"]
                if bx <= x <= bx+PW*W and by <= y <= by+PW*H:
                    board_click((x, y))
                    PLAY = False
                    FRAMES = []

                hx, hy = DRAW_DATA["HUD"]
                if hx <= x <= hx+PW*(W-2) and hy <= y <= hy+PW*2:
                    if HUD_click((x, y)):
                        FRAMES = []

            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    PLAY = not PLAY
                    mili = 0

                if e.key in [K_LEFT, K_RIGHT, K_c, K_r]:
                    PLAY = False

                if e.key == K_LEFT and FRAMES:
                    CELLS = FRAMES.pop()

                if e.key == K_RIGHT and CELLS:
                    FRAMES.append(CELLS)
                    CELLS = apply_rule(CELLS)
                    

                if e.key == K_c:
                    FRAMES = []
                    CELLS = set()

                if e.key == K_r:
                    FRAMES = []
                    CELLS = randomize()
