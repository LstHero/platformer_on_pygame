import pygame


class TimeUI(pygame.sprite.Sprite):
    BLOCK = False

    def __init__(self, pos, all_sprites, start_time):
        super().__init__(all_sprites)
        self.font = pygame.font.Font('.\data\\font\ComicoroRu_0.ttf', 60)
        self.pos = pos
        self.start_time = start_time
        self.update()

    def update(self):
        if self.BLOCK:
            return
        self.time = round((pygame.time.get_ticks() - self.start_time) / 1000, 1)
        self.image = self.font.render(f"{self.time} сек", 0,
                                      pygame.Color('black'))
        self.rect = self.image.get_rect()
        self.rect.topright = self.pos

    def get_time(self):
        return self.time

    def stop(self):
        self.BLOCK = True



# class DeathCongrats(pygame.sprite.Sprite):
#     def __init__(self, pos):
#         super().__init__(ALL_TILES_GROUP)
#         self.font = pygame.font.Font('.\data\\font\ComicoroRu_0.ttf', 60)
#         self.pos = pos
#         self.update()