"""
Solver for "Runaway Robot" - hacker.org/runaway
By Barney Gale

The trick to this solution is to categorize moves by their widths and heights.
Each move must have a manhattan distance between the minimum and maximum move
length. For each such combination of width and height, we generate a window
of those dimensions and tile it diagonally across the board, which bakes info
about that board into the window. We remove dead ends simultaneously. Any
window where (0, 0) is not an obstacle is trivially solvable.

No hacker.org level takes more than about a second. This algorithm doesn't use
any backtracking, and I believe it runs in polynomial time
"""


import re
import time
import numpy
import requests


USERNAME = ""
PASSWORD = ""


session = requests.Session()
window = numpy.empty(shape=(500, 500), dtype=numpy.bool)


def solve_board(board, move_min, move_max):
    """
    Iterate over possible window dimensions and attempt to solve each one.
    """

    # Generate window sizes
    window_sizes = [
        (h, move_len - h)
        for move_len in xrange(move_min, move_max + 1)
        for h in xrange(1, move_len)]

    # Check square-ish windows first
    window_sizes.sort(key=lambda size: abs(size[0] - size[1]))

    # Attempt to solve each window
    for h, w in window_sizes:
        solution = solve_window(board, h, w)
        if solution:
            return solution


def solve_window(board, h, w):
    """
    Finds a path from the top left to the bottom right in the given window.
    """

    # Skip unsolvable window
    if any(board[h::h, w::w].diagonal()):
        return

    # Add the window border
    for y in xrange(h): window[y, w + 1] = True
    for x in xrange(w): window[h + 1, x] = True
    window[h, w + 1] = False
    window[h + 1, w] = False

    # Load the window data
    for y in xrange(h, -1, -1):
        solvable = False
        for x in xrange(w, -1, -1):
            if (window[y + 1, x] and window[y, x + 1]) \
                    or any(board[y::h, x::w].diagonal()):
                window[y, x] = True
            else:
                window[y, x] = False
                solvable = True

        # Skip unsolvable window
        if not solvable:
            return

    # Skip unsolvable window
    if window[0, 0]:
        return

    # Find the solution
    y, x = 0, 0
    solution = []
    while y != h or x != w :
        if not window[y+1, x]:
            y += 1
            solution.append("D")
        else:
            x += 1
            solution.append("R")

    return "".join(solution)


def main():
    request = {'name': USERNAME, 'password': PASSWORD}
    while True:
        # Request the level
        response = session.get(
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
