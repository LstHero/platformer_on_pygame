import pygame
import sys


def terminate():
    pygame.quit()
    sys.exit()


def get_text_render(text, color, size_font):
    font = pygame.font.Font('.\data\\font\ComicoroRu_0.ttf', size_font)
    return font.render(text, 0, color)


def start_scene(game):
    screen = game.main_screen
    clock = game.clock
    screen.fill('black')
    # загружаем шрифт с разным размером
    logo = pygame.font.Font('.\data\\font\ComicoroRu_0.ttf', 100)
    press_enter = pygame.font.Font('.\data\\font\ComicoroRu_0.ttf', 60)
    # надписи рендерим
    logo_render = logo.render("Руины Бога Битвы", 0, pygame.Color('black'))
    press_enter_render = press_enter.render("Нажмите ENTER", 0, pygame.Color('black'))
    # формируем координаты текста
    logo_pos = (game.WIDTH // 2 - logo_render.get_rect().width // 2, game.HEIGHT // 5)
    press_enter_pos = (game.WIDTH // 2 - press_enter_render.get_rect().width // 2, game.HEIGHT // 7 * 6)
    alpha_change = 0
    change_direction = -1
    press_enter_render.set_alpha(254)
    while True:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                # клавиша ENTER
            elif event.type == pygame.KEYDOWN and (event.key == 13 or event.key == pygame.K_ESCAPE):
                return
        # Анимация мигания нижней кнопки PRESS ENTER
        alpha_now = press_enter_render.get_alpha()
        if alpha_now < 10 and alpha_change < 0:
            change_direction = 1
            alpha_change = 0
        elif alpha_now > 250 and alpha_change > 0:
            change_direction = -1
            alpha_change = 0
        press_enter_render.set_alpha(int(alpha_now + alpha_change))
        alpha_change += change_direction * 4 / game.FPS
        # обновляем фон и текст + рисуем
        game.BACKGROUND.update()
        game.BACKGROUND.draw(screen)
        screen.blit(logo_render, logo_pos)
        screen.blit(press_enter_render, press_enter_pos)
        pygame.display.flip()
        clock.tick(game.FPS)


def leaderboard_scene(game):
    screen = game.main_screen
    clock = game.clock
    screen.fill('black')
    leaders = game.get_leaderboard(new_get=True)
    lines = [get_text_render(line, 'black', 80) for line in leaders]
    while True:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                # клавиша ENTER
            elif event.type == pygame.KEYDOWN and event.key == 13:
                return  # начинаем игру
        # обновляем фон и текст + рисуем
        game.BACKGROUND.update()
        game.BACKGROUND.draw(screen)
        for i, line in enumerate(lines):
            screen.blit(line, (game.WIDTH // 2 - line.get_width() // 2, 50 * i + 50))
        pygame.display.flip()
        clock.tick(game.FPS)
