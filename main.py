import pygame
from fighter import Fighter
from characters_py.ken import KEN
from characters_py.kyo import KYO

pygame.init()

SCREEN_WIDTH  = 1200
SCREEN_HEIGHT = 600

YELLOW = (255, 255, 0)
RED    = (255, 0,   0)
WHITE  = (255, 255, 255)
SUPER_BAR_BLUE       = (0,   125, 255)
SUPER_BAR_BLUE_FLASH = (0,   255, 255)
BLACK  = (0,   0,   0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SvK")

clock = pygame.time.Clock()
FPS   = 60

bg_image   = pygame.image.load("assets/img/bg/River.gif").convert_alpha()
combo_font = pygame.font.SysFont("impact", 60)
hit_font   = pygame.font.SysFont("impact", 30)
win_font   = pygame.font.SysFont("impact", 80)


def draw_text(text, font, text_col, x, y):
    img    = font.render(text, True, text_col)
    shadow = font.render(text, True, BLACK)
    screen.blit(shadow, (x + 2, y + 2))
    screen.blit(img,    (x, y))


def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))


def draw_health_bar(health, max_health, x, y):
    ratio = max(0, health / max_health)
    pygame.draw.rect(screen, BLACK,  (x - 2, y - 2, 505, 35))
    pygame.draw.rect(screen, RED,    (x, y, 500, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, int(500 * ratio), 30))


def draw_super_meter(meter, x, y, is_full):
    ratio = meter / 100
    flash = is_full and (pygame.time.get_ticks() // 150) % 2 == 0
    color = SUPER_BAR_BLUE_FLASH if flash else SUPER_BAR_BLUE
    pygame.draw.rect(screen, BLACK, (x - 2, y - 2, 205, 25))
    pygame.draw.rect(screen, WHITE, (x, y, 200, 20))
    pygame.draw.rect(screen, color, (x, y, int(200 * ratio), 20))


def reset_fighters():
    f1 = Fighter(1, KYO, 200, 310)
    f2 = Fighter(2, KEN, 900, 310)
    return f1, f2


fighter_1, fighter_2 = reset_fighters()

winner_text        = ""   
winner_screen_end  = 0   

run = True
while run:
    clock.tick(FPS)
    now = pygame.time.get_ticks()

    draw_bg()

    # ── Win screen ────────────────────────────────────────────────────────────
    if winner_text:
        draw_health_bar(fighter_1.health, fighter_1.max_health, 20,  20)
        draw_health_bar(fighter_2.health, fighter_2.max_health, 680, 20)
        draw_super_meter(fighter_1.super_meter, 20,  55, False)
        draw_super_meter(fighter_2.super_meter, 980, 55, False)
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        text_surf   = win_font.render(winner_text, True, YELLOW)
        shadow_surf = win_font.render(winner_text, True, BLACK)
        tx = SCREEN_WIDTH  // 2 - text_surf.get_width()  // 2
        ty = SCREEN_HEIGHT // 2 - text_surf.get_height() // 2
        screen.blit(shadow_surf, (tx + 3, ty + 3))
        screen.blit(text_surf,   (tx, ty))

        if now >= winner_screen_end:
            fighter_1, fighter_2 = reset_fighters()
            winner_text = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()
        continue 

    # ── Normal game loop ──────────────────────────────────────────────────────
    if fighter_1.super_flash_timer > 0 or fighter_2.super_flash_timer > 0:
        dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dark.set_alpha(160)
        dark.fill((0, 0, 0))
        screen.blit(dark, (0, 0))

    draw_health_bar(fighter_1.health, fighter_1.max_health, 20,  20)
    draw_health_bar(fighter_2.health, fighter_2.max_health, 680, 20)
    draw_super_meter(fighter_1.super_meter, 20,  55, fighter_1.super_meter >= 100)
    draw_super_meter(fighter_2.super_meter, 980, 55, fighter_2.super_meter >= 100)

    if fighter_1.combo > 1:
        draw_text(str(fighter_1.combo), combo_font, RED,   20,   90)
        draw_text("HITS",               hit_font,   WHITE, 60,   115)
    if fighter_2.combo > 1:
        draw_text(str(fighter_2.combo), combo_font, RED,   1140, 90)
        draw_text("HITS",               hit_font,   WHITE, 1080, 115)

    super_flash_active = (
        fighter_1.super_flash_timer > 0 or
        fighter_2.super_flash_timer > 0
    )

    if not super_flash_active:
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2)
        fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1)

    if super_flash_active:
        if fighter_1.super_flash_timer > 0:
            fighter_1.update(screen, fighter_2)
        if fighter_2.super_flash_timer > 0:
            fighter_2.update(screen, fighter_1)
    else:
        fighter_1.update(screen, fighter_2)
        fighter_2.update(screen, fighter_1)

    fighter_1.draw(screen)
    fighter_2.draw(screen)

    # ── Check for KO ─────────────────────────────────────────────────────────
    if fighter_1.health <= 0 or fighter_2.health <= 0:
        if fighter_1.health <= 0 and fighter_2.health <= 0:
            winner_text = "DRAW!"
        elif fighter_2.health <= 0:
            winner_text = "PLAYER 1 WINS!"
        else:
            winner_text = "PLAYER 2 WINS!"
        winner_screen_end = now + 2000 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()