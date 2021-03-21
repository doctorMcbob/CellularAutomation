import pygame
pygame.init()

screen = pygame.display.set_mode((66 * 32, 66 * 32))

filenames = [str(i) + ".png" for i in range(1024)]
pics = [pygame.image.load(f).convert() for f in filenames]

img = pygame.Surface(((63 * 2) * 32, (63 * 2) * 32))

for i, pic in enumerate(pics):
    img.blit(pic, ((i % 32) * (63*2), (i // 32) * (63*2)))

screen.blit(img, (0, 0))
pygame.display.update()
pygame.image.save(img, "sick.png")
