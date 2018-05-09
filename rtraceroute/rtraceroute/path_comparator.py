from itertools import groupby
from itertools import izip_longest
from operator import itemgetter


class PathComparator(object):

    def __init__(self, forward_path, reverse_path):
        self.forward_path = list(reversed(forward_path))
        self.reverse_path = reverse_path
        self.forward_asns = PathComparator.get_asns(self.forward_path)
        self.reverse_asns = PathComparator.get_asns(self.reverse_path)

    def compare_paths_by_asns(self):
        a = PathComparator.group_asns(self.forward_path)
        b = PathComparator.group_asns(self.reverse_path)

        first_match_a, first_match_b = self.find_first_matching_asns(
            self.forward_path, self.reverse_path)

        # check that first matching asn is within first third of both paths
        if first_match_a > len(self.forward_path)/4 or first_match_b > len(self.reverse_path)/4:
            # otherwise, paths unify too late to be considered symmetrical
            return False

        if len(a) > len(b):
            a, b = b, a  # a is shorter or equal to b
        pos_a, pos_b = self.find_first_matching_asns(a, b)

        if pos_a is None:
            return False

        while pos_a < len(a) and pos_b < len(b):
            if ' ' in a[pos_a]:
                asns = a[pos_a].split(' ')
                for asn in asns:
                    if asn in b[pos_b]:
                        pos_a += 1
                        pos_b += 1
                        continue
                return False
            elif a[pos_a] == b[pos_b]:
                pos_a += 1
                pos_b += 1
            else:
                return False
        return True

    def compare_paths_by_hostnames(self):
        a = self.extract_hostnames(self.forward_path)
        b = self.extract_hostnames(self.reverse_path)

        if len(a) > len(b):
            a, b = b, a  # a is set to be shorter or equal to b

        pos_a = None
        pos_b = None

        for hostname in a:
            if hostname in b:
                pos_a = a.index(hostname)
                pos_b = b.index(hostname)

        if pos_a is not None:
            if pos_a > len(a)/2:
                return False  # paths meet too late

            while pos_a < len(a) and pos_b < len(b):
                found = False
                for hostname in a[pos_a]:
                    if hostname in b[pos_b]:
                        found = True
                        break
                if not found:
                    return False
                pos_a += 1
                pos_b += 1
            return True  # paths seem the same
        else:
            return False

    @staticmethod
    def extract_hostnames(path):
        hostnames = []

        for hop_line in path:
            line_hostnames = [x.hostname for x in hop_line]
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
    def get_asns(path):
        asns = []
        for hop_line in path:
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
    def get_hostnames(path):
        hostnames = []
        for hop_line in path:
            hostnames.append([x.hostname for x in hop_line])
        return hostnames

    @staticmethod
    def group_asns(hop_lines):
        return map(itemgetter(0),
                   groupby(PathComparator.get_asns(hop_lines)))

    def print_asn_paths(self):
        print("ASN paths:")
        print("Columns are in direction from destination host to source host.")
        print("{}\t\t{}".format('forward path', 'reverse path'))
        for asn_a, asn_b in izip_longest(self.forward_asns, self.reverse_asns,
                                         fillvalue=''):
            if isinstance(asn_a, list):
                asn_a = ', '.join(asn_a)
            if isinstance(asn_b, list):
                asn_b = ', '.join(asn_b)
            print "{}\t\t\t{}".format(asn_a, asn_b)

    def print_hostname_paths(self):
        forward_hostnames = self.get_hostnames(self.forward_path)
        reverse_hostnames = self.get_hostnames(self.reverse_path)

        print("Hostname paths:")
        print("Columns are in direction from destination host to source host.")
        print("{}{}{}".format('forward path', ' ' * 39, 'reverse path'))

        for f_hostname, r_hostname in izip_longest(
                forward_hostnames,
                reverse_hostnames,
                fillvalue=''):
            print("{}{}{}".format(
                ','.join(f_hostname),
                ' ' * (1 + (50 - len(','.join(f_hostname)))), # at least 1 space
                ','.join(r_hostname)))

    def extract_individual_paths(self, path):
        probe_count = self.find_probes_packets_count(path)
        paths = []

        for probe_number in range(1, probe_count):
            path = []
            for hop_line in path:
                if len(hop_line) == 1:
                    path.append(hop_line[0])
                    continue
                for hop in hop_line:
                    if probe_number in hop.packet_numbers:
                        path.append(hop)
                        break
            #if not self.path_in_paths(path, paths):
            paths.append(path)
        return paths

    @staticmethod
    def find_probes_packets_count(path):
        maxnum = 0
        for hop_line in path:
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

    @staticmethod
    def hop_in_path(hop, path):
        line = 0
        for hop_line in path:
            for a_hop in hop_line:
                if a_hop.ip == hop.ip or a_hop.hostname == hop.hostname:
                    return line
            line += 1
        return -1  # not found

    @staticmethod
    def merge_paths(path, other_path):
        """
        Method tries to stitch together TCP/UDP and ICMP path
        :param path:
        :param other_path:
        :return:
        """
        # icmp is not load-balanced so x[0] is not None
        parsed_ft_icmp_results_path = [x[0] for x in other_path]

        pos_found = -1
        for pos, hop in reversed(
                list(enumerate(parsed_ft_icmp_results_path))):
            line = PathComparator.hop_in_path(hop, path)
            if line != -1:
                pos_found = pos
                break

        if pos_found != -1:
            path = path[:line]
            path.extend(other_path[pos_found + 1:])
        return path
