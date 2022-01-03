"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
from math import sqrt
from types import SimpleNamespace
from client import Client
import json
from pygame import gfxdraw
import pygame
from pygame import *
from graph import Graph
from graph_algorithms import GraphAlgo

# init pygame
WIDTH, HEIGHT = 1080, 720

# default port
PORT = 6666
# server host (default localhost 127.0.0.1)
HOST = '127.0.0.1'
pygame.init()

screen = display.set_mode((WIDTH, HEIGHT), depth=32, flags=RESIZABLE)
clock = pygame.time.Clock()
pygame.font.init()

client = Client()
client.start_connection(HOST, PORT)

pokemons = client.get_pokemons()
pokemons_obj = json.loads(pokemons, object_hook=lambda d: SimpleNamespace(**d))

print(pokemons)

graph_json = client.get_graph()

FONT = pygame.font.SysFont('Arial', 20, bold=True)
# load the json string into SimpleNamespace Object

graph = json.loads(
    graph_json, object_hook=lambda json_dict: SimpleNamespace(**json_dict))

for n in graph.Nodes:
    x, y, _ = n.pos.split(',')
    n.pos = SimpleNamespace(x=float(x), y=float(y))

# get data proportions
min_x = min(list(graph.Nodes), key=lambda n: n.pos.x).pos.x
min_y = min(list(graph.Nodes), key=lambda n: n.pos.y).pos.y
max_x = max(list(graph.Nodes), key=lambda n: n.pos.x).pos.x
max_y = max(list(graph.Nodes), key=lambda n: n.pos.y).pos.y

g = Graph()
for n in graph.Nodes:
    g.add_node(n.id, n.pos)
for e in graph.Edges:
    g.add_edge(e.src, e.dest, e.w)
algo = GraphAlgo(g)


def scale(data, min_screen, max_screen, min_data, max_data):
    """
    get the scaled data with proportions min_data, max_data
    relative to min and max screen dimentions
    """
    return ((data - min_data) / (max_data - min_data)) * (max_screen - min_screen) + min_screen


# decorate scale with the correct values

def my_scale(data, x=False, y=False):
    if x:
        return scale(data, 50, screen.get_width() - 50, min_x, max_x)
    if y:
        return scale(data, 50, screen.get_height() - 50, min_y, max_y)


radius = 15

client.add_agent("{\"id\":0}")
# client.add_agent("{\"id\":1}")
# client.add_agent("{\"id\":2}")
# client.add_agent("{\"id\":3}")

# this commnad starts the server - the game is running now
client.start()

"""
The code below should be improved significantly:
The GUI and the "algo" are mixed - refactoring using MVC design pattern is required.
"""

