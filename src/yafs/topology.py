# -*- coding: utf-8 -*-
import logging
import networkx as nx
import warnings

class Topology:
    LINK_BW = "BW"
    LINK_PR = "PR"
    NODE_IPT = "IPT"

    def __init__(self, logger=None):
        super(Topology, self).__init__()
        self.G = nx.Graph()
        if self.G is None:  # Debug check to catch NetworkX failure
            raise ValueError("NetworkX graph initialization failed!")
        self.__idNode = 0
        self.nodeAttributes = {}
        self.logger = logger or logging.getLogger(__name__)
        self.__init_uptimes()

    def __init_uptimes(self):
        for key in self.nodeAttributes:
            self.nodeAttributes[key]["uptime"] = (0, None)

    def get_edges(self):
        return self.G.edges

    def get_edge(self, key):
        return self.G.edges[key]

    def get_nodes(self):
        return self.G.nodes

    def get_node(self, key):
        return self.G.nodes[key]

    def get_info(self):
        return self.nodeAttributes

    def create_topology_from_graph(self, G):
        if isinstance(G, nx.classes.graph.Graph):
            self.G = G
        else:
            raise TypeError

    def create_random_topology(self, nxGraphGenerator, params):
        try:
            self.G = nxGraphGenerator(*params)
        except:
            raise Exception

    def load(self, data):
        warnings.warn("The load function will merged with load_all_node_attr function",
                      FutureWarning, stacklevel=8)
        self.G = nx.Graph()
        for edge in data["link"]:
            self.G.add_edge(edge["s"], edge["d"], BW=edge[self.LINK_BW], PR=edge[self.LINK_PR])

        for node in data["entity"]:
            self.nodeAttributes[node["id"]] = node

        valuesIPT = {}
        for node in data["entity"]:
            valuesIPT[node["id"]] = node.get("IPT", 0)

        nx.set_node_attributes(self.G, values=valuesIPT, name="IPT")
        self.__init_uptimes()

    def load_all_node_attr(self, data):
        self.G = nx.Graph()
        for edge in data["link"]:
            self.G.add_edge(edge["s"], edge["d"], BW=edge[self.LINK_BW], PR=edge[self.LINK_PR])

        dc = {str(x): {} for x in data["entity"][0].keys()}
        for ent in data["entity"]:
            for key in ent.keys():
                dc[key][ent["id"]] = ent[key]
        for x in data["entity"][0].keys():
            nx.set_node_attributes(self.G, values=dc[x], name=str(x))

        for node in data["entity"]:
            self.nodeAttributes[node["id"]] = node

        self.__idNode = len(self.G.nodes)
        self.__init_uptimes()

    def load_graphml(self, filename):
        warnings.warn("The load_graphml function is deprecated and will be removed in version 2.0.0. Use NX.READ_GRAPHML function instead.",
                      FutureWarning, stacklevel=8)
        self.G = nx.read_graphml(filename)
        attEdges = {k: {"BW": 1, "PR": 1} for k in self.G.edges()}
        nx.set_edge_attributes(self.G, values=attEdges)
        attNodes = {k: {"IPT": 1} for k in self.G.nodes()}
        nx.set_node_attributes(self.G, values=attNodes)
        for k in self.G.nodes():
            self.nodeAttributes[k] = self.G.nodes[k]

    def get_nodes_att(self):
        return self.nodeAttributes

    def find_IDs(self, value):
        keyS = list(value.keys())[0]
        result = []
        for key in self.nodeAttributes.keys():
            val = self.nodeAttributes[key]
            if keyS in val and value[keyS] == val[keyS]:
                result.append(key)
        return result

    def size(self):
        return len(self.G.nodes)

    def add_node(self, id, **attr):
        self.__idNode += 1
        self.G.add_node(self.__idNode, **attr)
        return self.__idNode

    def add_edge(self, src, dst, **attr):
        self.G.add_edge(src, dst, **attr)

    def remove_node(self, id_node):
        self.G.remove_node(id_node)
        return self.size()
