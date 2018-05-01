from operator import itemgetter
from itertools import groupby
from itertools import izip_longest


class PathComparator(object):

    def __init__(self, forward_hop_lines, reverse_hop_lines):
        self.forward_hop_lines = list(reversed(forward_hop_lines))
        self.reverse_hop_lines = reverse_hop_lines
        self.forward_asns = PathComparator.extract_asns(self.forward_hop_lines)
        self.reverse_asns = PathComparator.extract_asns(self.reverse_hop_lines)

    def compare_paths_by_asns(self):
        a = PathComparator.group_asns(self.forward_hop_lines)
        b = PathComparator.group_asns(self.reverse_hop_lines)

        if len(a) > len(b):
            a, b = b, a  # a is shorter or equal to b

        pos_a, pos_b = self.find_first_matching_asns(a, b)
        if pos_a is None:
            return False

        same_from = pos_a

        while pos_a < len(a):
            if a[pos_a] == b[pos_b]:
                pos_a += 1
                pos_b += 1
            else:
                return False

        # allow only first asn to differ
        if same_from <= 1:
            return True
        else:
            return False

    def compare_paths_by_hostnames(self):
        a = self.extract_hostnames(self.forward_hop_lines)
        b = self.extract_hostnames(self.reverse_hop_lines)

        if len(a) > len(b):
            a, b = b, a  # a is shorter or equal to b

        pos_a = None
        pos_b = None

        for hostname in a:
            if hostname in b:
                pos_a = a.index(hostname)
                pos_b = b.index(hostname)

        if pos_a is not None:
            if pos_a > len(a)/2:
                return False  # paths meet too late

            while pos_a < len(a):
                if isinstance(a[pos_a], list):
                    found = False
                    for hostname in a[pos_a]:
                        if hostname in b[pos_b]:
                            found = True
                            break
                    if not found:
                        return False
                    pos_a += 1
                    pos_b += 1

                elif isinstance(b[pos_b], list):
                    found = False
                    for hostname in b[pos_b]:
                        if hostname in a[pos_a]:
                            found = True
                            break
                    if not found:
                        return False
                    pos_a += 1
                    pos_b += 1

                elif a[pos_a] == b[pos_b]:
                    pos_a += 1
                    pos_b += 1
                else:
                    return False
        return True  # paths seem the same

    @staticmethod
    def extract_hostnames(hop_lines):
        hostnames = []

        for hop_line in hop_lines:
            if len(hop_line) > 1:
                line_hostnames = [x.hostname for x in hop_lines]
            else:
                line_hostnames = hop_line[0].hostname
            hostnames.append(line_hostnames)
        return hostnames


    @staticmethod
    def intersection(lst1, lst2):
        temp = set(lst2)
        lst3 = [value for value in lst1 if value in temp]
        return lst3

    def find_first_matching_asns(self, a, b):
        pos_b = None
        for pos_a, asn_a in enumerate(a):
            if asn_a == 'AS???':
                continue
            if asn_a in b:
                pos_b = b.index(asn_a)
                return pos_a, pos_b
        return None, None

    @staticmethod
    def extract_asns(hop_lines):
        asns = []
        for hop_line in hop_lines:
            if len(hop_line) > 1:
                new_asns = list(set([x.asn for x in hop_line if x.asn]))
                if len(new_asns) > 1:
                    try:
                        new_asns.remove('AS???')
                    except ValueError:
                        pass  # do nothing
                    new_asns = ",".join(new_asns)
                elif len(new_asns) == 1:
                    new_asns = new_asns[0]
            else:
                new_asns = hop_line[0].asn
            asns.append(new_asns)
        return asns

    @staticmethod
    def group_asns(hop_lines):
        return map(itemgetter(0), groupby(PathComparator.extract_asns(hop_lines)))

    def print_asn_paths(self):
        print "{}\t\t\t{}".format('forward path', 'reverse path')
        for asn_a, asn_b in izip_longest(self.forward_asns, self.reverse_asns, fillvalue=''):
            if isinstance(asn_a, list):
                asn_a = ', '.join(asn_a)
            if isinstance(asn_b, list):
                asn_b = ', '.join(asn_b)
            print "{}\t\t\t{}".format(asn_a, asn_b)

    def extract_individual_paths(self, hop_lines):
        probe_count = self.find_probes_count(hop_lines)
        paths = []

        for probe_number in range(probe_count):
            path = []
            for hop_line in hop_lines:
                for hop in hop_line:
                    if probe_number in hop.probe_numbers:
                        path.append(hop)
                        break
            if not self.path_in_paths(path, paths):
                paths.append(path)
        return paths

    @staticmethod
    def find_probes_count(hop_lines):
        maxnum = 0
        for hop_line in hop_lines:
            probes = [x.packet_numbers for x in hop_line if
            len(x.packet_numbers) > 0]
            if probes:
                tmpmax = max(map(max, probes))
                if tmpmax > maxnum:
                    maxnum = tmpmax
        return maxnum + 1  # numbers in paris-traceroute output start from 0

    @staticmethod
    def path_in_paths(new_path, paths):
        found = False
        for path in paths:
            if len(path) != len(new_path):
                continue
            for hop_number in range(len(path)):
                if path[hop_number] != new_path[hop_number]:
                    break
                if hop_number == len(path):
                    found = True
        return found
