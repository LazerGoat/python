from typing import Any


class Path:
    points = None
    current_step = None

    def __init__(self, path_points: list):
        self.points = path_points
        self.directions = self.get_directions_from_points(self.points)
        self.start = path_points[0]
        self.end = path_points[-1]
        self.current_step = 0

    @classmethod
    def from_line(cls, _from: list, _to: list):
        return cls(cls.line(_from[0], _from[1], _to[0], _to[1]))

    @classmethod
    def len(cls):
        return len(cls.points)

    @classmethod
    def from_curve(cls, _from: list, _to: list, _curve_vec: list):
        return cls(
            cls.cubicbezier(
                _from[0],
                _from[1],
                _curve_vec[0],
                _curve_vec[1],
                _curve_vec[0],
                _curve_vec[1],
                _to[0],
                _to[1],
            )
        )

    @classmethod
    def get_next_step(cls):
        if len(cls) >= cls.current_step + 2:
            current_point = cls.points[cls.current_step]
            next_point = cls.points[cls.current_step + 1]

            direction = [
                next_point[0] - current_point[0],
                next_point[1] - current_point[1],
            ]
        return direction

    @classmethod
    def advance(cls):
        if len(cls) >= cls.current_step + 1:
            cls.current_step += 1

    def __len__(self):
        return len(self.points)

    @classmethod
    def get_directions_from_points(cls, points):
        path_directions: list[list[Any]] = []
        last_point = None
        for point in points:
            if last_point:
                direction = [point[0] - last_point[0], point[1] - last_point[1]]
                path_directions.append(direction)
            last_point = point

        return path_directions

    @classmethod
    def cubicbezier(cls, x0, y0, x1, y1, x2, y2, x3, y3, n=20):
        line_pts = []
        pts = []
        for i in range(n + 1):
            t = i / n
            a = (1.0 - t) ** 3
            b = 3.0 * t * (1.0 - t) ** 2
            c = 3.0 * t ** 2 * (1.0 - t)
            d = t ** 3

            x = int(a * x0 + b * x1 + c * x2 + d * x3)
            y = int(a * y0 + b * y1 + c * y2 + d * y3)
            pts.append((x, y))

        for i in range(n):
            line_pts += cls.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])

        last_point = None
        filtered_line_pts = []
        for i in range(len(line_pts)):
            if last_point:
                if line_pts[i][0] != last_point[0] or line_pts[i][1] != last_point[1]:
                    filtered_line_pts.append(line_pts[i])
            else:
                filtered_line_pts.append(line_pts[i])
            last_point = line_pts[i]

        # bitmap = debugmap(60, 60)
        # # bitmap.cubicbezier(16, 1, 1, 4, 3, 16, 15, 11)
        # for position in filtered_line_pts:
        #     bitmap.set(position[0], position[1])
        #     # print(position)
        #
        # bitmap.chardisplay()

        return filtered_line_pts

    @classmethod
    def line(cls, x0, y0, x1, y1):
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
