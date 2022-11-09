import math
from typing import Union

from debuginfos import DebugMap
from game_message import Tick, Action, Spawn, Sail, Dock, Anchor
from path import Path
from vec2 import vec2


def get_polar_direction(vector_dir):
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


class Bot:
    def __init__(self):
        self.ports = None
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
                    if (
                            tick.map.topology[y][x]
                            >= (tick.map.tideLevels.min + tick.map.tideLevels.max) // 2
                    ):
                        print([x, y], " : ", tick.map.topology[y][x])
                        self.blocked_tiles.append([x, y])
                    if tick.map.topology[y][x] < tick.map.tideLevels.min:
                        self.free_tiles.append([x, y])
            self.ports = tick.map.ports
            self.topology = tick.map.topology
            self.map_size = [len(tick.map.topology[0]), len(tick.map.topology)]
            return self.return_move(Spawn(tick.map.ports[0]))

        self.current_tide = tick.tideSchedule[
            0
        ]  # min(tick.tideSchedule[2], (tick.map.tideLevels.min + tick.map.tideLevels.max) // 2)
        self.current_position = [tick.currentLocation.column, tick.currentLocation.row]

        if self.last_position:
            if self.moving_to_port:
                if (
                        self.current_position[0] != self.last_position[0]
                        or self.current_position[1] != self.last_position[1]
                ):
                    self.current_path.pop(0)
                    self.stuck = False
                    self.spent_ticks = max(self.spent_ticks - 2, 0)
                else:
                    self.spent_ticks += 1
                    self.stuck = True

        self.last_position = self.current_position

        if not self.first_dock:
            self.first_dock = self.current_position
            return self.return_move(Dock())

        self.blocked_tiles = []
        for y in range(len(tick.map.topology)):
            for x in range(len(tick.map.topology[y])):
                if tick.map.topology[y][x] >= tick.tideSchedule[0]:
                    self.blocked_tiles.append([x, y])

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
                vec2(
                    port_position.column - self.current_position[0],
                    port_position.row - self.current_position[1],
                )
            )
        print(port_distances)

        # print("Moving: " + str(self.moving_to_port))
        # print("path.py: " + str(self.current_path))

        if self.spent_ticks >= 400 or self.return_home:
            self.dock_home()

        if self.spent_ticks >= 12:
            self.moving_to_port = False
            self.current_path = None
            self.spent_ticks = 0
            port_distances.pop(tuple(self.target_port))

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
                print("Moving to new port: ", self.target_port)
            else:
                print("No port found")
                self.dock_home()
                return self.return_move(Sail(get_polar_direction(self.current_path[0])))

        if self.moving_to_port:
            if len(self.current_path) == 0:
                self.moving_to_port = False
                self.current_path = None
                self.spent_ticks = 0
                return self.return_move(Dock())
            else:

                path = self.find_path(self.current_position, self.target_port)
                if path is not None:
                    self.current_path = path
                else:
                    print("No path.py found ( I'm stuck :( )")
                    return self.return_move(Anchor())

                return self.return_move(Sail(get_polar_direction(self.current_path[0])))

        return self.return_move(Anchor())

    def return_move(self, move: Union[Sail, Dock, Anchor, Spawn]):
        print("Move: ", move)
        if type(move) is Sail:
            print("Moving to: ", Sail(move).direction)
        elif type(move) is Dock:
            print("Docking at: ", self.current_position)
        elif type(move) is Anchor:
            print("Anchoring at: ", self.current_position)
        elif type(move) is Spawn:
            print("Init position at: ", [move.position.column, move.position.row])
        return move

    def dock_home(self):
        print("Returning home at : ", self.first_dock)
        self.return_home = True
        self.moving_to_port = True
        self.target_port = self.first_dock
        self.current_path = self.find_path(
            self.current_position, self.first_dock, max_overreach=30
        )
        self.spent_ticks = 0

    def find_path(self, from_pos, to_pos, max_overreach=20):
        path = Path.from_line(from_pos, to_pos)
        distance = round(
            vec2.distance_to(vec2(to_pos[0], to_pos[1]), vec2(from_pos[0], from_pos[1]))
        )
        path_midpoint = path.points[len(path.points) // 2]
        path_angle = (
                vec2(to_pos[0] - from_pos[0], to_pos[1] - from_pos[1]).angle() + math.pi / 2
        )

        is_valid = self.is_path_valid(path)
        if not is_valid:
            print("PATH INVALID TRYING BEZIER CURVE")
            attempt_count = 0
            for i in range(max_overreach):
                perp_length = (-(1 ** i)) * i
                for parallel_length in range((distance // 2) + 10):
                    for perp_sign in [-1, 1]:
                        for parallel_sign in [-1, 1]:

                            if is_valid:
                                path = curve_path
                                break

                            curve_handle1 = (
                                vec2(*path_midpoint)
                                .alongAngle(path_angle, perp_sign * perp_length)
                                .alongAngle(
                                    path_angle - math.pi / 2,
                                    parallel_sign * parallel_length,
                                )
                            )
                            # curve_handle2 = vec2(*path_midpoint).alongAngle(path_angle, perp_sign * perp_length)
                            curve_path = Path.from_curve(
                                from_pos, to_pos, [curve_handle1.x, curve_handle1.y]
                            )
                            is_valid = self.is_path_valid(curve_path)
                            attempt_count -= -1
            print("Found valid path.py after ", attempt_count, " curve attempts.")

        self.update_debug_map(path.points)

        print("path.py: ", path.directions)

        return path.directions

    def update_debug_map(self, path_points):
        print("Selected path.py : ")
        debug_map = DebugMap(self.map_size[0], self.map_size[1])
        # debug_map.cubicbezier(16, 1, 1, 4, 3, 16, 15, 11)
        for p in path_points:
            debug_map.set_symbol(p[0], p[1], "*")
            # print(position)
        for tile in self.blocked_tiles:
            debug_map.set_symbol(tile[0], tile[1], "█")
        for port in self.ports:
            debug_map.set_symbol(port.column, port.row, "P")

        debug_map.set_symbol(self.current_position[0], self.current_position[1], "@")
        debug_map.set_symbol(self.target_port[0], self.target_port[1], "!")
        debug_map.chardisplay()

    def is_path_valid(self, path: Path):
        # print("---------------------------")
        # print(points)
        # print(self.blocked_tiles)
        # print("---------------------------")

        if not all(
                0 <= point[0] < self.map_size[0] and 0 <= point[1] < self.map_size[1]
                for point in path.points
        ):
            return False

        valid = True
        for p in path.points:
            if self.topology[p[1]][p[0]] >= self.current_tide:
                valid = False
                break

        return valid

        # return not any(point in points for point in self.blocked_tiles) and all(
        #     point[0] >= 0 and point[0] < self.map_size[0] and point[1] >= 0 and point[1] < self.map_size[1] for point in
        #     points)
