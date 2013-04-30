#!/usr/bin/env python
""" (experimental) Load the topology script generated by Imalse
Topology Editor, generate the flow records and test with
the anomaly detectors.
"""
from __future__ import print_function, division, absolute_import
from sadit.util import load_para

zeros = lambda s:[[0 for i in xrange(s[1])] for j in xrange(s[0])]
def get_inet_adj_mat(fname):
    """ change the topology file with inet format to adjacent matrix.
    """
    fid = open(fname, 'r')
    i = -1
    while True:
        i += 1
        line = fid.readline()
        if not line: break
        if i == 0:
            totnode, totlink = [int(s.strip()) for s in line.rsplit()]
            adj_mat = zeros([totnode, totnode])
            continue
        if i <= totnode: # ignore the position information
            continue

        _from, _to, _lineBuffer = [s.strip() for s in line.rsplit()]
        adj_mat[int(_from)][int(_to)] = 1
    fid.close()

    return adj_mat

import pprint
import os
def fix_fs_addr_prefix_bug(f_name):
    """ fix the bug in fs address

    A fs node can either represent a real node or a network. If the addr in
    node's ipdests is add prefix, then fs will automatically consider it as
    network.  However, the net_settings generated by Imalse GUI topology also
    use CIDR format.  To reduce ambiguity, delete all network length
    information in **link_to_ip_map**

    """
    s = {}
    execfile(f_name, s)
    new_link_to_ip_map = {}
    for k, v in s.get('link_to_ip_map', {}).iteritems():
        new_link_to_ip_map[k] = [val.rsplit('/')[0] for val in v]
    s['link_to_ip_map'] = new_link_to_ip_map
    new_f_name = os.path.dirname(f_name) + '/new_' + os.path.basename(f_name)
    fid = open(new_f_name, 'w')
    fid.close()
    fid = open(new_f_name, 'a')
    for k, v in s.iteritems():
        if k.startswith('__'):
            continue
        fid.write('%s = '%(k))
        pprint.pprint(v, stream=fid)
    fid.close()
    return new_f_name

# from .BaseExper import BaseExper
from .Sim import Sim
class GUITopoSim(Sim):
    """ Load the network configurations generated by Imalse GUI tool
    """
    def __init__(self, argv, parser=None):
        super(GUITopoSim, self).__init__(argv)
        self.topo_file = self.ROOT + '/' + self.args.topology_file
        self.ns_file = self.ROOT + '/' + self.args.net_settings_file
        self.net_desc = self.get_net_desc(self.topo_file, self.ns_file)

    def init_parser(self, parser):
        super(GUITopoSim, self).init_parser(parser)
        parser.add_argument('-t','--topology_file',
                help='topology file generated by imalse GUI tool')
        parser.add_argument('-n', '--net_settings_file',
                help='net_settings file generated by imalse GUI tool')

    def get_net_desc(self, topo_file, ns_file):
        new_net_settings_file = fix_fs_addr_prefix_bug(ns_file)
        net_settings = load_para(f_name=new_net_settings_file, encap=None)
        net_settings['topo'] = get_inet_adj_mat(topo_file)
        net_settings['node_type'] = 'NNode'
        net_settings['node_para'] = {}
        # net_settings['srv_list'] = net_settings['server_id_set']
        return net_settings

if __name__ == "__main__":
    import doctest
    doctest.testmod()
