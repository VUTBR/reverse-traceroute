from datetime import datetime
from networkx import DiGraph
from networkx.drawing.nx_pydot import write_dot
import logging
import os


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
                        cur_hop.hop_number + cur_hop.ip,
                        path[hop_number + 1].hop_number + path[hop_number + 1].ip)

                    self.nxgraph.add_node(
                        cur_hop.hop_number + cur_hop.ip,
                        label="{}: {} \\n({})".format(
                            cur_hop.hop_number,
                            cur_hop.hostname if cur_hop.hostname != '*' else cur_hop.ip,
                            cur_hop.asn if cur_hop.asn != 'AS???' else cur_hop.domain)
                    )
                else:
                    self.nxgraph.add_node(
                        cur_hop.hop_number + cur_hop.ip,
                        label="{}: {} \\n({})".format(
                            cur_hop.hop_number,
                            cur_hop.hostname if cur_hop.hostname != '*' else cur_hop.ip,
                            cur_hop.asn if cur_hop.asn != 'AS???' else cur_hop.domain)
                    )

    def highlight_return_path(self, return_path):
        for hop_line in return_path:
            for hop in hop_line:
                self.highlight_hop_if_in_graph(hop)

    def highlight_hop_if_in_graph(self, hop):
        for node in self.nxgraph.nodes.items():
            if hop.hostname in node[1]['label']:
                self.nxgraph.add_node(node[0], color='green', style='filled')
                break
            elif hop.asn in node[1]['label']:
                self.nxgraph.add_node(node[0], color='orange', style='filled')
                break

    def save(self, name='graph'):
        """
        Creates pdf file with path graph.

        :param name: Name of created graph
        :return:
        """
        time = datetime.now()
        try:
            write_dot(self.nxgraph, 'nx.tmp.dot')
            os.system('dot -Tpdf nx.tmp.dot -o{}.pdf'.format(
            name + '_{}:{}:{}'.format(
                time.hour,
                time.minute,
                time.second)))
            #os.remove('nx.tmp.dot')
        except IOError as e:
            logging.error('Could not write temporary dot file '
                          'nx.tmp.dot')