# ROOT = '/home/wangjing/Dropbox/Research/sadit/'
ROOT = '/home/jzh/Dropbox/Git/sadit/'

DIR = '/home/jzh/Research/CyberSecurity/Robust_Method/PaperSimulation/FlowSizePeriod/'

import numpy as np
#################################
##   Parameters For Detector  ###
#################################
# import itertools
# ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        # method = 'robust',
        # method = 'mfmb',
        # ref_scheck='dump',
        ref_scheck = 'load',
        # lamb = 0,
        # lamb = 0,
        lamb = 0.5,
        # ref_scheck='load',
        comp_methods = ['robust', 'mfmb'],
        # data = DIR + 'n0_flow_50_anomalies.txt',
        # data = DIR + 'n0_flow_1_ano_200000_205000.txt',
        # data = DIR + 'n0_flow_reference.txt',
        # ref_data = DIR + 'n0_flow_reference.txt',
        data = DIR + 'n0_flow_1_ano_200000_205000.txt',
        # data = DIR + 'n0_referece_normal.txt',
        ref_data = DIR + 'n0_referece_normal.txt',
        dump_folder = DIR + 'PeriodResCompareOneAno/',
        # ref_data = DIR + 'n0_flow_50_anomalies.txt',
        normal_rg = None,
        # interval = 5000,
        interval = 2000,
        win_size=2000,
        win_type='time', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.001,
        unified_nominal_pdf = False, # used in sensitivities analysis
        fea_option = {'dist_to_center':5, 'flow_size':10, 'cluster':1},
        # fea_option = {'dist_to_center':1, 'flow_size':2, 'cluster':1},
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        max_detect_num = None,
        data_type = 'fs',
        pic_show = True,
        pic_name = './res2.eps',
        export_flows = None,
        csv = None,

        ####### Only for Robust approach #####
        register_info = {
            # 'FBAnoDetector' : {
                # 'type' : 'static',
                # 'para' : {
                    # ref_data = [DIR + 'n0_referece_normal.txt'],
                    # 'method' : ['mfmb'],

                    # 'normal_rg' : [100000, 500000],
                    # 'fea_option' : [
                        # {'dist_to_center':1, 'flow_size':2, 'cluster':1},
                        # {'dist_to_center':1, 'flow_size':3, 'cluster':1},
                        # {'dist_to_center':1, 'flow_size':4, 'cluster':1},
                        # {'dist_to_center':1, 'flow_size':5, 'cluster':1},
                        # ]
                    # } #FIXME
                # },
            'PeriodStaticDetector' : {
                'type' : 'static',
                'para' :  {
                    'period':[24 * 3600] ,
                    # 'start': np.linspace(0, 12*3600, 7),
                    # 'period': np.linspace(24*3600, 2*24*3600, 6),
                    'start': np.linspace(0, 24*3600, 24),
                    # 'start': [40000],
                    'delta_t':[3600, 10000],
                    },
                'para_type' : 'product',
                },
             },

        #### only for SVM approach #####
        # gamma = 0.01,

        #### only for Generalized Emperical Measure #####
        small_win_size = 1,
        # small_win_size = 1000,
        g_quan_N = 3,
        )
# when using different data_hanlder, you will have different set of avaliable options for fea_option.
