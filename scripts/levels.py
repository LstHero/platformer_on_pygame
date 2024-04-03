import pygame
import pytmx
import pygame_gui
from scripts.ui_classes import TimeUI
from scripts.camera import Camera
from scripts.load_images import load_image
from scripts.scenes import terminate, get_text_render, leaderboard_scene

ALL_TILES_GROUP = pygame.sprite.Group()
BACKGROUND_TILE_GROUP = pygame.sprite.Group()
BLOCKS_GROUP = pygame.sprite.Group()
PLATFORM_GROUP = pygame.sprite.Group()
DANGER_BLOCKS_GROUP = pygame.sprite.Group()
PLAYER_GROUP = pygame.sprite.Group()

DEBBUGING_MODE = False
START_LEVEL_TIME = 0
RIGHT = 1
LEFT = 2
JUMP = 3
STAY = 4
RUN = 5
FALL = 6
HIT_PLAYER_EVENT = 7
PLAYER_DEATH = False


class Level:
    layers = {'danger_blocks': DANGER_BLOCKS_GROUP,
              'blocks': BLOCKS_GROUP,
              'bridge': PLATFORM_GROUP,
              'bg_blocks': BACKGROUND_TILE_GROUP}

    def __init__(self, filename, scale=2):
        self.map = pytmx.load_pygame(f'./levels/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.scale = scale
        self.tile_size = self.map.tilewidth * self.scale
        self.get_sprite()

    def get_sprite(self):
        '''
        По факту это бывший метод render, который в примере из курса сам всё обрисовывал.
        Но так как мы всё таки добавляем класс камеры, то всё у нас должно быть в спрайтах.
        Первые 5 слоёв я сделал с фоновыми объектами.
        Следующий - под мосты (будет что-то типа платформой)
        7-й слой просто под обычные блоки, а 8-й под колья (danger_blocks).
        '''
        for layer_id in range(len(self.map.layers)):
            for y in range(self.height):
                for x in range(self.width):
                    layer = self.map.layers[layer_id]
                    image = self.map.get_tile_image(x, y, layer_id)
                    if image is None:
                        continue
                    image = pygame.transform.scale(image, (self.tile_size, self.tile_size)).convert_alpha()
                    if layer.name in self.layers:
                        group = self.layers[layer.name]
                    else:
                        group = self.layers['bg_blocks']
                    Tile(group, image, (x * self.tile_size, y * self.tile_size))


class Tile(pygame.sprite.Sprite):
    def __init__(self, group, image, pos):
        if group == PLATFORM_GROUP:  # не успеваю их немного доделать, заменю на блоки
            group = BLOCKS_GROUP
        super().__init__(group, ALL_TILES_GROUP)
        self.image = image
        self.rect = self.image.get_rect().move(pos)
        if group == DANGER_BLOCKS_GROUP:
            self.rect = self.rect.inflate(-4, -4)
        if group == BLOCKS_GROUP and DEBBUGING_MODE:
            self.image.fill(pygame.Color((0, 220, 0)))  # проверяю хитбокс


class Player(pygame.sprite.Sprite):
    anim_images = {'stay': ('_Idle.png', 10, 1),
                   'run': ('_Run.png', 10, 1),
                   'jump_up': ('_Jump.png', 3, 1),
                   'jump_top': ('_JumpFallInbetween.png', 2, 1),
                   'fall': ('_Fall.png', 3, 1),
                   'death': ('_Death.png', 10, 1),
                   'hit': ('_Hit.png', 1, 1),
                   'turn_around': ('_TurnAround.png', 3, 1)}

    def __init__(self, game, pos, group):
        super().__init__(game.ALL_SPRITES, group)
        self.is_right = True
        self.frames = dict()
        self.scale = game.SCALE
        for key, (image_name, cols, rows) in self.anim_images.items():
            # self.cut_sheet(load_image('player/' + image_name), key, cols, rows)
            self.frames[key] = []
            for i in range(cols):
                frame = load_image(f'player_sec/{key}/{i}' + image_name)
                self.frames[key].append(pygame.transform.scale(frame, (
                    frame.get_width() * self.scale, frame.get_height() * self.scale)))
        self.cur_frame = 0
        self.type_image = 'stay'
        self.image = self.frames[self.type_image][self.cur_frame].convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.midbottom = pos
        self.step = 8
        self.gravity = 1
        self.vertical_velocity = 0
        self.button_flags = {event: False for event in [LEFT, RIGHT, JUMP, FALL]}

    def cut_sheet(self, sheet, key, columns, rows):
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * self.scale, sheet.get_height() * self.scale))
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        self.frames[key] = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames[key].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def hit_animation(self, start=True):
        if start:
            pygame.time.set_timer(HIT_PLAYER_EVENT, 50)
        self.hit_anim_count += 1
        self.image.set_alpha(254 - self.hit_anim_count * 10)
        if self.hit_anim_count * 50 >= 1600:
            pygame.time.set_timer(HIT_PLAYER_EVENT, 0)

    def update(self):
        global PLAYER_DEATH

        self.rect_copy = self.rect.copy()
        self.rect.y += 3
        # если под нами поверхность, то условие будет верным и мы СТОИМ НА ЗЕМЛЕ
        if pygame.sprite.spritecollide(self, BLOCKS_GROUP, False):
            if not self.button_flags[JUMP] or self.vertical_velocity == 1:
                self.button_flags[JUMP] = False
                self.button_flags[FALL] = False
                self.vertical_velocity = 0
                self.type_image = 'stay'
            if self.button_flags[LEFT]:
                self.is_right = False if self.is_right else False
                self.type_image = 'run'
            elif self.button_flags[RIGHT]:
                self.type_image = 'run'
            if DEBBUGING_MODE: print('стоим--------------------------')
        else:
            if DEBBUGING_MODE: print('падаем')
            if not self.button_flags[JUMP] and not self.button_flags[FALL]:
                self.button_flags[FALL] = True
                self.vertical_velocity = 1
        self.rect.y = self.rect_copy.y
        if self.button_flags[JUMP]:
            if DEBBUGING_MODE: print(self.vertical_velocity, self.rect.y, sep='----')
            self.vertical_velocity += self.gravity
            self.rect.y += self.vertical_velocity
            self.type_image = 'jump_up'
            if self.rect.y >= self.rect_copy.y:
                self.type_image = 'fall'
                self.button_flags[JUMP] = False
                self.button_flags[FALL] = True
            #     print('-' * 18)
        if self.button_flags[FALL]:
            self.vertical_velocity += self.gravity
            self.rect.y += self.vertical_velocity

        self.rect.y += 1
        if pygame.sprite.spritecollide(self, BLOCKS_GROUP, False):
            mn_dy = []
            self.vertical_velocity = 0
            for sprite in pygame.sprite.spritecollide(self, BLOCKS_GROUP, False):
                dy = self.rect.bottom - sprite.rect.top
                if dy > 0 and self.rect.top > sprite.rect.top:
                    mn_dy.append(dy)
            self.rect.y -= dy

        if pygame.sprite.spritecollide(self, BLOCKS_GROUP, False) and DEBBUGING_MODE:
            print('ЭТОГО БЫТЬ НЕ ДОЛЖНО')  # после прошлых махинаций по оси y всё должно быть нормально

        if all([self.button_flags[RIGHT], self.button_flags[LEFT]]) or not any(
                [self.button_flags[RIGHT], self.button_flags[LEFT]]):
            self.rect.x += 0
        elif self.button_flags[RIGHT]:
            self.rect.x += self.step
        elif self.button_flags[LEFT]:
            self.rect.x += -self.step
        if pygame.sprite.groupcollide(PLAYER_GROUP, BLOCKS_GROUP, False, False):
            self.rect.x = self.rect_copy.x

        if pygame.sprite.spritecollide(self, DANGER_BLOCKS_GROUP, False):
            for key in self.button_flags:
                self.button_flags[key] = False
            self.type_image = 'death'
            PLAYER_DEATH = True
            return

    def jump(self, status):
        if PLAYER_DEATH:
            return
        if status and (self.button_flags[JUMP] or self.button_flags[FALL]):
            return
        if status:
            self.button_flags[JUMP] = status
            self.type_image = 'jump_up'
            self.vertical_velocity = -20

    def change_image(self):
        # if self.type_image == 'turn_around' and self.cur_frame + 1 == len(self.frames[self.type_image]):
        #     self.type_image = 'run'
        if self.type_image == 'death' and self.cur_frame + 1 == len(self.frames[self.type_image]):
            return
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.type_image])
        self.image = self.frames[self.type_image][self.cur_frame]
        if not self.is_right:
            self.image = pygame.transform.flip(self.image, 1, 0)
        if DEBBUGING_MODE:
            self.image = pygame.Surface(self.rect.size)
            self.image.fill(pygame.Color((220, 0, 0)))
        pos = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

    def move(self, direction_type, status):
        '''
        В этом методе допущен баг, на самом деле. Если держать нажатой клавишу в одном направлении,
        а потом нажать клавишу другого направления и отпустить её прежде, чем будет отпущена первая по нажатию,
        то анимация будет задом наперёд.
        В целом баг забавный, поэтому исправлять не буду (лунная походка, всё-таки).
        '''
        if PLAYER_DEATH:
            return
        self.button_flags[direction_type] = status
        if not status and (direction_type == LEFT and self.button_flags[RIGHT] or (
                direction_type == RIGHT and self.button_flags[LEFT])):
            return
        if direction_type == LEFT and self.is_right:
            self.is_right = False
        if direction_type == RIGHT and not self.is_right:
            self.is_right = True
        if status:
            self.type_image = 'run'
        else:
            self.type_image = 'stay'


