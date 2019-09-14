from pygame import *


def get_zoom(img, new_width=1280, new_height=720):
    screen_ratio = new_width / new_height
    img_ratio = img.get_width() / img.get_height()

    if screen_ratio > img_ratio:  # if screen is a "wider" image than supplied image
        return new_height / img.get_height()
    else:  # if screen is less wide than the image
        return new_width / img.get_width()


def get_start_dims(img, new_width=1280, new_height=720):
    specs = display.Info()

    screen_ratio = specs.current_w / specs.current_h
    img_ratio = img.get_width() / img.get_height()

    if screen_ratio > img_ratio:  # if screen is a "wider" image than supplied image
        return [round(img.get_width() * new_height / img.get_height()), new_height]
    else:  # if screen is less wide than the image
        return [new_width, round(img.get_height() * new_width / img.get_width())]
