from mapping_util import *
from pygame import *
from math import hypot

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

new_map_img = transform.rotozoom(map_img, angle, screen_zoom * manual_zoom)
new_map_rect = new_map_img.get_rect()
new_map_rect.topleft = pos
dot_surf = Surface(new_map_img.get_size(), SRCALPHA, 32)

click_and_drag = False

points = set()

screen.fill((200, 200, 255))
screen.blit(logo, ((screen_size[0]-logo.get_width())//2, (screen_size[1]-logo.get_height())//2))
display.flip()
time.wait(2000)

while True:
    mb = mouse.get_pressed()
    for e in event.get():
        if e.type == QUIT:
            break
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                clicked = True
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
                    draw.circle(dot_surf, (0, 0, 0, 0), (int(new_map_img.get_width() * minpoint[0]), int(new_map_img.get_height() * minpoint[1])), 5)



        elif e.type == MOUSEBUTTONUP:
            if e.button == 1:
                if not click_and_drag and new_map_rect.collidepoint(e.pos):
                    mx, my = e.pos
                    mx = (mx - pos[0]) / ((screen_zoom * manual_zoom) * map_img.get_width())
                    my = (my - pos[1]) / ((screen_zoom * manual_zoom) * map_img.get_height())
                    points.add((mx, my))
                    
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

            clicked = False
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
        screen.fill((0, 0, 0))
        pos[0] = max(min(pos[0], screen_size[0]-160), 160-new_map_img.get_width())
        pos[1] = max(min(pos[1], screen_size[1]-160), 160-new_map_img.get_height())

        screen.blit(new_map_img, pos)

        for rx, ry in points:
            draw.circle(dot_surf, (255, 0, 0), (int(new_map_img.get_width() * rx), int(new_map_img.get_height() * ry)), 5)
        screen.blit(dot_surf, pos)

        clock.tick()
        display.set_caption(f"InterNAV      FPS: {int(clock.get_fps())}")
        display.update()
        continue

    break

display.quit()
