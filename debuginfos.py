from collections import namedtuple
from copy import copy

Colour = namedtuple("Colour", "r,g,b")
Colour.copy = lambda self: copy(self)

black = Colour(0, 0, 0)
white = Colour(255, 255, 255)  # Colour ranges are not enforced.


class DebugMap:
    def __init__(self, width=60, height=60, background=white):
        self.width = width
        self.height = height
        self.background = background
        self.map = [[" " for w in range(width)] for h in range(height)]

    def chardisplay(self):
        txt = ""
        for i in range(self.height):
            for j in range(self.width):
                txt += self.map[i][j]
            txt += "\n"
        print(txt)

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


# debugmap.line = line
#
# bitmap = debugmap(17, 17)
# # for points in ((1,8,8,16),(8,16,16,8),(16,8,8,1),(8,1,1,8)):
# #     bitmap.line(*points)
# # bitmap.line(0,0, 16, 1)
#
# for position in line(0, 0, 4, 8):
#     bitmap.set(position[0], position[1])
#     # print(position)
#
# bitmap.chardisplay()


# debugmap.cubicbezier = cubicbezier
#
# bitmap = debugmap(60, 60)
# # bitmap.cubicbezier(16, 1, 1, 4, 3, 16, 15, 11)
# for position in cubicbezier(8, 1, 16, 8, 17, 8, 8, 15):
#     bitmap.set(position[0], position[1])
#     # print(position)
#
# bitmap.chardisplay()

# bitmap = debugmap(100, 100)
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
#     print("checking path.py validity")
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
bitmap = DebugMap(60, 60)
# #
# for tile in blocked_tiles:
#     bitmap.set(tile[0], tile[1], colour=Colour(255, 0, 0))
#
# path.py = find_path(a, b, 20)
#
# for position in path.py:
#     bitmap.set(position[0], position[1])
#     print(position)
#

bitmap.chardisplay()