def level_1(game):
    global PLAYER_DEATH

    screen = game.main_screen
    clock = game.clock
    level = Level('level_1.tmx', scale=game.SCALE)
    player = Player(game, (4 * level.tile_size, 18 * level.tile_size), PLAYER_GROUP)
    camera = Camera(game.SIZE, pygame.Rect(0, 0, level.width * level.tile_size,
                                           level.height * level.tile_size))
    START_LEVEL_TIME = pygame.time.get_ticks()
    time_ui_sprite = TimeUI((game.WIDTH - 100, 0), ALL_TILES_GROUP, START_LEVEL_TIME)
    death_text = get_text_render('ПОМЕР', pygame.Color('darkred'), 150)

    manager = pygame_gui.UIManager(game.SIZE, 'scripts/theme_for_UI.json')

    entry = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((640 - 200, 360 - 40), (400, 80)),
        manager=manager, placeholder_text=' Введите Ваше имя сюда (ENTER для подтверждения)',

    )
    entry_flag = False

    leaderboard = False
    # событие для смены картинки игрока (анимация персонажа)
    CHANGEIMAGE = pygame.USEREVENT + 1
    pygame.time.set_timer(CHANGEIMAGE, 100)
    # создаём текст PRESS_ENTER с функцией мигания
    press_enter_render = get_text_render("Нажмите ENTER, чтобы продолжить", pygame.Color('black'),60)
    press_enter_pos = (game.WIDTH // 2 - press_enter_render.get_rect().width // 2, game.HEIGHT // 10 * 9)
    alpha_change = 0
    change_direction = -1
    press_enter_render.set_alpha(254)
    # Подсказки для игрока
    helping_texts = [("КЛАВИШИ ДЛЯ ПЕРЕМЕЩЕНИЯ", (2 * level.tile_size - 10, 22 * level.tile_size), 50),
                     ("ИЛИ", (300, 935), 40),
                     (" - РЕСТАРТ", (720, 20 * level.tile_size - 2), 50),
                     (" - ПОЛНОЭКРАННЫЙ РЕЖИМ", (720, 22 * level.tile_size - 2), 50),
                     ("Цель игры - пробежать как можно быстрее.", (2 * level.tile_size, 10 * level.tile_size - 10), 60),
                     ("При этом помните: жизнь всего одна", (2 * level.tile_size, 11 * level.tile_size), 60)]
    helping_text_render = []
    for line, pos, size in helping_texts:
        render_text = get_text_render(line, pygame.Color('white'), size)
        helping_text_render.append((render_text, pos))
    while True:
        time_delta = clock.tick(game.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == CHANGEIMAGE:
                player.change_image()
            elif event.type == HIT_PLAYER_EVENT:
                player.hit_animation(start=False)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                pygame.display.toggle_fullscreen()
            elif event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_d, pygame.K_RIGHT}:
                    player.move(RIGHT, True)
                if event.key in {pygame.K_a, pygame.K_LEFT}:
                    player.move(LEFT, True)
                if event.key == pygame.K_SPACE:
                    player.jump(True)
            elif event.type == pygame.KEYUP:
                if event.key in {pygame.K_d, pygame.K_RIGHT}:
                    player.move(RIGHT, False)
                if event.key in {pygame.K_a, pygame.K_LEFT}:
                    player.move(LEFT, False)
                if event.key == pygame.K_SPACE:
                    player.jump(False)
            # кнопка R - это Рестарт
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                for sprite in ALL_TILES_GROUP:
                    sprite.kill()
                player.kill()
                PLAYER_DEATH = False
                return 'RESTART'
            if event.type == pygame.KEYDOWN and event.key == 13:
                entry_flag = True
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    leaderboard_scene(game)
                    return 'LEADERS'
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    print('Name:', event.text)
                    game.add_to_leaderboard(event.text, time_ui_sprite.get_time())
                    entry.kill()
                    entry_flag = False
                    leaderboard = True
                    confirmed_dialog = pygame_gui.windows.UIConfirmationDialog(manager=manager,
                                                                               action_long_desc=f'Хотите ' +
                                                                                                'ли Вы посмотреть' +
                                                                                                '<br>таблицу лидеров?',
                                                                               action_short_name='Да, хочу',
                                                                               window_title='Таблица лидеров',
                                                                               rect=pygame.Rect((640 - 200, 360 - 100),
                                                                                                (400, 200)))
            try:
                manager.process_events(event)
            except:
                pass
        manager.update(time_delta)

        screen.fill('black')
        player.update()
        ALL_TILES_GROUP.update()
        game.BACKGROUND.update(player)
        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in ALL_TILES_GROUP:
            camera.apply(sprite)
        for sprite in game.ALL_SPRITES:
            camera.apply(sprite)
        camera.apply_self()
        game.BACKGROUND.draw(screen)
        ALL_TILES_GROUP.draw(screen)
        PLAYER_GROUP.draw(screen)
        # проверка на смерть игрока
        if PLAYER_DEATH:
            screen.blit(death_text, (game.WIDTH // 2 - death_text.get_width() // 2,
                                     game.HEIGHT // 2 - death_text.get_height() // 2))
            time_ui_sprite.stop()
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
        # вывод подсказок
        if camera.pos_in_map[0] < 2600:
            for i in range(len(helping_text_render)):
                text, pos = helping_text_render[i]
                helping_text_render[i] = [text, (pos[0] + camera.dx, pos[1] + camera.dy)]
            for line, pos in helping_text_render:

                screen.blit(line, pos)
        # Проверка на окончание игры
        if player.rect.x >= 940:
            time_ui_sprite.stop()
            congrats_text = get_text_render('УРОВЕНЬ ПРОЙДЕН', pygame.Color('azure1'), 130)
            screen.blit(congrats_text, (game.WIDTH // 2 - congrats_text.get_width() // 2,
                                        game.HEIGHT // 2 - congrats_text.get_height() // 2 - 200))
            congrats_text = get_text_render(f'время: {time_ui_sprite.get_time()} сек.', pygame.Color('azure1'), 100)
            screen.blit(congrats_text, (game.WIDTH // 2 - congrats_text.get_width() // 2,
                                        game.HEIGHT // 2 - congrats_text.get_height() // 2 - 80))
            screen.blit(press_enter_render, press_enter_pos)

        if entry_flag or leaderboard:
            manager.draw_ui(screen)

        # обновляем экран
        pygame.display.flip()
        # clock.tick(game.FPS)
