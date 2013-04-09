#!/usr/bin/env python
# import argparse
# import settings
from BaseExper import BaseExper
from Configure import gen_anomaly_dot
from os import chdir as cd
from os import system as sh

from util import load_para, Namespace
class Sim(BaseExper):
    """
    Attributes:
    -----------------------
    net_desc : dict
        description of the network
    norm_desc : dict
        description of the normal case
    ano_list : list
        list of anomalies.

    """
    def __init__(self, argv):
        super(Sim, self).__init__(argv)

        if self.args.config is None:
            self.parser.print_help()
            import sys; sys.exit(0)

        self.ano_list = self.args.config['ANO_LIST']
        self.net_desc = self.args.config['NET_DESC']
        # self.dot_file = self.args.config['OUTPUT_DOT_FILE']
        self.norm_desc = self.args.config['NORM_DESC']
        self.sim_t = self.args.config['sim_t']
        self.dot_file = self.args.dot

    def init_parser(self, parser):
        parser.add_argument('-c', '--config', default=None,
                type=lambda x: load_para(x, Namespace),
                help="""config""")
        parser.add_argument('--dot', default=self.ROOT + '/Share/conf.dot',
                help="""output dot file""")

    def configure(self):
        gen_anomaly_dot(self.ano_list, self.net_desc, self.norm_desc,
                self.dot_file)

    def simulate(self):
        cd(self.ROOT + '/Simulator')
        sh('python fs.py %s -t %d' %(self.dot_file, self.sim_t) )
        cd(self.ROOT)

    def run(self):
        self.configure()
        self.simulate()
