import pyautogui
import re
import time
import os
import pprint

def get_screen(debug=False, max_block=2048):
    block_matrix = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    im = pyautogui.screenshot(region=(200, 400, 1020, 1020))  # screenshot
    if debug:
        im.save("screen.png")
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
            continue
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
    """return status score."""
    score = 0
    SCORE_PER_BLOCK = 10
    SCORE_PER_NOT_EQUAL = 2

    for i in range(4):
        for j in range(4):
            if block[i][j] != 0:
                score += SCORE_PER_BLOCK
            else:
                continue
            if i < 3 and block[i+1][j] != 0:
                if block[i][j] == block[i+1][j]:
                    score -= SCORE_PER_NOT_EQUAL
                if block[i][j] > block[i+1][j] * 2 or block[i][j] < block[i+1][j] / 2 :
                    score += SCORE_PER_NOT_EQUAL / 2
            if j < 3 and block[i][j+1] != 0:
                if block[i][j] == block[i][j+1]:
                    score -= SCORE_PER_NOT_EQUAL
                if block[i][j] > block[i][j+1] * 2 or block[i][j] < block[i][j+1] / 2 :
                    score -= SCORE_PER_NOT_EQUAL / 2
    if debug:
        print(score)
    return score


def action(direction):
    """action in screen."""
    pyautogui.click(520, 720)  # activate 2048 page
    pyautogui.press(direction)


def find_max_block(block):
    """find max block in table."""
    block_1d = block[0] + block[1] + block[2] + block[3]
    return max(block_1d)


def main():
    i = 0  # profile
    pyautogui.PAUSE = 0
    max_block = 2048
    while(True):
        # print("max block is {}".format(max_block))
        time.sleep(0.3)
        t0 = time.time()
        block = get_screen(debug=False, max_block=max_block)
        pprint.pprint(block)
        max_block = find_max_block(block)
        #t1 = time.time()
        #print(t1 - t0)
        best_direction = cal_move(block, debug=False)
        print("Best move is {}.".format(best_direction))
        #time.sleep(1)
        action(best_direction)
        t1 = time.time()
        print(t1 - t0)
        i += 1  # profile
        if i == 20:
            break
    # action('left')
#main()
import cProfile
cProfile.run('main()', 'restats')  # 把 cProfile 的结果输出

import pstats
p = pstats.Stats('restats')  # pstats 读取输出的结果
p.sort_stats('cumulative').print_stats(20)  # 按照 cumtime 排序, print_stats(n) 则显示前 n 行
