import pygame
from scripts.background_parallax import BackgroundParallax
from scripts.load_images import load_image
from scripts.scenes import start_scene, leaderboard_scene
from scripts.levels import level_1
import csv


def load_all_image(images):
    images['icon'] = load_image('icon\main_icon.png')
    images['background'] = {'1_CloudsBack': load_image('background\CloudsBack.png'),
                            '2_CloudsFront': load_image('background\CloudsFront.png'),
                            '4_BGFront': load_image('background\BGFront.png'),
                            '3_BGBack': load_image('background\BGBack.png')}
    images['enemies'] = ''
    return images


class Game:
    SIZE = (1280, 720)
    WIDTH, HEIGHT = SIZE
    FPS = 60
    IMAGES = dict()
    SCALE = 3
    ALL_SPRITES = pygame.sprite.Group()
    BACKGROUND = pygame.sprite.Group()

    def __init__(self):
        pygame.init()
        self.main_screen = pygame.display.set_mode(self.SIZE)
        load_all_image(self.IMAGES)
        pygame.display.set_caption('Ruins of the God of Battle')
        pygame.display.set_icon(self.IMAGES['icon'])
        self.clock = pygame.time.Clock()
        self.create_background()

    def create_background(self):
        # self.all_bg = dict()
        for i, bg_name in enumerate(sorted(self.IMAGES['background'].keys()), 1):
            BackgroundParallax(game=self, image=self.IMAGES['background'][bg_name], range_level=i)

    def add_to_leaderboard(self, name, time):
        leaderboard = self.get_leaderboard(get_lists=True)
        with open('leaderboard.csv', 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(csvfile, delimiter='&', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(leaderboard[0])
            for el in sorted(leaderboard[1:], key=lambda x: x[0]):
                writer.writerow(el)
            writer.writerow([len(leaderboard) - 1, name, time, True])

    def get_leaderboard(self, get_lists=False, sort=True, new_get=False):
        with open('leaderboard.csv', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter='&', quotechar='"')
            title = next(reader)
            leaders = [title]
            for id, name, time, is_new in reader:
                if new_get and str(is_new) == 'True':
                    leaders.append([int(id), name, float(time), True])
                else:
                    leaders.append([int(id), name, float(time), False])
            if sort:
                leaders = leaders[0:1] + sorted(leaders[1:], key=lambda x: (x[2], x[0]))
        if get_lists:
            return leaders
        return [f'<new> {i}). {x[1]}: {x[2]} сек. <new>' if x[-1] else f'{i}). {x[1]}: {x[2]} сек.' for i, x in enumerate(leaders[1:15])]


if __name__ == '__main__':
    game = Game()
    start_scene(game)
    result = level_1(game)
    while result == 'RESTART':
        result = level_1(game)
    pygame.display.flip()
