from mapping_util import *
from pygame import *
from math import hypot
import firebase_manager
import datetime
import copy
import firebase_admin
import wifi_manager
from firebase_admin import credentials
import calculationshit


def draw_shit():
    def firebase_sync():
        global last_synced, unsaved_changes

        print('FIREBASE SYNCED!')

        last_synced = str(datetime.datetime.now())
        unsaved_changes = False

        firebase_manager.set_nodes(points)
        firebase_manager.set_edge(edges)

    def center(p):
        nonlocal pos, new_map_rect
        # pos[0] += screen_size[0] // 2 - (pos[0] + int(new_map_img.get_width() * p[0]))
        # pos[1] += screen_size[1] // 2 - (pos[1] + int(new_map_img.get_height() * p[1]))

        x_movement = screen_size[0] // 2 - (pos[0] + int(new_map_img.get_width() * p[0]))
        y_movement = screen_size[1] // 2 - (pos[1] + int(new_map_img.get_height() * p[1]))

        for x in range(x_movement):
            pos[0] += 1 * x_movement / abs(x_movement)
            update_map()
            display.update()

        for y in range(y_movement):
            pos[1] += 1 * y_movement / abs(y_movement)
            update_map()
            display.update()

        new_map_rect.topleft = pos

    def update_map():
        nonlocal new_map_img, new_map_rect, markup_surf
        new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
        new_map_rect.size = new_map_img.get_size()
        new_map_rect.topleft = pos
        markup_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

    init()

    map_img = image.load("notcoding.jpg")
    logo = transform.scale(image.load("InterNAV.png"), (600, 450))
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

    mode = 'data'

    # MODES
    # 1 - Viewing map and getting location
    # 2 - Adding/Modifying nodes and graph

    new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
    new_map_rect = new_map_img.get_rect()
    new_map_rect.topleft = pos
    markup_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

    text = font.SysFont("Bahnschrift", 18)

    click_and_drag = False

    points = firebase_manager.get_nodes()

    edges = firebase_manager.get_edges()
    current_edge = []

    if not points:
        points = {}

    highlighted_point = ''

    unsaved_changes = False
    last_synced = 'Never'
    data_list = []

    view_setup = False

    to_be_scanned = {}

    point_recorded = False

    screen.fill((200, 200, 255))
    screen.blit(logo, ((screen_size[0] - logo.get_width()) // 2, (screen_size[1] - logo.get_height()) // 2))
    display.flip()
    time.wait(2000)

    if not points:
        mode = 'data'

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
                        draw.circle(markup_surf, (0, 0, 0, 0), (
                            int(new_map_img.get_width() * minpoint[0]),
                            int(new_map_img.get_height() * minpoint[1])), 5)

                        hitlist = []

                        for i in edges:
                            if firebase_manager.generate_id(minpoint) in i:
                                hitlist.append(i)

                        for z in hitlist:
                            edges.remove(z)

                        del points[firebase_manager.generate_id(minpoint)]
                        update_map()

                    unsaved_changes = True

            elif e.type == MOUSEBUTTONUP:
                if e.button in [1, 2] and mode == 'data':
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
                        if e.button == 1:
                            center(minpoint)
                        elif e.button == 2:
                            current_edge.append(firebase_manager.generate_id(minpoint))
                            if len(current_edge) == 2:
                                edges.append(current_edge)
                                current_edge = []

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

                view_setup = False

            elif keys_shit[K_2]:
                mode = 'data'

            elif keys_shit[K_3]:
                mode = 'scanning'

                to_be_scanned = copy.deepcopy(points)

                unsaved_changes = True

                for i in copy.deepcopy(to_be_scanned):
                    if 'aps' in to_be_scanned[i]:
                        del to_be_scanned[i]

            elif keys_shit[K_4]:
                firebase_sync()

            elif keys_shit[K_5] and mode == 'scanning' and not point_recorded:
                point_recorded = True

                points[highlighted_point]['aps'] = wifi_manager.dump_aps('wlp0s20f3', 3)

                del to_be_scanned[highlighted_point]

            elif not keys_shit[K_5]:
                point_recorded = False

            if mode == 'viewing' and not view_setup:
                view_setup = True

                calculationshit.Initialize(points, None, None, edges)

            if mode == 'viewing':
                calculatedPosition = calculationshit.findLocation(wifi_manager.dump_aps('wlp0s20f3', 3))

                update_map()

                print('POSITION!: ', calculatedPosition)

            data_list = [
                'MODE: ' + mode,
                'LAST SYNCED: ' + last_synced,
                'UNSAVED CHANGES: ' + str(unsaved_changes)
            ]

            if mode == 'scanning':

                if len(to_be_scanned):

                    data_list.append('PLEASE MOVE TO DESIGNATED POSITION AND PRESS 5 TO RECORD POINT!')
                    data_list.append('POINTS REMAINING: ' + str(len(to_be_scanned.keys())))

                    highlighted_point = list(to_be_scanned.keys())[0]
                    center(to_be_scanned[highlighted_point]['location'])

                    manual_zoom = 2
                    pos[0] -= int(to_be_scanned[highlighted_point]['location'][0] * p_w)
                    pos[1] -= int(to_be_scanned[highlighted_point]['location'][1] * p_h)

                    update_map()

                else:
                    data_list.append('SCANNING COMPLETE!')
                    data_list.append('PRESS 1 TO RETURN TO VIEW MODE')

                    if unsaved_changes:
                        firebase_sync()

            screen.fill((0, 0, 0))
            pos[0] = max(min(pos[0], screen_size[0] - 160), 160 - new_map_img.get_width())
            pos[1] = max(min(pos[1], screen_size[1] - 160), 160 - new_map_img.get_height())

            screen.blit(new_map_img, pos)

            for id1, id2 in edges:
                try:
                    (rx1, ry1), (rx2, ry2) = points[id1]['location'], points[id2]['location']
                    draw.line(markup_surf, (0, 255, 255),
                              (int(new_map_img.get_width() * rx1), int(new_map_img.get_height() * ry1)),
                              (int(new_map_img.get_width() * rx2), int(new_map_img.get_height() * ry2)))
                except:
                    update_map()

            for pointid in points:

                rx, ry = points[pointid]['location']

                if firebase_manager.generate_id([rx, ry]) == highlighted_point:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)

                draw.circle(markup_surf, color,
                            (int(new_map_img.get_width() * rx), int(new_map_img.get_height() * ry)), 5)

            if mode == 'viewing':
                draw.circle(markup_surf, (0, 0, 255),
                            (int(new_map_img.get_width() * calculatedPosition[0]),
                             int(new_map_img.get_height() * calculatedPosition[1])), 5)

            screen.blit(markup_surf, pos)

            for i, data in enumerate(data_list):
                screen.blit(text.render(data, True, (0, 0, 0), (220, 220, 220)), (20, 20 + 30 * i))

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
