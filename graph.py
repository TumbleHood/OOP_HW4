from types import SimpleNamespace


class Graph:
    def __init__(self):
        self.v = {}  # v: {node_id: node_pos, ...}
        self.e_out = {}  # e_out: {start_id: {end_id: weight, ...}, ...}
        self.e_in = {}  # e_in: {end_id: {start_id: weight, ...}, ...}
        self.mc = 0

    def v_size(self):
        return len(self.v)

    def e_size(self):
        size = 0
        for i in self.e_in:
            size += len(self.e_in[i])  # len of e_in is the same as e_out
        return size

    def get_all_v(self):
        return self.v

    def all_in_edges_of_node(self, id1: int):
        if id1 in self.e_in:
            return self.e_in.get(id1)
        return None

    def all_out_edges_of_node(self, id1: int):
        if id1 in self.e_out:
            return self.e_out.get(id1)
        return None

    def get_mc(self):
        return self.mc

    def add_edge(self, id1: int, id2: int, weight: float):
        if id1 in self.e_out and id2 in self.e_out[id1] and \
                id2 in self.e_in and id1 in self.e_in[id2]:
            return False  # return false if the edge already exists
        if id1 not in self.e_out:
            self.e_out[id1] = {}
        if id2 not in self.e_in:
            self.e_in[id2] = {}
        self.e_out[id1][id2] = weight
        self.e_in[id2][id1] = weight
        self.mc += 1  # we changed the graph therefore we add 1 to the mc
        return True

    def add_node(self, node_id: int, pos: SimpleNamespace = None):
        if node_id not in self.v:
            self.v[node_id] = pos
            self.mc += 1  # we changed the graph therefore we add 1 to the mc
            return True
        return False

    def remove_node(self, node_id: int):
        if node_id in self.v:
            self.v.pop(node_id)
            if node_id in self.e_out:
                self.e_out.pop(node_id)
            if node_id in self.e_in:
                self.e_in.pop(node_id)
            for i in self.e_out.values():
                if node_id in i:
                    i.pop(node_id)
            for i in self.e_in.values():
                if node_id in i:
                    i.pop(node_id)
            self.mc += 1  # we changed the graph therefore we add 1 to the mc
            return True
        return False

    def remove_edge(self, node_id1: int, node_id2: int):
        if node_id1 in self.e_out and node_id2 in self.e_out[node_id1] and \
                node_id2 in self.e_in and node_id1 in self.e_in[node_id2]:
            self.e_out[node_id1].pop(node_id2)
            self.e_in[node_id2].pop(node_id1)
            self.mc += 1  # we changed the graph therefore we add 1 to the mc
            return True
        return False

    def __str__(self):
        return "Graph: |V|=" + str(self.v_size()) + ", |E|=" + str(self.e_size())
