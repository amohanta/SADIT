#!/usr/bin/env python
"""
This file contains all the detection techniques
"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"
__status__ = "Development"

import sys
sys.path.append("..")
# import settings
try:
    from matplotlib.pyplot import figure, plot, show, subplot, title, savefig
except:
    print 'no matplotlib'
    VIS = False

from DetectorLib import I1, I2
from util import DataEndException, FetchNoDataException,  abstract_method

import cPickle as pickle
# from AnoType import ModelFreeAnoTypeTest, ModelBaseAnoTypeTest
from DataFile import DataFile, HardDiskFileHandler

class AnoDetector (object):
    """It is an Abstract Base Class for the anomaly detector."""
    def __init__(self, desc):
        self.desc = desc
        # self.record_data = dict(IF=[], IB=[], winT=[], threshold=[], em=[])
        self.record_data = dict(entropy=[], winT=[], threshold=[], em=[])

    def __call__(self, *args, **kwargs):
        return self.detect(*args, **kwargs)

    def get_em(self, rg, rg_type):
        """abstract method. Get empirical measure,
        rg is a list specify the start and the end point of the data
            that will be used
        rg_type is the type of the rg, can be ['flow'|'time']"""
        abstract_method()

    def I(self, em1, em2):
        """abstract method to calculate the difference of two
        empirical measure"""
        abstract_method()

    def record(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.record_data[k].append(v)

    def reset_record(self):
        for k, v in self.record_data.iteritems():
            self.record_data[k] = []

    # def detect(self, data_file, nominal_rg = [0, 1000], rg_type='time',  max_detect_num=None):
    def detect(self, data_file):
        """main function to detect. it will slide the window, get the emperical
        measure and get the indicator"""
        nominal_rg = self.desc['normal_rg']
        rg_type = self.desc['win_type']
        max_detect_num = self.desc['max_detect_num']

        self.data_file = data_file
        self.norm_em = self.get_em(rg=nominal_rg, rg_type=rg_type)

        win_size = self.desc['win_size']
        interval = self.desc['interval']
        time = self.desc['fr_win_size'] if ('flow_rate' in self.desc['fea_option'].keys()) else 0

        i = 0
        while True:
            i += 1
            if max_detect_num and i > max_detect_num:
                break
            if rg_type == 'time' : print 'time: %f' %(time)
            else: print 'flow: %s' %(time)

            try:
                # d_pmf, d_Pmb, d_mpmb = self.data_file.get_em(rg=[time, time+win_size], rg_type='time')
                em = self.get_em(rg=[time, time+win_size], rg_type=rg_type)
                entropy = self.I(em, self.norm_em)
                self.record( entropy=entropy, winT = time, threshold = 0, em=em )
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += interval

        return self.record_data

    def plot_entropy(self, pic_show=True, pic_name=None):
        if not VIS: return
        rt = self.record_data['winT']
        figure()
        plot(rt, self.record_data['entropy'])

        if pic_name: savefig(pic_name)
        if pic_show: show()

    def dump(self, data_name):
        pickle.dump( self.record_data, open(data_name, 'w') )

class ModelFreeAnoDetector(AnoDetector):
    def I(self, d_pmf, pmf):
        return I1(d_pmf, pmf)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return pmf, Pmb, mpmb

class ModelBaseAnoDetector(AnoDetector):
    def I(self, em, norm_em):
        d_Pmb, d_mpmb = em
        Pmb, mpmb = norm_em
        return I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def get_em(self, rg, rg_type):
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return Pmb, mpmb

class FBAnoDetector(AnoDetector):
    """model free and model based together"""
    def I(self, em, norm_em):
        d_pmf, d_Pmb, d_mpmb = em
        pmf, Pmb, mpmb = norm_em
        return I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return pmf, Pmb, mpmb

    def plot_entropy(self, pic_show=True, pic_name=None):
        rt = self.record_data['winT']
        figure()
        subplot(211)
        mf, mb = zip(*self.record_data['entropy'])
        plot(rt, mf)
        title('model free')
        subplot(212)
        plot(rt, mb)
        title('model based')

        if pic_name: savefig(pic_name)
        if pic_show: show()

def detect(f_name, win_size, fea_option, detector_type, detector_desc):
    """An function for convenience
    - *f_name* the name or a list of name for the flow file.
    - *win_size* the window size
    - *fea_option*

    """
    detector_map = {
            'mf':ModelFreeAnoDetector,
            'mb':ModelBaseAnoDetector,
            'mfmb':FBAnoDetector,
            }
    # data_file = DataFile(f_name, win_size, fea_option)
    data_file = HardDiskFileHandler(f_name, win_size, fea_option)
    detector = detector_map[detector_type](detector_desc)
    detector(data_file)
    return detector
# type_detector = ModelFreeAnoTypeTest(detect, 3000, settings.ANO_DESC['T'])
    # type_detector.detect_ano_type()

    # type_detector = ModelBaseAnoTypeTest(detect, 3000, settings.ANO_DESC['T'])
    # type_detector.detect_ano_type()

    # import pdb;pdb.set_trace()
    # detect.plot_entropy()

def test_detect():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            # interval=30,
            # interval=50,
            # win_size = 50,
            interval=20,
            # win_size = 10,
            win_size=400,
            win_type='time', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            # discrete_level = DISCRETE_LEVEL,
            # cluster_number = CLUSTER_NUMBER,
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            # fea_option = {'dist_to_center':2, 'octets':2, 'cluster':2},
            # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':1},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            )
    desc = DETECTOR_DESC
    detector = detect('../Simulator/n0_flow.txt', desc['win_size'],
            desc['fea_option'], 'mfmb', desc)
    detector.plot_entropy()

def standalone_detect(file_name):
    from settings import DETECTOR_DESC as desc
    detector = detect(file_name, desc['win_size'],
            desc['fea_option'], 'mfmb', desc)

    detector.plot_entropy()

if __name__ == "__main__":
    test_detect()