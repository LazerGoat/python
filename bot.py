import math

from game_message import Tick, Action, Spawn, Sail, Dock, Anchor, directions
from test import line, cubicbezier
from vec2 import vec2

class Bot:

    def __init__(self):
        print("Initializing your super mega duper bot")
        self.moving_to_port = False
        self.current_path = None
        self.target = [0, 0]
        self.current_position = [0, 0]
        self.last_position = None
        self.blocked_tiles = []
        self.free_tiles = []
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
            for y in range(len(tick.map.topology)):
                for x in range(len(tick.map.topology[y])):
                    if tick.map.topology[y][x] - tick.map.tideLevels.max > 0:
                        self.blocked_tiles.append([x, y])
                    if tick.map.topology[y][x] - tick.map.tideLevels.min < 0:
                        self.free_tiles.append([x, y])

            return Spawn(tick.map.ports[0])



        self.current_position = [tick.currentLocation.column, tick.currentLocation.row]

        if self.last_position:
            if self.moving_to_port:
                if self.current_position[0] != self.last_position[0] or self.current_position[1] != self.last_position[1]:
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

        map_ports = tick.map.ports.copy()
        values_to_remove = []
        for i in tick.visitedPortIndices:
            values_to_remove.append(map_ports[i])
        for v in values_to_remove:
            map_ports.remove(v)

        port_distances = {}
        for port_position in map_ports:
            port_distances[(port_position.column, port_position.row)] = abs(vec2(port_position.column - self.current_position[0], port_position.row - self.current_position[1]))
        print(port_distances)
        print("Moving: " + str(self.moving_to_port))
        print("Path: " + str(self.current_path))



        if self.spent_ticks >= 8 or self.return_home:
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
                max_attempts -= 1

            if self.moving_to_port:
                print("Moving to new port")
            else:
                print("No port found")
                print("Returning home at : ", self.first_dock)
                self.dock_home()
                return Sail(self.get_polar_direction(self.current_path[0]))
        else:
            if len(self.current_path) == 0:
                self.moving_to_port = False
                self.current_path = None
                self.spent_ticks = 0
                print("Docking at " + str(self.current_position))
                return Dock()
            else:
                return Sail(self.get_polar_direction(self.current_path[0]))

        return Anchor()

    def dock_home(self):
        print("Returning home at : ", self.first_dock)
        self.return_home = True
        self.moving_to_port = True
        self.current_path = self.find_path(self.current_position, self.first_dock)
        self.spent_ticks = 0

    def find_path(self, from_pos, to_pos, max_attempt_count=20):
        path_directions = None
        original_path_points = line(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
        path_points = original_path_points.copy()
        path_midpoint = original_path_points[len(original_path_points)//2]
        path_angle = vec2(*path_midpoint).angle() + math.pi/2
        isValid = self.is_path_blocked(path_points)
        if not isValid:
            print("PATH INVALID TRYING BEZIER CURVE")

            attempt_count = 0
            while not isValid and attempt_count <= max_attempt_count:
                length = -max_attempt_count ** max_attempt_count

                for i in [-1, 1]:
                    curve_handle1 = vec2(*path_midpoint).alongAngle(path_angle, i*length)
                    curve_handle2 = vec2(*path_midpoint).alongAngle(path_angle, i*length)
                    path_points = cubicbezier(from_pos[0], from_pos[1], curve_handle1.x, curve_handle1.y,
                                              curve_handle2.x, curve_handle2.y, to_pos[0], to_pos[1])
                    isValid = self.is_path_blocked(path_points)
                    if isValid:
                        break

                attempt_count -= -1
            if isValid:
                path_directions = self.get_directions_from_points(path_points)
        else:
            path_directions = self.get_directions_from_points(path_points)
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

    def is_path_blocked(self, points):
        return not any(point in points for point in self.blocked_tiles)


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
