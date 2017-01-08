import pyautogui
import cv2
import numpy as np
import re
import time
import os
from pprint import pprint


def init_screen(debug=False):
    """init screen."""
    block_matrix = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

    bricks = read_images()
    # screenshot: note that window is not shifted by title image
    im = pyautogui.screenshot(region=(200, 250, 1020, 1220))
    img_screen = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)

    # get title bar position
    img_title = cv2.imread('images/title.png', 0)
    res = cv2.matchTemplate(img_screen, img_title, cv2.TM_CCOEFF_NORMED)
    threshold = 0.99
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        print("init of title bar: {}".format(pt))
        pos_title_bar = pt

    # init bricks
    for i in range(4):
        for j in range(4):
            img_brick = get_brick_image(img_screen, pos_title_bar, i, j)
            flag_find = False
            for key in bricks:
                res = cv2.matchTemplate(img_brick, bricks[key],
                                        cv2.TM_CCOEFF_NORMED)
                threshold = 0.99
                loc = np.where(res >= threshold)
                for pt in zip(*loc[::-1]):
                    block_matrix[i][j]= key
                    flag_find = True
                if flag_find:
                    break
    if debug:
        print(block_matrix)
    return block_matrix, pos_title_bar


def get_screen(block_matrix, pos_title_bar, debug=False):
    """Get new screen after move."""

    bricks = read_images()
    im = pyautogui.screenshot(region=(200, 250, 1020, 1220))  # screenshot
    img_screen = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)

    for i in range(4):
        for j in range(4):
            if block_matrix[i][j] != 0:
                continue
            img_brick = get_brick_image(img_screen, pos_title_bar, i, j)
            flag_find = False
            for key in bricks:
                res = cv2.matchTemplate(img_brick, bricks[key],
                                        cv2.TM_CCOEFF_NORMED)
                threshold = 0.99
                loc = np.where(res >= threshold)
                for pt in zip(*loc[::-1]):
                    # print("brick row {}, column {}, num {}".format(i, j, key))
                    block_matrix[i][j]= key
                    if key != 0:  # find non-zero brick, i.e. the new block
                        return block_matrix
                    else:
                        flag_find = True
                if flag_find:
                    break
    if debug:
        print(block_matrix)

    # if no new brick found, the game is over
    return None


def read_images(debug=False):
    """Read known brick images."""

    # use OrderedDict to search from low to high bricks
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


def get_brick_image(img_screen, pos_title_bar, row, column):
    """Get brick image using numpy slices."""

    WIDTH_SHIFT = 218 + pos_title_bar[1]
    HEIGHT_SHIFT = 20 + pos_title_bar[0]
    WIDTH_BLOCK = 242
    HEIGHT_BLOCK = 242

    img_brick = img_screen[
        WIDTH_SHIFT+WIDTH_BLOCK*row : WIDTH_SHIFT+WIDTH_BLOCK*(row+1),
        HEIGHT_SHIFT+HEIGHT_BLOCK*column : HEIGHT_SHIFT+HEIGHT_BLOCK*(column+1)
    ]

    # cv2.imshow("brick row {}, column {}".format(row, column), img_brick)
    # cv2.waitKey(0)
    return img_brick


def pos_to_shape(pos, debug=True):
    if debug:
        print((int(pos[0]/240), int(pos[1] / 240)))
    return (int(pos[0]/240), int(pos[1] / 240))


def cal_move(block_matrix, debug=False):
    """wrapper for calculate best move and score."""
    MAX_SCORE = 10000
    best_score = MAX_SCORE
    best_direction = ''

    for direction in ['right','left','up','down']:
        moved_matrix = move(block_matrix, direction)
        if is_block_equal(block_matrix, moved_matrix):
            continue  # not valid move
        else:
            moved_score = score_blocks(moved_matrix, debug=False)
            if debug:
                print(direction, moved_score)
            if moved_score < best_score:
                best_score = moved_score
                best_direction = direction
    if debug:
        print("Best move is {}.".format(best_direction))
    return best_direction


