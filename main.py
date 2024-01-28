import pygame
import sys
import math
import numpy as np
"""
read graph.txt and parse them as nodes and leafs
read coords.txt to attach x and y coords to each main node

"""


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
        self.scale_x, self.scale_y, self.min_x, self.min_y = coordinate_scaling(self.coords_file)

        self._parse_graph_file()
        self._parse_coords_file()
        # self._calc_weights()

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


class Visualize:
    def __init__(self, _graph, width=800, height=800, background_color=(255, 255, 255), node_color=(0, 0, 255),
                 line_color=(140, 146, 172), text_color=(0, 0, 0)):
        self.graph = _graph
        self.width = width
        self.height = height
        self.background_color = background_color
        self.node_color = node_color
        self.line_color = line_color
        self.text_color = text_color

    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        # TODO: make font size dynamic to size of the graph
        font = pygame.font.Font(None, 36)
        clock = pygame.time.Clock()

        while True:
            screen.fill(self.background_color)
            # checking if window is closed or not
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # drawing nodes
            for node in self.graph.nodes:
                item = self.graph.nodes[f'{node}']

                # TODO: make circle size dynamic to size of graph
                pygame.draw.circle(screen, self.node_color,
                                   (item.x_placement, item.y_placement,), 20)
                # node_label = font.render(item.label, True, self.text_color)
                node_label = font.render(item.label, True, self.background_color)
                text_rect = node_label.get_rect(center=(item.x_placement, item.y_placement))
                screen.blit(node_label, text_rect.topleft)

            # drawing edges
            for edge in self.graph.edges:
                origin, destination = edge
                origin_node = self.graph.nodes[origin]
                destination_node = self.graph.nodes[destination]

                # drawing edge
                pygame.draw.line(screen, self.line_color,
                                 start_pos=(origin_node.x_placement, origin_node.y_placement),
                                 end_pos=(destination_node.x_placement, destination_node.y_placement))

                ed = euclidian_distance(origin_node.x, origin_node.y, destination_node.x, destination_node.y)
                mid_x, mid_y = midpoint(origin_node.x_placement, origin_node.y_placement,
                                        destination_node.x_placement, destination_node.y_placement)

                text_surface = font.render(f"{ed:.2f}", True, self.text_color)

                # Blit text onto the screen
                screen.blit(text_surface, (mid_x, mid_y))

            # update display
            pygame.display.flip()
            # Cap the frame rate
            clock.tick(60)


graph = Graph(graph_file="./graph.txt", coords_file="./coords.txt")
visualize = Visualize(_graph=graph)
visualize.start()
