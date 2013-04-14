"""
This file defines useful API for other modules or program to use
"""
# from Detector_basic import ModelFreeAnoDetector, ModelBaseAnoDetector, FBAnoDetector
from StoDetector import ModelFreeAnoDetector, ModelBaseAnoDetector, FBAnoDetector
from SVMDetector import SVMFlowByFlowDetector, SVMTemporalDetector

detector_map = {
        'mf': ModelFreeAnoDetector,
        'mb': ModelBaseAnoDetector,
        'mfmb': FBAnoDetector,
        'svm_fbf': SVMFlowByFlowDetector,
        'svm_temp': SVMTemporalDetector,
        }

# from DataHandler import HardDiskFileHandler, HardDiskFileHandler_pcap2netflow, SQLDataFileHandler_SperottoIPOM2009, DataFile
# from DataHandler import QuantizeDataHandler, DataFile
from DataHandler import *
data_handler_handle_map = {
        'svm_temp': SVMTemporalHandler,
        'mf': QuantizeDataHandler,
        'mb': QuantizeDataHandler,
        'mfmb': QuantizeDataHandler,
        }

from Data import *
data_map = {
        'fs': PreloadHardDiskFile,
        'pcap2netflow': PreloadHardDiskFile_pcap2netflow,
        'xflow': PreloadHardDiskFile_xflow,
        'SQLFile_SperottoIPOM2009': SQLFile_SperottoIPOM2009,
        }
def detect(f_name, desc):
    """An function for convenience
    - *f_name* the name or a list of name for the flow file.
    - *win_size* the window size
    - *fea_option*

    """
    win_size = desc['win_size']
    fea_option = desc['fea_option']
    # data_file = data_handler_handle_map[ desc['data_handler'] ](f_name, win_size, fea_option)
    data_file = data_map[ desc['data_type'] ](f_name)
    data_handler = data_handler_handle_map[desc['detector_type']](data_file, win_size, fea_option)
    detector = detector_map[ desc['detector_type'] ](desc)
    # detector.detect(data_file)
    detector.detect(data_handler)
    return detector

def test_detect():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=20,
            win_size=400,
            win_type='time', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            data_handler = 'fs',
            )
    desc = DETECTOR_DESC
    detector = detect('../Simulator/n0_flow.txt', desc)
    detector.plot_entropy()

if __name__ == "__main__":
    test_detect()