def move(block_matrix, direction, debug=False):
    """move and combine."""
    if debug:
        print(block_matrix)
        print(direction)
    if direction is 'right':
        block_matrix = move_right(block_matrix)
    if direction is 'left':
        block_matrix = turn_right(turn_right(block_matrix))
        block_matrix = move_right(block_matrix)
        block_matrix = turn_left(turn_left(block_matrix))
    if direction is 'up':
        block_matrix = turn_left(block_matrix)
        block_matrix = move_right(block_matrix)
        block_matrix = turn_right(block_matrix)
    if direction is 'down':
        block_matrix = turn_right(block_matrix)
        block_matrix = move_right(block_matrix)
        block_matrix = turn_left(block_matrix)
    if debug:
        print(block_matrix)
    return block_matrix


def move_right(block_matrix):
    new_block = []
    for row in block_matrix:
        new_block.append(move_right_row(row, debug=False))
    return new_block


def move_right_row(row, debug=True):
    """move single row to right."""
    if debug:
        print(row)
    row_del_0 = []
    for i in row:  # copy non-zero blocks
        if i != 0:
            row_del_0.append(i)
    #print(row_del_0)
    row = row_del_0
    i = 0
    j = len(row_del_0) - 1
    while i < j:  # combine blocks
        #print(i, j)
        if row[j] == row[j-1]:
            row[j-1] *= 2
            del row[j]
            j -= 2
        else:
            j -= 1
    #print(i, j)
    #print(row_del_0)
    for i in range(4 - len(row_del_0)):  # insert zeros
        row_del_0.insert(0,0)
    if debug:
        print(row)
    return row


def turn_right(block_matrix, debug=False):
    """block turn right."""
    new_block = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for i in range(4):
        for j in range(4):
            new_block[3-j][i] = block_matrix[i][j]
    if debug:
        print(new_block)
    return new_block


def turn_left(block_matrix, debug=False):
    """block turn left."""
    new_block = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for i in range(4):
        for j in range(4):
            new_block[j][3-i] = block_matrix[i][j]
    if debug:
        print(new_block)
    return new_block


def is_block_equal(block1, block2):
    for i in range(4):
        for j in range(4):
            if block1[i][j] != block2[i][j]:
                return False
    return True


def score_blocks(block, debug=False):
    """Return status score."""
    score = 0
    SCORE_PER_BLOCK = 10
    SCORE_PER_NOT_EQUAL = 1

    for i in range(4):
        for j in range(4):
            if block[i][j] != 0:
                score += SCORE_PER_BLOCK
            else:
                continue
            if i < 3 and block[i+1][j] != 0:
                if block[i][j] == block[i+1][j]:
                    score -= SCORE_PER_NOT_EQUAL
                if block[i][j] >= block[i+1][j] * 4 or block[i][j] <= block[i+1][j] / 4 :
                    score += SCORE_PER_NOT_EQUAL * 2
            if j < 3 and block[i][j+1] != 0:
                if block[i][j] == block[i][j+1]:
                    score -= SCORE_PER_NOT_EQUAL
                if block[i][j] >= block[i][j+1] * 4 or block[i][j] <= block[i][j+1] / 4 :
                    score -= SCORE_PER_NOT_EQUAL * 2
    if debug:
        print(score)
    return score


def action(direction):
    """action in screen."""
    pyautogui.click(520, 720)  # activate 2048 page
    pyautogui.press(direction)


def main():
    i = 0  # profile
    pyautogui.PAUSE = 0
    block, pos_title_bar = init_screen(debug=False)
    while(True):
        t0 = time.time()
        best_direction = cal_move(block, debug=False)
        print("Best move is {}.".format(best_direction))
        action(best_direction)
        i += 1
        time.sleep(0.4)
        block = move(block, best_direction)  # calculate block after move
        block = get_screen(block, pos_title_bar, debug=False)
        if block == None:
            print("Game over")
            return
        t1 = time.time()
        print("move {}, time {:.2f}".format(i, t1 - t0 - 0.4))
    # action('left')
main()


"""
import cProfile
cProfile.run('main()', 'restats')  # 把 cProfile 的结果输出
import pstats
p = pstats.Stats('restats')  # pstats 读取输出的结果
p.sort_stats('cumulative').print_stats(20)  # 按照 cumtime 排序, print_stats(n) 则显示前 n 行
"""
