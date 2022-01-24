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
from threading import Thread
import time

# init pygame
WIDTH, HEIGHT = 1080, 720

# default port
PORT = 6666
# server host (default localhost 127.0.0.1)
HOST = '127.0.0.1'

client = Client()
connected = False
while not connected:
    try:
        client.start_connection(HOST, PORT)
        connected = True
    except ConnectionRefusedError:
        print("Waiting for Server")

pygame.init()

screen = display.set_mode((WIDTH, HEIGHT), depth=32, flags=RESIZABLE)
clock = pygame.time.Clock()
pygame.font.init()

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


def calc_time_path(p, close_edge, source, speed):
    if p.type > 0:
        if close_edge.n_src.id < close_edge.n_dest.id:
            dist, path = algo.shortest_path(source, close_edge.n_src.id)
            dist += close_edge.w/2  # approximately the middle of the edge
            path.append(close_edge.n_dest.id)
        else:
            dist, path = algo.shortest_path(source, close_edge.n_dest.id)
            dist += close_edge.w/2
            path.append(close_edge.n_src.id)
    else:
        if close_edge.n_src.id < close_edge.n_dest.id:
            dist, path = algo.shortest_path(source, close_edge.n_dest.id)
            dist += close_edge.w/2
            path.append(close_edge.n_src.id)
        else:
            dist, path = algo.shortest_path(source, close_edge.n_src.id)
            dist += close_edge.w/2
            path.append(close_edge.n_dest.id)
    return dist/speed, path

radius = 15

client.add_agent("{\"id\":0}")
client.add_agent("{\"id\":1}")
client.add_agent("{\"id\":2}")
client.add_agent("{\"id\":3}")

# this commnad starts the server - the game is running now
client.start()

"""
The code below should be improved significantly:
The GUI and the "algo" are mixed - refactoring using MVC design pattern is required.
"""

previous_time = -1
moves = 0

try:
    while client.is_running() == 'true':
        pokemons = json.loads(client.get_pokemons(),
                              object_hook=lambda d: SimpleNamespace(**d)).Pokemons
        pokemons = [p.Pokemon for p in pokemons]

        i = 0
        for p in pokemons:
            p.id = i
            i += 1
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if 0 < pos[0] < 100 and 0 < pos[1] < 50:  # check if the stop button was pressed
                    pygame.quit()
                    exit(0)

        # refresh surface
        screen.fill(Color(0, 0, 0))

        # draw "stop" button
        rect = pygame.draw.rect(screen, (255, 0, 0), (5, 5, 90, 40), 0)
        screen.blit(FONT.render("S T O P", True, (255, 255, 255)), (18, 14))

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

            text = FONT.render(str(agent.id), True, Color(255, 255, 255))
            rect = text.get_rect(center=(agent.pos.x - 1, agent.pos.y - 1))
            screen.blit(text, rect)
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

            text = FONT.render(symbol, True, Color(0, 0, 0))
            rect = text.get_rect(center=(p.pos.x, p.pos.y - 2))
            screen.blit(text, rect)

            text = FONT.render(str(p.value), True, Color(255, 255, 255))
            rect = text.get_rect(center=(p.pos.x, p.pos.y - 20))
            screen.blit(text, rect)

        # refresh rate
        clock.tick(60)

        # find the closest edge to each pokemon:
        closest = {}
        for p in pokemons:
            min_dist = float("inf")
            closest_edge = None
            for e in graph.Edges:
                # formula to calculate a distance from a point to a line (represented by 2 other points)
                dist = (abs((e.n_src.pos.x - e.n_dest.pos.x) * (e.n_dest.pos.y - p.real.y)
                            - (e.n_dest.pos.x - p.real.x) * (e.n_src.pos.y - e.n_dest.pos.y))) \
                       / (sqrt((e.n_src.pos.x - e.n_dest.pos.x) ** 2 + (e.n_src.pos.y - e.n_dest.pos.y) ** 2))
                if dist < min_dist:
                    min_dist = dist
                    closest_edge = e
            closest[p.id] = (p, closest_edge)

        times = {}  # {pokemon id: {agent: [time_to_reach, next_node, speed] ...}
        # choose next edge
        for agent in agents:
            if len(closest) > 0:
                for i, x in closest.items():
                    dist, path = calc_time_path(x[0], x[1], agent.src, agent.speed)
                    if i not in times.keys():
                        times[i] = {}
                    times[i][agent.id] = [dist, path[1:], agent.speed]

        # assert each pokemon an agent
        next_nodes = {}
        while times:
            min_time = float("inf")
            pokemon = list(times.keys())[0]
            agent = list(list(times.values())[0].keys())[0]
            for p, a_dic in times.items():
                for a, v in a_dic.items():
                    if v[0] < min_time:
                        min_time = v[0]
                        agent = a
                        pokemon = p
            temp = times.pop(pokemon)
            time_to_reach, next_node, speed = temp[agent]
            if agent not in list(next_nodes.keys()):
                next_nodes[agent] = next_node
            for k, v in times.items():
                dist, path = calc_time_path(closest[pokemon][0], closest[pokemon][1], next_node[-1], speed)
                v[agent][0] += dist
                v[agent][1] += path[1:]

        for agent in agents:
            for p in pokemons:
                if abs(agent.pos.x - p.pos.x) < 1 and abs(agent.pos.y - p.pos.y) < 1:
                    print(p.id, "Pokemon Got!")
            if agent.id not in list(next_nodes.keys()):
                # if the agent will not reach any pokemon faster than other agents
                next_nodes[agent.id] = [agent.src]  # stay in place
            screen.blit(FONT.render(str(agent.id) + " → " + str(next_nodes[agent.id][-1]), True, (255, 255, 255)),
                        (WIDTH - 100, agent.id * 15 + 50))
            if agent.dest == -1:
                client.choose_next_edge(
                    '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(next_nodes[agent.id][0]) + '}')

        ttl = client.time_to_end()

        if previous_time == -1 or previous_time - float(ttl) >= 100:  # making sure we do 10 moves per second
            previous_time = float(ttl)
            client.move()
            moves += 1

        msg = "Time left: " + str(int(int(ttl)/1000)) + " | Moves: " + str(moves)
        text = FONT.render(msg, True, Color(255, 255, 255))
        rect = text.get_rect(center=(WIDTH/2, 15))
        screen.blit(text, rect)

        # update screen changes
        display.update()

        # print(ttl, client.get_info())

except ConnectionResetError:
    print("Game Over!")
