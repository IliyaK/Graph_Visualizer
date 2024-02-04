import pygame
import sys
import math
import numpy as np
from itertools import permutations


def euclidian_distance(x, y, x2, y2):
    return math.sqrt((x2-x)**2 + (y2-y)**2)


def midpoint(x, y, x2, y2):
    return (x2+x)/2, (y2+y)/2


def coordinate_scaling(coordinate_file):
    with open(coordinate_file, "r") as fout:
        _graph = fout.read()
    _graph = _graph.split("\n")
    xs = []
    ys = []
    for i in _graph:
        i = i.split(" ")
        xs.append(float(i[1]))
        ys.append(float(i[2]))
    # TODO: make safety_border adjustable variable
    safety_border = 20
    max_x, min_x = max(xs), min(xs)
    max_y, min_y = max(ys), min(ys)
    min_x -= safety_border
    max_x += safety_border
    min_y -= safety_border
    max_y += safety_border
    # TODO: make these numbers consistent with what Visualizer() is using
    return 800/(max_x - min_x), 800/(max_y - min_y), min_x, min_y


class Node:
    def __init__(self):
        self.label = ""
        self.x = 0.0
        self.y = 0.0
        self.parent = None
        self.isBlocked = False
        self.x_placement = 0.0
        self.y_placement = 0.0
        self.distance_to_goal = 0.0
        self.leafs = []
        self.weights = []


class Graph:
    def __init__(self, graph_file, coords_file):
        self.graph_file = graph_file
        self.coords_file = coords_file
        self.nodes = {}
        self.edges = []
        self.weights = []
        # linking edges to weights
        self.link = {}
        self.scale_x, self.scale_y, self.min_x, self.min_y = coordinate_scaling(self.coords_file)

        self._parse_graph_file()
        self._parse_coords_file()
        self._calc_weights()
        self._link()

    def _parse_graph_file(self):
        with open(self.graph_file, "r") as fout:
            _graph = fout.read()
        _graph = _graph.split("\n")

        for i in _graph:
            i = i.split(" ")
            self.nodes[f"{i[0]}"] = Node()
            self.nodes[f"{i[0]}"].label = f"{i[0]}"
            for j in i[1:]:
                self.edges.append((i[0], j))
                self.nodes[f"{i[0]}"].leafs.append(j)

        # removing duplicates from edge list
        np.unique(self.edges)

    def _parse_coords_file(self):
        with open(self.coords_file, "r") as fout:
            _graph = fout.read()
        _graph = _graph.split("\n")

        for i in _graph:
            i = i.split(" ")
            self.nodes[f"{i[0]}"].x_placement = (float(i[1])-self.min_x)*self.scale_x
            self.nodes[f"{i[0]}"].x = float(i[1])
            self.nodes[f"{i[0]}"].y_placement = (float(i[2])-self.min_y)*self.scale_y
            self.nodes[f"{i[0]}"].y = float(i[2])

    def _calc_weights(self):
        for edge in self.edges:
            origin_x, origin_y = self.nodes[edge[0]].x, self.nodes[edge[0]].y
            destination_x, destination_y = self.nodes[edge[1]].x, self.nodes[edge[1]].y
            self.weights.append(euclidian_distance(origin_x, origin_y, destination_x, destination_y))

    def _link(self):
        for pos, edge in enumerate(self.edges):
            self.link[f"{edge[0]},{edge[1]}"] = self.weights[pos]

    def _calc_to_dest(self, destination):
        destination_x, destination_y = self.nodes[destination].x, self.nodes[destination].y
        for node in self.nodes:
            self.nodes[node].distance_to_goal = euclidian_distance(self.nodes[node].x, self.nodes[node].y, destination_x, destination_y)

    def _blocked_setup(self, blocks):
        if blocks:
            for node in self.nodes:
                if self.nodes[node].label in blocks:
                    self.nodes[node].isBlocked = True

    def a_star(self, origin, destination, blocks=None):
        self._calc_to_dest(destination)

        self._blocked_setup(blocks)

        start = self.nodes[origin]
        visited_nodes = []
        unseen_nodes = {start.label: start}

        g_value = {start.label: 0.0}
        f_value = {start.label: start.distance_to_goal}

        while len(unseen_nodes) != 0:

            if start.label == destination:
                return self.make_path(start.label)

            neighbors = [edge for edge in self.edges if edge[0] == start.label]

            visited_nodes.append(start.label)
            unseen_nodes.pop(start.label)

            for neighbor in neighbors:
                if neighbor[1] in visited_nodes:
                    continue

                if self.nodes[neighbor[1]].isBlocked:
                    continue

                temp_g_value = g_value[neighbor[0]] + self.link[f"{neighbor[0]},{neighbor[1]}"]

                if neighbor[1] not in unseen_nodes.keys():
                    unseen_nodes[neighbor[1]] = self.nodes[neighbor[1]]

                elif temp_g_value >= unseen_nodes[neighbor[1]].distance_to_goal:
                    continue

                unseen_nodes[neighbor[1]].parent = start
                g_value[neighbor[1]] = temp_g_value
                f_value[neighbor[1]] = temp_g_value + self.nodes[neighbor[1]].distance_to_goal

            try:
                vals = []
                nds = list(unseen_nodes.keys())
                for node in unseen_nodes:
                    vals.append(f_value[node])

                start = self.nodes[nds[vals.index(min(vals))]]
            except ValueError:
                return "NOT POSSIBLE"

        return "NOT POSSIBLE"

    def make_path(self, destination):
        nodes = []
        while self.nodes[destination].parent:
            nodes.append(destination)
            destination = self.nodes[destination].parent.label
        nodes.append(destination)
        # print(nodes)
        # print(nodes[::-1])
        return nodes[::-1]