while client.is_running() == 'true':
    pokemons = json.loads(client.get_pokemons(),
                          object_hook=lambda d: SimpleNamespace(**d)).Pokemons
    pokemons = [p.Pokemon for p in pokemons]
    for p in pokemons:
        x, y, _ = p.pos.split(',')
        p.pos = SimpleNamespace(x=my_scale(
            float(x), x=True), y=my_scale(float(y), y=True))
        p.real = SimpleNamespace(x=float(x), y=float(y))
    agents = json.loads(client.get_agents(),
                        object_hook=lambda d: SimpleNamespace(**d)).Agents
    agents = [agent.Agent for agent in agents]
    for a in agents:
        x, y, _ = a.pos.split(',')
        a.pos = SimpleNamespace(x=my_scale(
            float(x), x=True), y=my_scale(float(y), y=True))
    # check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

    # refresh surface
    screen.fill(Color(0, 0, 0))

    # draw nodes
    for n in graph.Nodes:
        x = my_scale(n.pos.x, x=True)
        y = my_scale(n.pos.y, y=True)

        # its just to get a nice antialiased circle
        gfxdraw.filled_circle(screen, int(x), int(y),
                              radius, Color(64, 80, 174))
        gfxdraw.aacircle(screen, int(x), int(y),
                         radius, Color(255, 255, 255))

        # draw the node id
        id_srf = FONT.render(str(n.id), True, Color(255, 255, 255))
        rect = id_srf.get_rect(center=(x, y))
        screen.blit(id_srf, rect)

    # draw edges
    for e in graph.Edges:
        # find the edge nodes
        src = next(n for n in graph.Nodes if n.id == e.src)
        dest = next(n for n in graph.Nodes if n.id == e.dest)

        # scaled positions
        src_x = my_scale(src.pos.x, x=True)
        src_y = my_scale(src.pos.y, y=True)
        dest_x = my_scale(dest.pos.x, x=True)
        dest_y = my_scale(dest.pos.y, y=True)

        # draw the line
        pygame.draw.line(screen, Color(61, 72, 126),
                         (src_x, src_y), (dest_x, dest_y))

        e.n_src = src
        e.n_dest = dest

    # draw agents
    for agent in agents:
        pygame.draw.circle(screen, Color(122, 61, 23),
                           (int(agent.pos.x), int(agent.pos.y)), 10)
    # draw pokemons (note: should differ (GUI wise) between the up and the down pokemons (currently they are marked
    # in the same way).

    for p in pokemons:
        pygame.draw.circle(screen, Color(0, 255, 255), (int(p.pos.x), int(p.pos.y)), 10)
        """
        if dest > src the pokemon will have an up arrow ↑ printed on it,
        to show that it goes from a low number to a higher number.
        if src > dest the pokemon will have a down arrow ↓ printed on it.
        uses the same lines of code used to print numbers onto the nodes.
        """
        if p.type > 0:
            symbol = "↑"
        elif p.type < 0:
            symbol = "↓"
        else:
            symbol = "?"  # will probably never happen, but just in case.

        id_srf = FONT.render(symbol, True, Color(0, 0, 0))
        rect = id_srf.get_rect(center=(p.pos.x, p.pos.y - 2))
        screen.blit(id_srf, rect)

    # update screen changes
    display.update()

    # refresh rate
    clock.tick(60)

    # find the closest edge to each pokemon:
    closest = []
    for p in pokemons:
        min_dist = float("inf")
        closest_edge = None
        for e in graph.Edges:
            # formula to calculate a distance from a point to a line (represented by 2 other points)
            dist = (abs((e.n_src.pos.x - e.n_dest.pos.x)*(e.n_dest.pos.y - p.real.y)
                        - (e.n_dest.pos.x - p.real.x)*(e.n_src.pos.y - e.n_dest.pos.y)))\
                   / (sqrt((e.n_src.pos.x - e.n_dest.pos.x) ** 2 + (e.n_src.pos.y - e.n_dest.pos.y) ** 2))
            if dist < min_dist:
                min_dist = dist
                closest_edge = e
        closest.append((p, closest_edge))

        # choose next edge
        for agent in agents:
            min_dist = float("inf")
            next_node = None
            for x in closest:
                if x[0].type > 0:
                    if x[1].n_src.id < x[1].n_dest.id:
                        dist, path = algo.shortest_path(agent.src, x[1].n_src.id)
                        dist += x[1].w
                        path.append(x[1].n_dest.id)
                    else:
                        dist, path = algo.shortest_path(agent.src, x[1].n_dest.id)
                        dist += x[1].w
                        path.append(x[1].n_src.id)
                else:
                    if x[1].n_src.id < x[1].n_dest.id:
                        dist, path = algo.shortest_path(agent.src, x[1].n_dest.id)
                        dist += x[1].w
                        path.append(x[1].n_src.id)
                    else:
                        dist, path = algo.shortest_path(agent.src, x[1].n_src.id)
                        dist += x[1].w
                        path.append(x[1].n_dest.id)
                if dist < min_dist:
                    min_dist = dist
                    next_node = path[1]

            if agent.dest == -1:
                print("Next node: ", next_node)
                client.choose_next_edge(
                    '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(next_node) + '}')
                ttl = client.time_to_end()
                # print(ttl, client.get_info())

    client.move()
# game over:
