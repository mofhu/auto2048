import cv2
import numpy as np


def main():
    bricks = read_images()
    im = pyautogui.screenshot(region=(200, 250, 1020, 1220))  # screenshot
    im.save("screen.png")
    img_screen = cv2.imread('screen.png', 0)
    img_title = cv2.imread('images/title.png', 0)
    res = cv2.matchTemplate(img_screen, img_title, cv2.TM_CCOEFF_NORMED)
    threshold = 0.99
    loc = np.where(res >= threshold)
    print(loc)
    for pos in zip(*loc[::-1]):
        print(pos)

    for i in range(4):
        for j in range(4):
            img_brick = get_brick_image(img_screen, i, j)
            flag_find = False
            for key in bricks:
                res = cv2.matchTemplate(img_brick, bricks[key],
                                        cv2.TM_CCOEFF_NORMED)
                threshold = 0.99
                loc = np.where(res >= threshold)
                for pt in zip(*loc[::-1]):
                    print(key, ':', i, j)
                    flag_find = True
                if flag_find:
                    break

    print(img_screen.shape)
    # cv2.imshow("img", img_screen)
    # cv2.waitKey(0)
    # template = cv2.imread('images/0.png',0)
    # w, h = template.shape[::-1]


def read_images(debug=False):
    """Read known brick images."""

    from collections import OrderedDict
    bricks = {}
    for image in os.listdir("images"):  # match for blocks
        num = re.match("\d+", image)
        if not num:
            continue
        else:
            num = int(num.group())
            bricks[num] = cv2.imread("images/{}.png".format(num), 0)
        if debug:
            cv2.imshow(str(num), bricks[num])
            cv2.waitKey(0)
    bricks = OrderedDict(sorted(bricks.items()))
    return bricks


def get_brick_image(img_screen, row, column):
    """Get brick image using numpy slices."""

    WIDTH_SHIFT = 218
    HEIGHT_SHIFT = 20
    WIDTH_BLOCK = 242
    HEIGHT_BLOCK = 242

    img_brick = img_screen[
        WIDTH_SHIFT+WIDTH_BLOCK*row : WIDTH_SHIFT+WIDTH_BLOCK*(row+1),
        HEIGHT_SHIFT+HEIGHT_BLOCK*column : HEIGHT_SHIFT+HEIGHT_BLOCK*(column+1)
    ]

    # cv2.imshow("brick row {}, column {}".format(row, column), img_brick)
    # cv2.waitKey(0)
    return img_brick


import pyautogui
import re
import os


def get_screen(debug=False, max_block=2048):
    block_matrix = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    im = pyautogui.screenshot(region=(200, 250, 1020, 1220))  # screenshot
    im.save("screen.png")
    title = pyautogui.locateOnScreen("images/title.png", im, grayscale=True)
    print(title)
    pyautogui.moveTo([title[0] / 2, title[1] / 2])
    print(type(im))
    return
    for image in os.listdir("images"):  # match for blocks
        num = re.match("\d+", image)
        if not num:
            continue
        else:
            num = int(num.group())
            if num > max_block * 2:
                continue
        if debug:
            print(image)
        block = pyautogui.locateAll("images/"+image, im, grayscale=True)
        for pos in block:
            if debug:
                print(pos)
            index = pos_to_shape(pos, debug=False)
            block_matrix[index[1]][index[0]] = num
    if debug:
        print(block_matrix)
    return block_matrix

#import cProfile
#cProfile.run('main()')
#get_screen()
main()

