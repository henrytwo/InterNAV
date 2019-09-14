from mapping_util import *
from pygame import *
from math import hypot
import firebase_manager
import datetime
import copy
import firebase_admin
import wifi_manager
from firebase_admin import credentials


def draw_shit():
    def center(p):
        nonlocal pos, new_map_rect
        pos[0] += screen_size[0] // 2 - (pos[0] + int(new_map_img.get_width() * p[0]))
        pos[1] += screen_size[1] // 2 - (pos[1] + int(new_map_img.get_height() * p[1]))
        new_map_rect.topleft = pos

    def update_map():
        nonlocal new_map_img, new_map_rect, dot_surf
        new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
        new_map_rect.size = new_map_img.get_size()
        new_map_rect.topleft = pos
        dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

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

    points = firebase_manager.get_nodes()

    highlighted_point = ''

    unsaved_changes = False
    last_synced = 'Never'
    data_list = []

    to_be_scanned = {}

    point_recorded = False

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
                if e.button == 3 and mode == 'data':
                    mx, my = e.pos
                    mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                    my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())

                    minpoint = ()
                    minval = 99999

                    for pointid in points:

                        p = points[pointid]['location']

                        dist = hypot(p[0] - mx, p[1] - my)
                        print(dist)
                        if dist < 0.005 and dist < minval:
                            minpoint = p
                            minval = dist

                    if minpoint != ():
                        del points[firebase_manager.generate_id(minpoint)]
                        draw.circle(dot_surf, (0, 0, 0, 0), (
                            int(new_map_img.get_width() * minpoint[0]),
                            int(new_map_img.get_height() * minpoint[1])), 5)

                    unsaved_changes = True

            elif e.type == MOUSEBUTTONUP:
                if e.button == 1 and mode == 'data':
                    mx, my = e.pos
                    mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                    my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())

                    minpoint = ()
                    minval = 99999

                    for pointid in points:

                        p = points[pointid]['location']

                        dist = hypot(p[0] - mx, p[1] - my)
                        print(dist)
                        if dist < 0.005 and dist < minval:
                            minpoint = p
                            minval = minpoint

                            highlighted_point = firebase_manager.generate_id(p)

                    if minpoint == ():
                        if not click_and_drag and new_map_rect.collidepoint(e.pos):
                            mx, my = e.pos
                            mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                            my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())

                            points[firebase_manager.generate_id([mx, my])] = {
                                'location': [mx, my]
                            }

                    else:
                        center(minpoint)

                    unsaved_changes = True

                elif e.button == 4:
                    if manual_zoom < 2:
                        manual_zoom += 0.05
                        pos[0] -= int((abs(e.pos[0]) / img_w) * p_w)
                        pos[1] -= int((abs(e.pos[1]) / img_h) * p_h)
                        update_map()

                elif e.button == 5:
                    if manual_zoom > 0.25:
                        manual_zoom -= 0.05
                        pos[0] += int((abs(e.pos[0]) / img_w) * p_w)
                        pos[1] += int((abs(e.pos[1]) / img_h) * p_h)
                        update_map()

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
                update_map()
                display.set_mode(screen_size, RESIZABLE)

        else:

            keys_shit = key.get_pressed()

            if keys_shit[K_1]:
                mode = 'viewing'

            if keys_shit[K_2]:
                mode = 'data'

            if keys_shit[K_3]:
                mode = 'scanning'

                to_be_scanned = copy.deepcopy(points)

                for i in copy.deepcopy(to_be_scanned):
                    if 'aps' in to_be_scanned[i]:
                        del to_be_scanned[i]

            if keys_shit[K_4]:
                print('FIREBASE SYNCED!')

                last_synced = str(datetime.datetime.now())
                unsaved_changes = False

                firebase_manager.set_nodes(points)

            if keys_shit[K_5] and mode == 'scanning' and not point_recorded:
                point_recorded = True

                points[highlighted_point]['aps'] = wifi_manager.dump_aps('wlp0s20f3')

                del to_be_scanned[highlighted_point]

            elif not keys_shit[K_5]:
                point_recorded = False

            data_list = [
                'MODE: ' + mode,
                'LAST SYNCED: ' + last_synced,
                'UNSAVED CHANGES: ' + str(unsaved_changes)
            ]

            if mode == 'scanning':
                data_list.append('PLEASE MOVE TO DESIGNATED POSITION AND PRESS 5 TO RECORD POINT!')
                data_list.append('POINTS REMAINING: ' + str(len(to_be_scanned.keys())))

                highlighted_point = list(to_be_scanned.keys())[0]
                center(to_be_scanned[highlighted_point]['location'])


            screen.fill((0, 0, 0))
            pos[0] = max(min(pos[0], screen_size[0] - 160), 160 - new_map_img.get_width())
            pos[1] = max(min(pos[1], screen_size[1] - 160), 160 - new_map_img.get_height())

            screen.blit(new_map_img, pos)

            for pointid in points:

                rx, ry = points[pointid]['location']

                if firebase_manager.generate_id([rx, ry]) == highlighted_point:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)

                draw.circle(dot_surf, color,
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
    cred = credentials.Certificate('firebase_key.json')
    firebase_admin.initialize_app(cred)

    draw_shit()
