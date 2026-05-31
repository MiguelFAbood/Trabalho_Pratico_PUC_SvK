import pygame
from fighter import Fighter

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600

YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREY = (200, 200, 200)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SvK")

clock = pygame.time.Clock()
FPS = 60

bg_image = pygame.image.load("assets/img/bg/River.gif").convert_alpha()

def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

def draw_health_bar(health, x, y):
    ratio = health / 1000
    pygame.draw.rect(screen, BLACK, (x - 2, y - 2, 505, 35))
    pygame.draw.rect(screen, RED, (x, y, 500, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 500 * ratio, 30))

fighter_1 = Fighter(1, "street fighter/ken", 200, 310)
fighter_2 = Fighter(2, "street fighter/ken", 900, 310)

run = True
while run:
    clock.tick(FPS)
    
    draw_bg()
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 680, 20)
    
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2)
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1)

    fighter_1.update(screen, fighter_2)
    fighter_2.update(screen, fighter_1)

    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()
pygame.quit()