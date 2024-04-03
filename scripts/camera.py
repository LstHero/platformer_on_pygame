class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, size, level_rect):
        self.dx = 0
        self.dy = 0
        self.width, self.height = size
        self.offset = 20
        self.start_level = True
        self.level_rect = level_rect.copy()
        self.limit_width = range(self.level_rect.x + (self.width // 2 + self.offset),
                                 self.level_rect.width - (self.width // 2 + self.offset))
        self.limit_height = range(self.level_rect.y + (self.height // 2 + self.offset),
                                  self.level_rect.height - (self.height // 2 + self.offset))
        self.pos_camera = (self.offset + self.width // 2, self.offset + self.height // 2)
        self.pos_in_map = (self.limit_width[0], self.limit_height[0])

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def get_dx(self, target_x, x):
        dx = -(target_x - x)
        return dx

    def get_near(self, target_x, x, x_pos_in_map, limit):
        dx = self.get_dx(target_x, x)
        if x_pos_in_map - dx in limit:
            pass
        elif self.get_dx(target_x, limit[0]) < self.get_dx(target_x, limit[-1]):
            dx = self.get_dx(x, limit[0])
        else:
            dx = self.get_dx(x, limit[-1])
        return dx

    def update(self, target):
        self.dx = self.get_near(target.rect.x + target.rect.w // 2, self.pos_camera[0], self.pos_in_map[0],
                                self.limit_width)
        self.dy = self.get_near(target.rect.y + target.rect.h // 2, self.pos_camera[1], self.pos_in_map[1],
                                self.limit_height)

    def apply_self(self):
        self.pos_in_map = (self.pos_in_map[0] - self.dx, self.pos_in_map[1] - self.dy)
