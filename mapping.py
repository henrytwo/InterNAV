from mapping_util import *
from pygame import *
from math import hypot
import firebase_manager
import datetime

import firebase_admin
from firebase_admin import credentials


def draw_screen():
    cred = credentials.Certificate('firebase_key.json')
    firebase_admin.initialize_app(cred)

    init()

    map_img = image.load("notcoding.jpg")
    logo = transform.scale(image.load("logo.png"), (600, 450))
    screen_size = get_start_dims(map_img)
    img_w, img_h = map_img.get_size()
    p_w, p_h = img_w * 0.05, img_h * 0.05

    screen = display.set_mode(screen_size, RESIZABLE)
    display.set_caption("InterNAV")

    clock = time.Clock()

    screen_zoom = get_zoom(map_img, *screen_size)
    manual_zoom = 1
    angle = 0
    pos = [0, 0]

    mode = 'viewing'

    # MODES
    # 1 - Viewing map and getting location
    # 2 - Adding/Modifying nodes and graph

    new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
    new_map_rect = new_map_img.get_rect()
    new_map_rect.topleft = pos
    dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

    text = font.SysFont("Comic Sans MS", 20, bold=True, italic=True)

    click_and_drag = False

    raw_points = firebase_manager.get_nodes()

    points = []

    unsaved_changes = False
    last_synced = 'Never'
    data_list = []

    if raw_points:
        for i in raw_points:
            points.append(raw_points[i]['location'])

    screen.fill((200, 200, 255))
    screen.blit(logo, ((screen_size[0] - logo.get_width()) // 2, (screen_size[1] - logo.get_height()) // 2))
    display.flip()
    time.wait(200)

    while True:
        mb = mouse.get_pressed()
        for e in event.get():
            if e.type == QUIT:
                break
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 3:
                    mx, my = e.pos
                    mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                    my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())

                    minpoint = ()
                    minval = 99999

                    for p in points:
                        dist = hypot(p[0] - mx, p[1] - my)
                        print(dist)
                        if dist < 0.005 and dist < minval:
                            minpoint = p
                            minval = minpoint

                    if minpoint != ():
                        points -= {minpoint}
                        draw.circle(dot_surf, (0, 0, 0, 0), (
                            int(new_map_img.get_width() * minpoint[0]),
                            int(new_map_img.get_height() * minpoint[1])), 5)

            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    mx, my = e.pos
                    mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                    my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())

                    minpoint = ()
                    minval = 99999

                    for p in points:
                        dist = hypot(p[0] - mx, p[1] - my)
                        print(dist)
                        if dist < 0.005 and dist < minval:
                            minpoint = p
                            minval = minpoint

                    if minpoint == ():
                        if not click_and_drag and new_map_rect.collidepoint(e.pos):
                            mx, my = e.pos
                            mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                            my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())
                            points.append([mx, my])

                            firebase_manager.set_nodes(points)

                    else:
                        print(minpoint)
                        pos[0] += screen_size[0] // 2 - minpoint[0]
                        pos[1] += screen_size[1] // 2 - minpoint[1]
                        new_map_rect.topleft = pos

                elif e.button == 4:
                    if manual_zoom < 2:
                        manual_zoom += 0.05
                        pos[0] -= int((abs(e.pos[0]) / img_w) * p_w)
                        pos[1] -= int((abs(e.pos[1]) / img_h) * p_h)
                        new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
                        new_map_rect.size = new_map_img.get_size()
                        new_map_rect.topleft = pos
                        dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

                elif e.button == 5:
                    if manual_zoom > 0.25:
                        manual_zoom -= 0.05
                        pos[0] += int((abs(e.pos[0]) / img_w) * p_w)
                        pos[1] += int((abs(e.pos[1]) / img_h) * p_h)
                        new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
                        new_map_rect.size = new_map_img.get_size()
                        new_map_rect.topleft = pos
                        dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

                click_and_drag = False
            elif e.type == MOUSEMOTION:
                if mb[0]:
                    click_and_drag = True
                    pos[0] += e.rel[0]
                    pos[1] += e.rel[1]
                    new_map_rect.topleft = pos

            elif e.type == VIDEORESIZE:
                screen_size[0] = max(800, e.size[0])
                screen_size[1] = max(600, e.size[1])
                screen_zoom = get_zoom(map_img, *screen_size)
                new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
                new_map_rect.size = new_map_img.get_size()
                new_map_rect.topleft = pos
                dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)
                display.set_mode(screen_size, RESIZABLE)

        else:

            keys_shit = key.get_pressed()

            if keys_shit[K_1]:
                mode = 'viewing'

            if keys_shit[K_2]:
                mode = 'data'

            if keys_shit[K_3]:
                mode = 'scanning'

            if keys_shit[K_4]:
                print('FIREBASE SYNCED!')

                last_synced = str(datetime.datetime.now())
                unsaved_changes = False

                firebase_manager.set_nodes(points)

            data_list = [
                'MODE: ' + mode,
                'LAST SYNCED: ' + last_synced,
                'UNSAVED CHANGES: ' + str(unsaved_changes)
            ]

            screen.fill((0, 0, 0))
            pos[0] = max(min(pos[0], screen_size[0] - 160), 160 - new_map_img.get_width())
            pos[1] = max(min(pos[1], screen_size[1] - 160), 160 - new_map_img.get_height())

            screen.blit(new_map_img, pos)

            for rx, ry in points:
                draw.circle(dot_surf, (255, 0, 0),
                            (int(new_map_img.get_width() * rx), int(new_map_img.get_height() * ry)), 5)
            screen.blit(dot_surf, pos)

            for i, data in enumerate(data_list):
                screen.blit(text.render(data, True, (0, 0, 0), (200, 200, 200)), (20, 20 + 30 * i))

            clock.tick()
            display.set_caption(f"InterNAV | FPS: {int(clock.get_fps())}")
            display.update()
            continue

        break

    display.quit()


if __name__ == '__main__':
    draw_screen()

    cred = credentials.Certificate('firebase_key.json')
    firebase_admin.initialize_app(cred)