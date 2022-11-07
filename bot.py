import math

from game_message import Tick, Action, Spawn, Sail, Dock, Anchor, directions
from test import line, cubicbezier, Bitmap
from vec2 import vec2


class Bot:

    def __init__(self):
        print("Initializing your super mega duper bot")
        self.moving_to_port = False
        self.current_path = None
        self.target_port = [0, 0]
        self.current_position = [0, 0]
        self.last_position = None

        self.blocked_tiles = []
        self.free_tiles = []
        self.topology = []
        self.map_size = [0, 0]
        self.current_tide = 0

        self.docked_at_spawn = False
        self.spent_ticks = 0
        self.first_dock = None
        self.return_home = False
        self.stuck = False

    def get_next_move(self, tick: Tick) -> Action:
        """
        Here is where the magic happens, for now the move is random. I bet you can do better ;)
        """
        print()
        print()

        if tick.currentLocation is None:
            print(tick.map.topology)
            print(tick.map.tideLevels)
            for y in range(len(tick.map.topology)):
                for x in range(len(tick.map.topology[y])):
                    if tick.map.topology[y][x] >= (tick.map.tideLevels.min + tick.map.tideLevels.max) // 2:
                        print([x, y], " : ", tick.map.topology[y][x])
                        self.blocked_tiles.append([x, y])
                    if tick.map.topology[y][x] < tick.map.tideLevels.min:
                        self.free_tiles.append([x, y])

            self.topology = tick.map.topology
            self.map_size = [len(tick.map.topology[0]), len(tick.map.topology)]
            return Spawn(tick.map.ports[0])

        self.current_tide = tick.tideSchedule[0]
        self.current_position = [tick.currentLocation.column, tick.currentLocation.row]

        if self.last_position:
            if self.moving_to_port:
                if self.current_position[0] != self.last_position[0] or self.current_position[1] != self.last_position[
                    1]:
                    self.current_path.pop(0)
                    self.stuck = False
                    self.spent_ticks = max(self.spent_ticks - 1, 0)
                else:
                    self.spent_ticks += 1
                    self.stuck = True

        self.last_position = self.current_position
        if not self.docked_at_spawn:
            print("Docking at " + str(self.current_position))
            self.docked_at_spawn = True
            self.first_dock = self.current_position
            return Dock()

        # t = tick
        # tick.map.topology = []
        # print(t)
        print("Current position : " + str(self.current_position))

        map_ports = tick.map.ports
        values_to_remove = []
        for i in tick.visitedPortIndices:
            values_to_remove.append(map_ports[i])
        for v in values_to_remove:
            map_ports.remove(v)

        port_distances = {}
        for port_position in map_ports:
            port_distances[(port_position.column, port_position.row)] = abs(
                vec2(port_position.column - self.current_position[0], port_position.row - self.current_position[1]))
        print(port_distances)
        print("Moving: " + str(self.moving_to_port))
        # print("Path: " + str(self.current_path))

        if self.spent_ticks >= 12 or self.return_home:
            self.dock_home()

        if not self.moving_to_port:
            max_attempts = len(port_distances)
            while not self.moving_to_port and max_attempts > 0:
                nearest_port = min(port_distances, key=port_distances.get)
                port_distances.pop(nearest_port)
                path = self.find_path(self.current_position, list(nearest_port))
                if path is not None:
                    self.moving_to_port = True
                    self.current_path = path
                    self.target_port = list(nearest_port)
                max_attempts -= 1

            if self.moving_to_port:
                print("Moving to new port")
            else:
                print("No port found")
                self.dock_home()
                return Sail(self.get_polar_direction(self.current_path[0]))

        if self.moving_to_port:
            if len(self.current_path) == 0:
                self.moving_to_port = False
                self.current_path = None
                self.spent_ticks = 0
                print("Docking at " + str(self.current_position))
                return Dock()
            else:

                path = self.find_path(self.current_position, self.target_port)
                if path is not None:
                    self.current_path = path
                else:
                    print("No path found ( I'm stuck :( )")
                    return Anchor()

                return Sail(self.get_polar_direction(self.current_path[0]))

        return Anchor()

    def dock_home(self):
        print("Returning home at : ", self.first_dock)
        self.return_home = True
        self.moving_to_port = True
        self.target_port = self.first_dock
        self.current_path = self.find_path(self.current_position, self.first_dock, max_attempt_count=30)
        self.spent_ticks = 0

    def find_path(self, from_pos, to_pos, max_attempt_count=20):
        path_directions = None
        original_path_points = line(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
        path_points = original_path_points.copy()
        path_midpoint = original_path_points[len(original_path_points) // 2]
        path_angle = vec2(to_pos[0] - from_pos[0], to_pos[1] - from_pos[1]).angle() + math.pi / 2
        isValid = self.is_path_valid(path_points)
        if not isValid:
            print("PATH INVALID TRYING BEZIER CURVE")

            attempt_count = 0
            while not isValid and attempt_count <= max_attempt_count:
                length = (-1 ** attempt_count) * attempt_count

                for i in [-1, 1]:
                    curve_handle1 = vec2(*path_midpoint).alongAngle(path_angle, i * length)
                    curve_handle2 = vec2(*path_midpoint).alongAngle(path_angle, i * length)
                    path_points = cubicbezier(from_pos[0], from_pos[1], curve_handle1.x, curve_handle1.y,
                                              curve_handle2.x, curve_handle2.y, to_pos[0], to_pos[1])
                    isValid = self.is_path_valid(path_points)
                    if isValid:
                        path_directions = self.get_directions_from_points(path_points)
                        break
                attempt_count -= -1

            if not isValid:
                path_directions = self.get_directions_from_points(original_path_points)
        else:
            path_directions = self.get_directions_from_points(path_points)

        print("Selected path:")
        bitmap = Bitmap(self.map_size[0], self.map_size[1])
        # bitmap.cubicbezier(16, 1, 1, 4, 3, 16, 15, 11)
        for p in path_points:
            bitmap.set(p[0], self.map_size[1] - p[1])
            # print(position)
        for tile in self.blocked_tiles:
            bitmap.set_symbol(tile[0], self.map_size[1] - tile[1], 'X')

        bitmap.set_symbol(self.current_position[0], self.map_size[1] - self.current_position[1], '0')

        bitmap.chardisplay()

        print("Path: ", path_directions)

        return path_directions

    def get_directions_from_points(self, points):
        path_directions = []
        last_point = None
        for point in points:
            if last_point:
                direction = [point[0] - last_point[0], point[1] - last_point[1]]
                path_directions.append(direction)
            last_point = point

        return path_directions

    def is_path_valid(self, points):
        print("checking path validity")
        # print("---------------------------")
        # print(points)
        # print(self.blocked_tiles)
        # print("---------------------------")

        if not all(0 <= point[0] < self.map_size[0] and 0 <= point[1] < self.map_size[1] for point in points):
            return False

        valid = True
        for p in points:
            if self.topology[p[1]][p[0]] >= self.current_tide:
                valid = False
                break

        return valid

        # return not any(point in points for point in self.blocked_tiles) and all(
        #     point[0] >= 0 and point[0] < self.map_size[0] and point[1] >= 0 and point[1] < self.map_size[1] for point in
        #     points)

    def get_polar_direction(self, vector_dir):
        h = ""
        v = ""
        if vector_dir[0] > 0:
            h = "E"
        elif vector_dir[0] < 0:
            h = "W"

        if vector_dir[1] > 0:
            v = "S"
        elif vector_dir[1] < 0:
            v = "N"

        return v + h
