from mapping_util import *
from pygame import *

init()

map_img = image.load('notcoding.jpg')

screen_size = get_start_dims(map_img)
img_w, img_h = map_img.get_size()
p_w, p_h = img_w * 0.05, img_h * 0.05

screen = display.set_mode(screen_size, RESIZABLE)
display.set_caption('geiii')

clock = time.Clock()

screen_zoom = get_zoom(map_img, *screen_size)
manual_zoom = 1
angle = 0
pos = [0, 0]

new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

click_and_drag = False

points = set()

while True:
    mb = mouse.get_pressed()
    for e in event.get():
        if e.type == QUIT:
            break
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                clicked = True

        elif e.type == MOUSEBUTTONUP:
            if e.button == 1:
                if not click_and_drag:
                    mx, my = e.pos
                    mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                    my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())
                    points.add((mx, my))
                    print((mx, my))
            elif e.button == 4:
                if manual_zoom < 2:
                    manual_zoom += 0.05
                    pos[0] -= int((abs(e.pos[0]) / img_w) * p_w)
                    pos[1] -= int((abs(e.pos[1]) / img_h) * p_h)
                    new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
                    dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

            elif e.button == 5:
                if manual_zoom > 0.25:
                    manual_zoom -= 0.05
                    pos[0] += int((abs(e.pos[0]) / img_w) * p_w)
                    pos[1] += int((abs(e.pos[1]) / img_h) * p_h)
                    new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
                    dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

            clicked = False
            click_and_drag = False
        elif e.type == MOUSEMOTION:
            if mb[0]:
                pos[0] += e.rel[0]
                pos[1] += e.rel[1]
                click_and_drag = True

        elif e.type == VIDEORESIZE:
            screen_size = e.size
            screen_zoom = get_zoom(map_img, *screen_size)
            new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
            dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)
            display.set_mode(screen_size, RESIZABLE)

    else:
        screen.fill((0, 0, 0))
        screen.blit(new_map_img, pos)
        for rx, ry in points:
            draw.circle(dot_surf, (255, 0, 0), (int(new_map_img.get_width() * rx), int(new_map_img.get_height() * ry)), 5)
        screen.blit(dot_surf, pos)

        clock.tick()
        display.set_caption(f'2cool {clock.get_fps()}')
        display.update()
        continue

    break

display.quit()
