from graphviz import Digraph
from datetime import datetime


class GraphVisualizer(object):
    
    def __init__(self, paths, name='graph'):
        self.paths = paths
        self.name = name
        self.graph = Digraph(self.name, engine='dot', strict=True)

    def create_graph(self):
        for path in self.paths:
            for hop_number in range(len(path)):
                if hop_number < len(path) - 1:
                    cur_hop = path[hop_number]

                    self.graph.edge(
                        cur_hop.hop_number + cur_hop.ip,
                        path[hop_number+1].hop_number + path[hop_number+1].ip
                    )

                    self.graph.node(
                        cur_hop.hop_number + cur_hop.ip,
                        label="{}: {} ({})".format(
                            cur_hop.hop_number, cur_hop.ip,
                            cur_hop.asn if cur_hop.asn != 'AS???' else cur_hop.domain)
                    )

    def visualize(self):
        self.graph.view()

    def save(self):
        self.graph.render(self.name + str(datetime.now()))

