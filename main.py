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
import multiprocessing
import time as t

manager = multiprocessing.Manager()
shared_dict = manager.dict()

cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)


def update_position(shared_dict):
    while True:
        shared_dict['data'] = wifi_manager.dump_aps('wlp0s20f3', 3)


def draw_shit(shared_dict):
    def firebase_sync():
        nonlocal last_synced, unsaved_changes

        print('FIREBASE SYNCED!')

        last_synced = str(datetime.datetime.now())
        unsaved_changes = False

        firebase_manager.set_nodes(points)
        firebase_manager.set_edge(edges)

    def center(p):

        nonlocal pos, new_map_rect
        # pos[0] += screen_size[0] // 2 - (pos[0] + int(new_map_img.get_width() * p[0]))
        # pos[1] += screen_size[1] // 2 - (pos[1] + int(new_map_img.get_height() * p[1]))

        x_movement = int(screen_size[0] // 2 - (pos[0] + int(new_map_img.get_width() * p[0])))
        y_movement = int(screen_size[1] // 2 - (pos[1] + int(new_map_img.get_height() * p[1])))

        print(x_movement, y_movement, p)

        while abs(x_movement) > 2 or abs(y_movement) > 2:
            pos[0] += x_movement / 2
            pos[1] += y_movement / 2

            x_movement /= 2
            y_movement /= 2
            update_map()
            display.update()
        print('gei')

        # pos is top left corner
        #

        # print('moving x')
        # for x in range(abs(x_movement) // 3):
        #     pos[0] += 3 * x_movement / abs(x_movement)
        #     update_map()
        #     display.update()
        #
        # print('moving y')
        # for y in range(abs(y_movement) // 3):
        #     pos[1] += 3 * y_movement / abs(y_movement)
        #     update_map()
        #     display.update()

        new_map_rect.topleft = pos

    def update_map():
        nonlocal new_map_img, new_map_rect, markup_surf
        new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
        new_map_rect.size = new_map_img.get_size()
        new_map_rect.topleft = pos
        markup_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)
        screen.fill(0)
        screen.blit(new_map_img, pos)

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

    mode = 'viewing'

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

    auto_zoomed = False

    point_recorded = False

    navigation_path = None

    last_position = None

    screen.fill((200, 200, 255))
    screen.blit(logo, ((screen_size[0] - logo.get_width()) // 2, (screen_size[1] - logo.get_height()) // 2))
    display.flip()
    t.sleep(0.05)

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
                        # print(dist)
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
                if e.button in [1, 2]:
                    mx, my = e.pos
                    mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                    my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())

                    minpoint = ()
                    minval = 99999

                    for pointid in points:

                        p = points[pointid]['location']

                        dist = hypot(p[0] - mx, p[1] - my)
                        # print(dist)
                        if dist < 0.005 and dist < minval:
                            minpoint = p
                            minval = dist

                            highlighted_point = firebase_manager.generate_id(p)

                    if minpoint == ():
                        if not click_and_drag and new_map_rect.collidepoint(e.pos) and mode == 'data':
                            mx, my = e.pos
                            mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                            my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())

                            points[firebase_manager.generate_id([mx, my])] = {
                                'location': [mx, my]
                            }

                    else:
                        if e.button == 1 and mode == 'viewing':
                            center(minpoint)

                            navigation_path = calculationshit.getPath(firebase_manager.generate_id(minpoint))
                        if e.button == 2:
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

                navigation_path = None
                view_setup = False

            elif keys_shit[K_2]:
                mode = 'data'

            elif keys_shit[K_3]:
                mode = 'scanning'

                auto_zoomed = False

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
                calculatedPosition = calculationshit.findLocation(
                    shared_dict['data'] if ('data' in shared_dict) else wifi_manager.dump_aps('wlp0s20f3', 3))


                if calculatedPosition != last_position and navigation_path:
                    navigation_path = calculationshit.getPath(firebase_manager.generate_id(minpoint))

                    last_position = copy.deepcopy(calculatedPosition)


                update_map()

                #print('POSITION!: ', calculatedPosition)

            data_list = [
                'Keyboard commands: 1-View/Navigation 2-Configuration 3-Scanning 4-Sync with Firebase 5-Record RP',
                'MODE: ' + mode,
                'LAST SYNCED: ' + last_synced,
                'UNSAVED CHANGES: ' + str(unsaved_changes)
            ]

            if mode == 'scanning':

                if len(to_be_scanned):

                    data_list.append('PLEASE MOVE TO DESIGNATED POSITION AND PRESS 5 TO RECORD POINT!')
                    data_list.append('POINTS REMAINING: ' + str(len(to_be_scanned.keys())))

                    highlighted_point = list(to_be_scanned.keys())[0]
                    print('hey')

                    if not auto_zoomed:
                        manual_zoom = 2
                        pos[0] -= int(to_be_scanned[highlighted_point]['location'][0] * p_w)
                        pos[1] -= int(to_be_scanned[highlighted_point]['location'][1] * p_h)

                        auto_zoomed = True

                    center(to_be_scanned[highlighted_point]['location'])


                    update_map()

                else:
                    data_list.append('SCANNING COMPLETE!')
                    data_list.append('PRESS 1 TO RETURN TO VIEW MODE')

                    if unsaved_changes:
                        firebase_sync()

            screen.fill((255,255,255))
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

            if navigation_path:
                for id1, id2 in navigation_path:

                    (rx1, ry1), (rx2, ry2) = id1, id2
                    draw.line(markup_surf, (255, 0, 255),
                              (int(new_map_img.get_width() * rx1), int(new_map_img.get_height() * ry1)),
                              (int(new_map_img.get_width() * rx2), int(new_map_img.get_height() * ry2)), 5)


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
            #display.set_caption(f"InterNAV | FPS: {int(clock.get_fps())}")
            display.set_caption(f"InterNAV")
            display.update()
            continue

        break

    display.quit()


up = multiprocessing.Process(target=update_position, args=(shared_dict,))
up.start()

dp = multiprocessing.Process(target=draw_shit, args=(shared_dict,))
dp.start()

print('Running!')
input('Press any key to end')
