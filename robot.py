"""
Solver for "Runaway Robot" - hacker.org/runaway
By Barney Gale

The trick to this solution is to categorize moves by their widths and heights.
Each move must have a manhattan distance between the minimum and maximum move
length. For each such combination of width and height, we generate a window
of those dimensions and tile it diagonally across the board, which bakes
information about that board into the window. We then use a conventional
backtracking algorithm to solve the window, where possible. The board and each
window are optimized to remove dead ends and, in the former case, unreachable
positions.

This is still an exponential-time algorithm, but it performs significantly
better than naive backtracking, with no hacker.org level taking more than about
a second.
"""


import re
import time
import numpy
import requests


USERNAME = ""
PASSWORD = ""


session = requests.Session()


def simplify_unreachable(terrain):
    """
    Mark the following unreachable positions as bombs:

    - Positions to the right of the leftmost bomb in the first row
    - Positions below the topmost bomb in the first column
    - Positions with bombs immediately above and to the left
    """

    seen = False
    for x in xrange(terrain.shape[0]):
        if seen:
            terrain[x, 0] = True
        elif terrain[x, 0]:
            seen = True

    seen = False
    for y in xrange(terrain.shape[1]):
        if seen:
            terrain[0, y] = True
        elif terrain[0, y]:
            seen = True

    for y in xrange(1, terrain.shape[1]):
        for x in xrange(1, terrain.shape[0]):
            if terrain[x-1, y] and terrain[x, y-1]:
                terrain[x, y] = True


def simplify_terminal(terrain):
    """
    Mark as bombs any positions with bombs immediately below and to the right.
    """

    for y in xrange(terrain.shape[1]-2, -1, -1):
        for x in xrange(terrain.shape[0]-2, -1, -1):
            if terrain[x+1, y] and terrain[x, y+1]:
                terrain[x, y] = True


def make_window(board, wx, wy):
    """
    Returns a rectangular window on to the given board. Each position in the
    window is the boolean OR of positions on the board moving diagonally in
    (wx, wy) steps from the start position.
    """

    window = numpy.zeros((wx + 1, wy + 1), dtype=numpy.bool)
    for y in xrange(window.shape[1]):
        for x in xrange(window.shape[0]):
            window[x, y] = any(board[x::wx, y::wy].diagonal())

    return window
    

def solve_board(board, move_min, move_max):
    """
    Iterate over possible window dimensions and attempt to solve each one.
    """

    simplify_unreachable(board)
    simplify_terminal(board)
    for move_len in xrange(move_min, move_max+1):
        for wx in xrange(1, move_len):
            wy = move_len - wx
            if not any(board[::wx, ::wy].diagonal()):
                window = make_window(board, wx, wy)
                solution = solve_window(window)
                if solution is not None:
                    return solution
   

def solve_window(window):
    """
    Finds a path from the top left to the bottom right in the given window.
    """

    simplify_terminal(window)
    stack = [[]]
    while len(stack) > 0:
        move = stack.pop(-1)
        x, y = move.count("R"), move.count("D")
        if x < window.shape[0] and y < window.shape[1] and not window[x, y]:
            if x == window.shape[0]-1 and y == window.shape[1]-1:
                return "".join(move)
            stack.append(move + ["R"])
            stack.append(move + ["D"])


def main():
    request = {'name': USERNAME, 'password': PASSWORD}
    while True:
        # Request the level
        response = requests.get(
            url="http://www.hacker.org/runaway/index.php",
            params=request)
        response = dict(re.findall('FV(\w+)=([^"&]+)', response.text))

        # Load terrain
        board = numpy.array(
            [".X".index(c) for c in response['terrainString']],
            dtype=numpy.bool)
        board = board.reshape(
            int(response['boardY']),
            int(response['boardX']))
        board = board.transpose()

        # Solve!
        start = time.time()
        request['path'] = solve_board(
            board,
            int(response['insMin']),
            int(response['insMax']))
        end = time.time()

        # Show progress
        print "level: %d\ttime: %.3f" % (int(response['level']), end - start)


if __name__ == "__main__":
    main()
