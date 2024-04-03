import pygame


class BackgroundParallax(pygame.sprite.Sprite):
    def __init__(self, game, image, range_level, scale=True, pos=(0, 0)):
        super().__init__(game.BACKGROUND)
        self.scale = scale
        self.main_game = game
        if scale:
            self.image = pygame.transform.scale(image, game.SIZE)
        else:
            self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = range_level * 20 / game.FPS
        self.x = 0
        self.range_level = range_level
        if pos == (0, 0) and self.range_level in {1, 2}:
            self.clone(1)

    def update(self, target=None):
        self.x += self.speed
        if self.range_level in {1, 2}:
            self.rect.x -= int(self.x // 1)
            self.x %= 1
        if self.rect.x == -self.rect.width:
            self.clone(2)
            self.kill()


    def clone(self, code=0):
        BackgroundParallax(self.main_game, self.image, range_level=self.range_level, scale=self.scale,
                           pos=(self.rect.x + self.rect.width * code, self.rect.y))

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
