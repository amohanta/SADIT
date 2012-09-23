#!/usr/bin/env python
import sys
sys.path.insert(0, "..")
from Configure import gen_anomaly_dot
import settings
from util import Namespace
import argparse

from os import chdir as cd
from os import system as sh
from Detector import detect

zeros = lambda s:[[0 for i in xrange(s[1])] for j in xrange(s[0])]
def get_inet_adj_mat(fname):
    """change the topology file with inet format to
    adjacent matrix.
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
    """A fs node can either represent a real node or a network. If the addr in
    node's ipdests is add prefix, then fs will automatically consider it as network.
    However, the net_settings generated by Imalse GUI topology also use CIDR format.
    To reduce ambiguity, delete all network length information in **link_to_ip_map**
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


class ImalseSettings(object):
    """This Experiment Load the network configurations generated by Imalse GUI tool
    and generate the data correspondingly.
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='ImalseSettings')
        self.initparser(self.parser)
        self.args, self.re_args = self.parser.parse_known_args()

    def initparser(self, parser):
        parser.add_argument('--topology_file', default='misc/imalse/topology.inet',
                help='topology file generated by imalse GUI tool')
        parser.add_argument('--net_settings_file', default='misc/imalse/net_settings.py',
                help='net_settings file generated by imalse GUI tool')
        parser.add_argument('--traf_pattern', default='misc/imalse/traffic_pattern.py',
        # parser.add_argument('--traf_pattern', default='settings.py',
                help='files that contains the traffic pattern')
        parser.add_argument('-t', '--simtime', default=5000,
                help='simulatuion time')
        parser.add_argument('--dot_file', default='misc/imalse/conf.dot',
                help='the configured dot file')

    def load_para(self, f_name, encap=Namespace, **kwargs):
        """load parameters. **kwargs** contains some
        additional parameters"""
        s = kwargs
        execfile(f_name, s)
        return s if encap is None else encap(s)
        # return Namespace(s)

    def get_net_desc(self):
        topo = get_inet_adj_mat(settings.ROOT + '/' + self.args.topology_file)
        new_net_settings_file = fix_fs_addr_prefix_bug(settings.ROOT + '/' + self.args.net_settings_file)
        net_settings = self.load_para(f_name=new_net_settings_file, encap=None)
        net_settings['topo'] = topo
        net_settings['node_type'] = 'NNode'
        net_settings['node_para'] = {}
        # net_settings['srv_list'] = net_settings['server_id_set']
        return net_settings

    def configure(self):
        traf_pattern = self.load_para(
                f_name = settings.ROOT + '/' + self.args.traf_pattern,
                sim_t = float(self.args.simtime),
                )

                # topo = topo,
                # srv_node_list = net_settings.server_id_set,

        self.dot_file = settings.ROOT + '/' + self.args.dot_file
        gen_anomaly_dot(
                traf_pattern.ANO_LIST,
                self.get_net_desc(),
                traf_pattern.NORM_DESC,
                self.dot_file,
                )
        return self.dot_file

    def simulate(self):
        cd(settings.ROOT + '/Simulator')
        sh('python fs.py %s -t %s' %(self.dot_file, self.args.simtime) )
        cd(settings.ROOT)

    def detect(self):
        self.flow_file = settings.ROOT + '/Simulator/n0_flow.txt'
        # self.flow_file = settings.ROOT + '/Simulator/n1_flow.txt'
        self.detector = detect(self.flow_file, settings.DETECTOR_DESC)
        return self.detector

if __name__ == "__main__":
    exper = ImalseSettings()
    exper.configure()
    exper.simulate()
    detector = exper.detect()
    detector.plot_entropy(hoeffding_false_alarm_rate = 0.01)
