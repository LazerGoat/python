import math
from collections import namedtuple
from copy import copy

from vec2 import vec2

Colour = namedtuple('Colour', 'r,g,b')
Colour.copy = lambda self: copy(self)

black = Colour(0, 0, 0)
white = Colour(255, 255, 255)  # Colour ranges are not enforced.


class Bitmap():
    def __init__(self, width=40, height=40, background=white):
        assert width > 0 and height > 0 and type(background) == Colour
        self.width = width
        self.height = height
        self.background = background
        self.map = [[background.copy() for w in range(width)] for h in range(height)]

    def fillrect(self, x, y, width, height, colour=black):
        assert x >= 0 and y >= 0 and width > 0 and height > 0 and type(colour) == Colour
        for h in range(height):
            for w in range(width):
                self.map[y + h][x + w] = colour.copy()

    def chardisplay(self):
        txt = []
        for row in self.map:
            for bit in row:
                if bit == self.background:
                    txt += ' '
                else:
                    txt += '@'

        # Boxing
        txt = ['|' + row + '|' for row in txt]
        txt.insert(0, '+' + '-' * self.width + '+')
        txt.append('+' + '-' * self.width + '+')
        print('\n'.join(reversed(txt)))

    def set(self, x, y, colour=black):
        assert type(colour) == Colour
        try:
            self.map[y][x] = colour
        except:
            print("Err pos: ", [x, y])

    def set_symbol(self, x, y, symbol):
        try:
            self.map[y][x] = symbol
        except:
            print("Err pos: ", [x, y])

    def get(self, x, y):
        return self.map[y][x]


def line(x0, y0, x1, y1):
    "Bresenham's line algorithm"
    positions = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            positions.append([x, y])
            # self.set(x, y)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            positions.append([x, y])

            # self.set(x, y)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    positions.append([x, y])
    # print(positions)

    # self.set(x, y)
    return positions


# Bitmap.line = line
#
# bitmap = Bitmap(17, 17)
# # for points in ((1,8,8,16),(8,16,16,8),(16,8,8,1),(8,1,1,8)):
# #     bitmap.line(*points)
# # bitmap.line(0,0, 16, 1)
#
# for position in line(0, 0, 4, 8):
#     bitmap.set(position[0], position[1])
#     # print(position)
#
# bitmap.chardisplay()


def cubicbezier(x0, y0, x1, y1, x2, y2, x3, y3, n=20):
    line_pts = []
    pts = []
    for i in range(n + 1):
        t = i / n
        a = (1. - t) ** 3
        b = 3. * t * (1. - t) ** 2
        c = 3.0 * t ** 2 * (1.0 - t)
        d = t ** 3

        x = int(a * x0 + b * x1 + c * x2 + d * x3)
        y = int(a * y0 + b * y1 + c * y2 + d * y3)
        pts.append((x, y))

    for i in range(n):
        line_pts += line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])

    last_point = None
    filtered_line_pts = []
    for i in range(len(line_pts)):
        if last_point:
            if line_pts[i][0] != last_point[0] or line_pts[i][1] != last_point[1]:
                filtered_line_pts.append(line_pts[i])
        else:
            filtered_line_pts.append(line_pts[i])
        last_point = line_pts[i]

    # bitmap = Bitmap(60, 60)
    # # bitmap.cubicbezier(16, 1, 1, 4, 3, 16, 15, 11)
    # for position in filtered_line_pts:
    #     bitmap.set(position[0], position[1])
    #     # print(position)
    #
    # bitmap.chardisplay()

    return filtered_line_pts

# Bitmap.cubicbezier = cubicbezier
#
# bitmap = Bitmap(60, 60)
# # bitmap.cubicbezier(16, 1, 1, 4, 3, 16, 15, 11)
# for position in cubicbezier(8, 1, 16, 8, 17, 8, 8, 15):
#     bitmap.set(position[0], position[1])
#     # print(position)
#
# bitmap.chardisplay()

# bitmap = Bitmap(100, 100)
#
# a = vec2(0, 0)
# b = vec2(50, 50)
# # print(b)
# for i in range(0, 6):
#
#     b1 = b.alongAngle(math.pi/4, i)
#     bitmap.set(math.ceil(b1.x), math.ceil(b1.y))
# bitmap.chardisplay()
# cubicbezier(16, 1, 1, 4, 3, 16, 15, 11, 20)

#
# a = [[0,0], [0,4]]
# b = [[0,0]]
# print(not any(point in b for point in a))


# def find_path(from_pos, to_pos, max_attempt_count=20):
#     path_directions = None
#     original_path_points = line(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
#     path_points = original_path_points.copy()
#     path_midpoint = original_path_points[len(original_path_points) // 2]
#     path_angle = vec2(to_pos[0] - from_pos[0], to_pos[1] - from_pos[1]).angle() + math.pi / 2
#     isValid = is_path_blocked(path_points)
#     # for p in path_points:
#     #     bitmap.set(p[0], p[1])
#     # for i in range(0, 10):
#     #     curve_handle1 = vec2(*path_midpoint).alongAngle(path_angle, i)
#     #     curve_handle2 = vec2(*path_midpoint).alongAngle(path_angle, -i)
#     #
#     #     bitmap.set(round(curve_handle1.x), round(curve_handle1.y))
#     #     bitmap.set(round(curve_handle2.x), round(curve_handle2.y))
#
#     if not isValid:
#         print("PATH INVALID TRYING BEZIER CURVE")
#
#         attempt_count = 0
#         while not isValid and attempt_count <= max_attempt_count:
#             length = (-1 ** attempt_count) * attempt_count
#
#             for i in [-1, 1]:
#
#                 curve_handle1 = vec2(*path_midpoint).alongAngle(path_angle, i * length)
#                 curve_handle2 = vec2(*path_midpoint).alongAngle(path_angle, i * length)
#
#                 path_points = cubicbezier(from_pos[0], from_pos[1], round(curve_handle1.x), round(curve_handle1.y),
#                                           round(curve_handle2.x), round(curve_handle2.y), to_pos[0], to_pos[1])
#                 isValid = is_path_blocked(path_points)
#                 if isValid:
#                     break
#
#             attempt_count -= -1
#         if isValid:
#             path_directions = path_points  # get_directions_from_points(path_points)
#     else:
#         path_directions = None  # get_directions_from_points(path_points)
#     return path_directions
#
#
# def get_directions_from_points(points):
#     path_directions = []
#     last_point = None
#     for point in points:
#         if last_point:
#             direction = [point[0] - last_point[0], point[1] - last_point[1]]
#             path_directions.append(direction)
#         last_point = point
#
#     return path_directions
#
#
# def is_path_blocked(points):
#     print("checking path validity")
#     print("---------------------------")
#     print(points)
#     print(blocked_tiles)
#     print("---------------------------")
#     return not any(point in points for point in blocked_tiles) and all(
#         point[0] >= 0 and point[0] < 60 and point[1] >= 0 and point[1] < 60 for point in points)
#
#
# a = [8, 8]
# b = [20, 18]
# # blocked_tiles = [[10,10], [11,11], [9,8],[8,10],  [7,10]]
# # blocked_tiles = []
# blocked_tiles = line(0, 10, 21, 10) + line(0, 11, 21, 10)
#
# bitmap = Bitmap(60, 60)
# #
# for tile in blocked_tiles:
#     bitmap.set(tile[0], tile[1], colour=Colour(255, 0, 0))
#
# path = find_path(a, b, 20)
#
# for position in path:
#     bitmap.set(position[0], position[1])
#     print(position)
#
# bitmap.chardisplay()
