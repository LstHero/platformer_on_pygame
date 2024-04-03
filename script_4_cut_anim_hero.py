from PIL import Image
import os

for_anim = {'stay': ('_Idle.png', 10, 1),
            'run': ('_Run.png', 10, 1),
            'jump_up': ('_Jump.png', 3, 1),
            'jump_top': ('_JumpFallInbetween.png', 2, 1),
            'fall': ('_Fall.png', 3, 1),
            'death': ('_Death.png', 10, 1),
            'hit': ('_Hit.png', 1, 1),
            'turn_around': ('_TurnAround.png', 3, 1)}


start_path = 'data/image/120x80_PNGSheets'
all_files = os.listdir(start_path)
counts = []
ans = []
f_s = 'name: {filename}, mid = {mid}'
for key, (filename, *arr) in for_anim.items():
    if filename in all_files:
        if filename.split('.')[-1] != 'png':
            continue
        img = Image.open(start_path + '/' + filename)
        pixels = img.load()
        x, y = img.size
        count = 0
        for i in range(y):
            c = 0
            for j in range(x):
                if pixels[j, i] == (0, 0, 0, 0):
                    c += 1
            if c == x:
                count += 1
            else:
                break
        main_image = img.crop((0, count, x, y))
        x, y = main_image.size
        frames = []
        for i in range(0, x, 120):
            frames.append(main_image.crop((i, 0, i + 120, y)))
        os.mkdir('data/image/player_sec/' + key)
        for id, frame in enumerate(frames):
            pixels = frame.load()
            x, y = frame.size
            left = right = 0
            for i in range(x):
                c = 0
                for j in range(y):
                    if pixels[i, j] == (0, 0, 0, 0):
                        c += 1
                    else:
                        break
                if c == y:
                    left += 1
                else:
                    break
            for i in range(x - 1, -1, -1):
                c = 0
                for j in range(y):
                    if pixels[i, j] == (0, 0, 0, 0):
                        c += 1
                    else:
                        break
                if c == y:
                    right += 1
                else:
                    break
            width = x - left - right
            crop_frame = frame.crop((left, 0, left + width, y))
            crop_frame.save('data/image/player_sec/' + key + '/' + str(id) + filename)
