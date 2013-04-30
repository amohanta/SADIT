"""
This file is the flow by flow svm detector
"""
import settings
SVM_FOLDER = settings.ROOT + '/tools/libsvm-3.12'
import subprocess

def write_svm_data_file(label, fea, f_name):
    fid = open(f_name, 'w')
    assert(len(label) == len(fea))
    n = len(label)
    for i in xrange(n):
        fea_v = fea[i]
        line = ['%s:%s'%(j+1, fea_v[j]) for j in xrange(len(fea_v)) ]
        fid.write(str(label[i]) + ' ' + ' '.join(line) + '\n')

# from Detector.DataHandler import HardDiskFileHandler
from Detector.DataHandler import QuantizeDataHandler
# class SVMDataHandler(HardDiskFileHandler):
class SVMDataHandler(QuantizeDataHandler):
    """Data Hanlder for SVM approach. It use a set of features
    which will be defined here"""
    pass

class SVMDetector(object):
    """base class for SVM Detector"""
    def __init__(self, desc):
        self._defaults()
        self.__dict__.update(desc)

    @property
    def rg_type(self): return self.win_type

    def _defaults(self):
        """default value for SVM detector parameters"""
        self.svm_dat_file= settings.ROOT + '/Share/test.dat'
        self.svm_model_file= settings.ROOT + '/Share/test.model'
        self.svm_pred_file= settings.ROOT + '/Share/test.pred'

        self.scale_para_file = settings.ROOT + '/Share/scale.sf'
        self.nu = 0.01
        self.gamma = 0.01

    def scale(self):
        print 'start to scale ...'
        scale_file = self.svm_dat_file + '.scale'
        subprocess.check_call(' '.join([SVM_FOLDER + '/svm-scale',
            '-s', self.scale_para_file,
            self.svm_dat_file,
            '>',
            scale_file
            ]), shell=True)
        self.svm_dat_file = scale_file

    def train(self):
        print 'start to train...'
        subprocess.check_call([SVM_FOLDER + '/svm-train',
            '-s', '2',
            '-n', str(self.nu),
            '-g', str(self.gamma),
            self.svm_dat_file,
            self.svm_model_file])

    def predict(self):
        print 'start to predict...'
        subprocess.check_call([SVM_FOLDER + '/svm-predict',
            self.svm_dat_file,
            self.svm_model_file,
            self.svm_pred_file])

    def load_pred(self):
        fid = open(self.svm_pred_file)
        self.pred = []
        while True:
            line = fid.readline()
            if not line: break
            self.pred.append(int(line))
        fid.close()

    def stat(self):
        pred_num = dict()
        for val in [-1, 1]:
            num = len([val for p in self.pred if p == val])
            pred_num[val] = num
        self.ano_val = 1 if pred_num[1] < pred_num[-1] else -1
        print 'total flows', len(self.pred), 'alarm num, ', pred_num[self.ano_val]

    def plot(self, *args, **kwargs): self.plot_pred(*args, **kwargs)

    def get_start_time(self):
        return self.data_file.data.get_fea_slice(fea=['start_time'])

class SVMFlowByFlowDetector(SVMDetector):
    """SVM Flow By Flow Anomaly Detector Method"""
    # MAX_FLOW_ONE_TIME = 1e4 # max number of flow it will compare each time
    SAMPLE_RATIO = 0.1 # sample the flows to reduce computation cost, sample ratio

    @staticmethod
    def sample(fea, ratio):
        flow_num = len(fea)
        sample_num = int(ratio * flow_num)
        interval = int(flow_num / sample_num)
        sample_fea = [fea[i] for i in xrange(0, flow_num, interval)]
        return sample_fea

    def get_start_time(self):
        start_time = self.data_file.data.get_fea_slice(fea=['start_time'])
        return self.sample(start_time, self.SAMPLE_RATIO)

    def write_dat(self, data):
        fea = data.get_fea_slice()
        # fea_str = data.data.get_fea_slice(['flow_size'])
        # fea = [[float(s[0])] for s in fea_str]
        # import pdb;pdb.set_trace()
        # label = [0] * len(fea)
        # write_svm_data_file(label, fea, self.svm_dat_file)

        #### SAMPLE FEATURE TO REDUCE COMPUTATION TIME ####
        sample_fea = self.sample(fea, self.SAMPLE_RATIO)
        label = [0] * len(sample_fea)
        write_svm_data_file(label, sample_fea, self.svm_dat_file)

    def detect(self, data):
        self.data_file = data
        self.write_dat(data)
        self.scale()
        self.train()
        self.predict()
        self.load_pred()

    def plot_pred(self, pic_show=True, pic_name=None):
        import matplotlib.pyplot as plt
        self.stat()
        fea_slice = self.get_start_time()
        min_t = float(fea_slice[0][0])
        start_time = [float(v[0])-min_t for v in fea_slice]
        x = [start_time[i] for i in xrange(len(start_time)) if self.pred[i] == self.ano_val]
        y = [1 for i in xrange(len(start_time)) if self.pred[i] == self.ano_val]
        # plt.plot(start_time, self.pred, '+')
        plt.plot(x, y, '+')
        if pic_show: plt.show()
        if pic_name: plt.savefig(pic_name)

from sadit.util import DataEndException, FetchNoDataException
class SVMTemporalDetector(SVMDetector):
    """SVM Temporal Difference Detector. Proposed by R.L Taylor. Implemented by
    J. C. Wang <wangjing@bu.ed> """
    def write_dat(self, data_handler):
        """construct feature and write dat data for libsvm use. data is a Data Handler Class. refer
        DataHandler.py for details.
        """
        fea_list = []
        time = 0
        i = 0
        while True:
            i += 1
            if self.max_detect_num and i > self.max_detect_num:
                break
            if self.rg_type == 'time' : print 'time: %f' %(time)
            else: print 'flow: %s' %(time)

            try:
                # fea = data_handler.get_svm_feature(rg=[time, time+self.win_size], rg_type=self.rg_type)
                fea = data_handler.get_svm_fea(rg=[time, time+self.win_size], rg_type=self.rg_type)
                fea_list.append(fea)
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += self.interval

        self.detect_num = i - 1

        label = [0] * len(fea_list)
        write_svm_data_file(label, fea_list, self.svm_dat_file)

    def train(self):
        print 'start to train...'
        subprocess.check_call([SVM_FOLDER + '/svm-train',
            '-s', '2',
            '-n', '0.001',
            '-g', str(self.gamma),
            self.svm_dat_file,
            self.svm_model_file])

    def detect(self, data_handler):
        self.write_dat(data_handler)
        self.scale()
        self.train()
        self.predict()
        self.load_pred()

    def plot_pred(self, pic_show=True, pic_name=None):
        import matplotlib.pyplot as plt
        self.stat()
        ano_idx = [i for i in xrange(self.detect_num) if self.pred[i] == self.ano_val]
        x = [i*self.interval for i in ano_idx]
        y = [self.pred[i] for i in ano_idx]
        plt.plot(x, y, '+')
        if pic_show: plt.show()
        if pic_name: plt.savefig(pic_name)



if __name__ == "__main__":
    desc = dict(gamma=0.1,
            svm_dat_file='./test.dat',
            svm_model_file='./test.model',
            svm_pred_file='./test.pred')
    detector = SVMFlowByFlowDetector(desc)
    detector.detect()
