import os
from typing import List
from graph import Graph
import json
from itertools import permutations
import random


class GraphAlgo:

    def __init__(self, g=None):
        self.g = g

    def get_graph(self):
        return self.g

    def load_from_json(self, file_name: str):
        self.g = Graph()
        if not os.path.isfile(os.path.abspath(file_name)):
            file_name += ".json"
        if os.path.isfile(os.path.abspath(file_name)):
            with open(os.path.abspath(file_name)) as f:
                data = json.load(f)
                for node in data.get("Nodes"):
                    id1 = int(node.get("id"))
                    pos = None
                    if "pos" in node:
                        pos_list = node.get("pos").split(",")
                        pos = (float(pos_list[0]), float(pos_list[1]), float(pos_list[2]))
                    self.g.add_node(id1, pos)
                for edge in data.get("Edges"):
                    src = int(edge.get("src"))
                    w = float(edge.get("w"))
                    dest = int(edge.get("dest"))
                    self.g.add_edge(src, dest, w)
            return True
        return False

    def save_to_json(self, file_name: str):
        if not file_name.endswith(".json"):
            file_name += ".json"
        f = open(os.path.abspath(file_name), "w")
        data = {"Nodes": [], "Edges": []}
        for v in self.g.get_all_v().items():
            node = {"id": v[0]}
            if v[1]:
                pos = str(v[1])[1:-1].replace(" ", "")  # remove the brackets and the spaces
                node["pos"] = pos
            data["Nodes"].append(node)
            if self.g.all_out_edges_of_node(v[0]):
                for e in self.g.all_out_edges_of_node(v[0]).items():
                    edge = {"src": v[0], "dest": e[0], "w": e[1]}
                    data["Edges"].append(edge)

        json_data = json.dumps(data, indent=2)  # pretty print json
        f.write(json_data)
        f.close()
        return True

    def shortest_path(self, id1: int, id2: int):
        # https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Pseudocode
        q = list(self.g.get_all_v().keys())
        dist, prev = {}, {}

        for v in q:
            dist[v] = float("inf")
            prev[v] = -1
        dist[id1] = 0

        while q:
            u = (q[0], float("inf"))
            for i in dist.items():
                if i[0] in q and i[1] < u[1]:
                    u = i
            q.remove(u[0])

            if u[0] == id2:
                break

            if self.g.all_out_edges_of_node(u[0]):
                for e in self.g.all_out_edges_of_node(u[0]).items():
                    if e[0] in q:
                        alt = dist[u[0]] + e[1]
                        if alt < dist[e[0]]:
                            dist[e[0]] = alt
                            prev[e[0]] = u[0]

        path = []
        u = id2
        if prev[u] != -1 or u == id1:
            while u != -1:
                path.insert(0, u)
                u = prev[u]

        return dist[id2], path

    def tsp(self, node_lst: List[int]):
        pers = permutations(node_lst)
        dist, path = {}, {}
        for per in pers:  # go over all permutations
            dist[per] = 0
            path[per] = []
            for i in range(len(per) - 1):
                dist[per] += self.shortest_path(per[i], per[i + 1])[0]
                # add the weight between each pair in the permutations
                path[per] += self.shortest_path(per[i], per[i + 1])[1][:-1]
                # write the real path between all the cities
                # (since it can contain vertices that are not mentioned in cities)
            path[per].append(per[-1])

        tsp = ((), float("inf"))
        for i in dist.items():
            if i[1] < tsp[1]:
                tsp = i

        if tsp[0]:
            return path[tsp[0]], tsp[1]
        return float("inf"), None

    def center_point(self):
        max_dist = {}
        for v1 in list(self.g.get_all_v().keys()):
            max_dist[v1] = 0
            for v2 in list(self.g.get_all_v().keys()):
                if v1 != v2:
                    max_dist[v1] = max(self.shortest_path(v1, v2)[0], max_dist[v1])
                    if max_dist[v1] == float("inf"):
                        return None, float("inf")

        min_max = (None, float("inf"))
        for i in max_dist.items():
            if i[1] < min_max[1]:
                min_max = i

        return min_max

    # def plot_graph(self):
    #     x_list, y_list = {}, {}
    #     point_color = "red"
    #     label_color = "lime"
    #     arrow_color = "black"
    #     for v in self.g.get_all_v().items():  # draws the points
    #         if v[1]:
    #             x_list[v[0]] = (v[1][0])
    #             y_list[v[0]] = (v[1][1])
    #         else:
    #             x_list[v[0]] = (random.random())
    #             y_list[v[0]] = (random.random())
    #     plt.scatter(x_list.values(), y_list.values(), color=point_color)
    #
    #     for v in self.g.get_all_v().keys():  # draws arrows
    #         if self.g.all_out_edges_of_node(v):
    #             for e in self.g.all_out_edges_of_node(v).keys():
    #                 plt.annotate("", xy=(x_list[e], y_list[e]), xytext=(x_list[v], y_list[v]),
    #                              arrowprops=dict(arrowstyle="->", color=arrow_color))
    #
    #     for v in self.g.get_all_v():  # writes the id over the point
    #         plt.annotate(str(v), (x_list[v], y_list[v]), color=label_color)
    #
    #     plt.show()
