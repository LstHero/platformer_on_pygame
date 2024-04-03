tile_size = 16
with open('simple_levels\level_1', 'w') as txt_file:
    for i in range(23):
        if i < 15:
            txt_file.write('.' * 200 + '\n')
        elif i == 15:
            txt_file.write('%' * 200 + '\n')
        else:
            txt_file.write('#' * 200 + '\n')
    for i in range(7):
        txt_file.write('$' * 200)