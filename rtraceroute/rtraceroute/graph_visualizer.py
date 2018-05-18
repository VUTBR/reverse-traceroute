from datetime import datetime
from networkx import DiGraph
from networkx.drawing.nx_pydot import write_dot
import networkx as nx
import logging
import os

NODE_DATA = 1
NODE_ID = 0


class GraphVisualizer(object):
    
    def __init__(self, paths, name='graph'):
        self.paths = paths
        self.name = name
        self.nxgraph = DiGraph()

    def create_nxgraph(self):
        for path in self.paths:
            for hop_number in range(len(path)):
                cur_hop = path[hop_number]
                if hop_number < len(path) - 1:

                    self.nxgraph.add_edge(
                        str(cur_hop.hop_number) + cur_hop.ip,
                        str(path[hop_number + 1].hop_number) + path[hop_number + 1].ip)

                    self.nxgraph.add_node(
                        str(cur_hop.hop_number) + cur_hop.ip,
                        label="{}: {} \\n({})".format(
                            cur_hop.hop_number,
                            cur_hop.hostname if cur_hop.hostname != '*' else cur_hop.ip,
                            cur_hop.asn if cur_hop.asn != 'AS???' else cur_hop.domain)
                    )
                else:
                    self.nxgraph.add_node(
                        str(cur_hop.hop_number) + cur_hop.ip,
                        label="{}: {} \\n({})".format(
                            cur_hop.hop_number,
                            cur_hop.hostname if cur_hop.hostname != '*' else cur_hop.ip,
                            cur_hop.asn if cur_hop.asn != 'AS???' else cur_hop.domain)
                    )

    def draw_return_path(self, return_path):
        # first, find common host
        node = None
        hop_found = None

        import IPython
        IPython.embed()

        # get first matching node in graph and return path
        for hops in return_path:
            node, hop_found = self.get_node_by_hostname(hops)
            if node is not None:
                break
        if node is None:
            return

        i = 0
        found = False
        for hops in return_path:
            for hop in hops:
                if hop.hostname == hop_found.hostname:
                    found = True
                    break
            if found:
                break
            i += 1

        rest_return_path = return_path[i:]
        rest_graph = nx.nodes(nx.dfs_tree(self.nxgraph, node[NODE_ID]))
        raise NotImplemented

    def get_node_by_hostname(self, hops):
        for node in self.nxgraph.nodes.items():
            for hop in hops:
                if hop.hostname == '*':
                    continue
                if hop.hostname in node[NODE_DATA]['label']:
                    return node, hop
        return None, None

    def highlight_return_path(self, return_path):
        for hop_line in return_path:
            for hop in hop_line:
                self.highlight_hop_if_in_graph(hop)

    def highlight_hop_if_in_graph(self, hop):
        for node in self.nxgraph.nodes.items():
            if hop.hostname in node[NODE_DATA]['label']:
                self.nxgraph.add_node(node[0], color='green', style='filled')
            if hop.asn in node[NODE_DATA]['label']:
                if 'color' in node[NODE_DATA] and 'green' not in node[NODE_DATA]['color']:
                    self.nxgraph.add_node(node[0], color='orange',
                                          style='filled')
                elif 'color' not in node[NODE_DATA]:
                    self.nxgraph.add_node(node[0], color='orange',
                                          style='filled')

    def save(self, name='graph'):
        """
        Creates pdf file with path graph.

        :param name: Name of created graph
        :return:
        """
        time = datetime.now()
        try:
            write_dot(self.nxgraph, 'nx.tmp.dot')
            os.system('dot -Tpdf nx.tmp.dot -oreports/{}.pdf'.format(
            name + '_{}:{}:{}'.format(
                time.hour,
                time.minute,
                time.second)))
            # os.remove('nx.tmp.dot')
        except IOError as e:
            logging.error('Could not write temporary dot file '
                          'nx.tmp.dot')