class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.clicked = False
        self.rect = pygame.Rect(x, y, width, height)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # negating current state of clicked
                self.clicked = not self.clicked

    def draw(self, screen, font, background_color, text_color):
        pygame.draw.rect(screen, background_color, self.rect)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class NodeButtons:
    number_of_starts = 0
    number_of_ends = 0

    def __init__(self, text, x, y, r):
        self.states = ["Base", "Start", "Finish", "Blocked"]
        self.colors = {
            "Base": (0, 0, 255),
            "Start": (0, 255, 0),
            "Finish": (255, 0, 0),
            "Blocked": (0, 0, 0)
        }
        self.state = 0
        self.text = text
        self.clicked = False
        self.radius = r
        self.x = x
        self.y = y

    def draw(self, screen, font):
        pygame.draw.circle(screen, self.colors[self.states[self.state]], (self.x, self.y), self.radius)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)

    def event(self, event, start, finish):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            distance = ((mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2) ** 0.5
            if distance <= self.radius:
                """
                0 - base node
                1 - start node
                2 - finish node
                3 - blocked
                """
                self.state += 1
                if start:
                    if self.state == 1:
                        self.state += 1
                if finish:
                    if self.state == 2:
                        self.state += 1

                if self.state > 3:
                    self.state = 0
                return self.state


class Visualize:
    def __init__(self, _graph, start_node=None, end_node=None, blocks=None, width=800, height=800,
                 background_color=(255, 255, 255), node_color=(0, 0, 255),
                 line_color=(140, 146, 172), text_color=(0, 0, 0)):
        self.graph = _graph
        self.width = width
        self.height = height
        self.background_color = background_color
        self.node_color = node_color
        self.line_color = line_color
        self.text_color = text_color

        self.start_node = start_node
        self.end_node = end_node
        if blocks:
            self.blocks = blocks
        else:
            self.blocks = []
        self.messages = {
            "solution": "No Solution",
        }
        self.solution = []

        self.start_button = Button("Solve", 10, 40, 70, 30)
        self.node_buttons = []

    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        # TODO: make font size dynamic to size of the graph
        font = pygame.font.Font(None, 36)
        clock = pygame.time.Clock()

        # establishing nodes
        for node in self.graph.nodes:
            item = self.graph.nodes[f'{node}']
            self.node_buttons.append(NodeButtons(text=item.label, x=item.x_placement, y=item.y_placement, r=20))

        while True:
            screen.fill(self.background_color)
            # checking if window is closed or not
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.start_button.event(event)

                for node in self.node_buttons:
                    act = node.event(event, self.start_node, self.end_node)
                    item = self.graph.nodes[f'{node.text}']
                    # base node
                    if act == 0:
                        if self.end_node == item.label:
                            self.end_node = None
                        if self.start_node == item.label:
                            self.start_node = None
                        if item.label in self.blocks:
                            self.blocks.remove(item.label)
                            item.isBlocked = False

                    # start node
                    if act == 1:
                        self.start_node = item.label
                        if self.end_node == item.label:
                            self.end_node = None
                        if item.label in self.blocks:
                            self.blocks.remove(item.label)
                            item.isBlocked = False

                    # finish node
                    elif act == 2:
                        self.end_node = item.label
                        if self.start_node == item.label:
                            self.start_node = None
                        if item.label in self.blocks:
                            self.blocks.remove(item.label)
                            item.isBlocked = False

                    # blocked node
                    elif act == 3:
                        if self.start_node == item.label:
                            self.start_node = None
                        if self.end_node == item.label:
                            self.end_node = None

                        if self.blocks:
                            self.blocks.append(item.label)
                        else:
                            self.blocks = [item.label]

            # drawing nodes
            for node in self.node_buttons:
                node.draw(screen, font)

            # TODO: simplify edges
            for edge in self.graph.edges:
                origin, destination = edge
                origin_node = self.graph.nodes[origin]
                destination_node = self.graph.nodes[destination]
                if edge in self.solution:
                    # drawing edge
                    pygame.draw.line(screen, (0, 255, 0),
                                     start_pos=(origin_node.x_placement, origin_node.y_placement),
                                     end_pos=(destination_node.x_placement, destination_node.y_placement), width=5)
                # drawing edge
                pygame.draw.line(screen, self.line_color,
                                 start_pos=(origin_node.x_placement, origin_node.y_placement),
                                 end_pos=(destination_node.x_placement, destination_node.y_placement))

                # ed = euclidian_distance(origin_node.x, origin_node.y, destination_node.x, destination_node.y)
                mid_x, mid_y = midpoint(origin_node.x_placement, origin_node.y_placement,
                                        destination_node.x_placement, destination_node.y_placement)

                # text_surface = font.render(f"{ed:.2f}", True, self.text_color)
                text_surface = font.render(f'{self.graph.link[f"{origin_node.label},{destination_node.label}"]:.2f}', True, self.text_color)

                # Blit text onto the screen
                screen.blit(text_surface, (mid_x, mid_y))

            # messages
            dynamic_text = font.render(f"Solution: {self.messages['solution']}", True, self.text_color)
            text_rect = dynamic_text.get_rect()
            text_rect.topleft = (10, 10)
            screen.blit(dynamic_text, text_rect)

            # buttons
            self.start_button.draw(screen, font, self.background_color, self.text_color)

            # button actions
            if self.start_button.clicked:
                if self.end_node and self.start_node:
                    solution = self.graph.a_star(self.start_node, self.end_node, blocks=self.blocks)
                    self.messages['solution'] = solution
                    if type(solution) is list:
                        self.solution = list(permutations(solution, 2))
                    for node in self.graph.nodes:
                        self.graph.nodes[node].parent = None
                self.start_button.clicked = False

            # update display
            pygame.display.flip()
            # Cap the frame rate
            clock.tick(3)

graph = Graph(graph_file="./graph2.txt", coords_file="./coords2.txt")
# print(graph.a_star("4", "1", blocks=["2", "7", "6"]))


visualize = Visualize(_graph=graph)
visualize.start()
