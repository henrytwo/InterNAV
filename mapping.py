from mapping_util import *
from pygame import *

init()

map_img = image.load('notcoding.png')
screen_size = get_start_dims(map_img)

screen = display.set_mode(screen_size, RESIZABLE)
display.set_caption('geiii')

clock = time.Clock()

screen_zoom = get_zoom(map_img, *screen_size)
manual_zoom = 1
angle = 0
pos = 0, 0

new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)

click_and_drag = False

points = set()

while True:
    for e in event.get():
        if e.type == QUIT:
            break
        elif e.type == MOUSEBUTTONDOWN:
            pass
        elif e.type == MOUSEBUTTONUP:
            if e.button == 4:
                manual_zoom += 0.05
                new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
            elif e.button == 5:
                manual_zoom -= 0.05
                new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
            else:
                mx, my = e.pos
                mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())
                points.add((mx, my))
                print((mx, my))
        elif e.type == MOUSEMOTION:
            print('wow')
        elif e.type == VIDEORESIZE:
            screen_size = e.size
            screen_zoom = get_zoom(map_img, *screen_size)
            new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
            display.set_mode(screen_size, RESIZABLE)

    else:
        screen.fill((0, 0, 0))
        screen.blit(new_map_img, pos)

        clock.tick()
        display.set_caption(f'2cool {clock.get_fps()}')
        display.update()
        continue

    break

display.quit()
