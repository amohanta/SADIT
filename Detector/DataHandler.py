#!/usr/bin/env python
""" Handler Class for Data Files
    - [HardDiskFileHandler]: hard disk flow file generated by fs-simulator
    - [HardDiskFileHandler_pcap2netflow]: hard disk flow file generated by pcap2netflow tool
    - [SQLDataFileHandler_SperottoIPOM2009]: labeled data stored in mysql server provided by simpleweb.org
it also includes a depreciated version of hanlder class for flow file generated by fs-simulator [DataFile]
"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"

# import sys; sys.path.append("..")
from ClusterAlg import KMeans, KMedians
from DetectorLib import vector_quantize_states, model_based, model_free
from util import Find, DataEndException, DF, NOT_QUAN, QUAN
from util import abstract_method, FetchNoDataException

from DataHandler_deprec import DataFile

##############################################################
####                  Interface Class                   ######
##############################################################
class Data(object):
    """virtual base class for data. Data class deals with any implementation
    details of the data. it can be a file, a sql data base, and so on, as long
    as it support the pure virtual methods defined here.
    """
    def get_fea_slice(self, rg=None, rg_type=None):
        """ get a slice of feature
        - **rg** is the range for the slice
        - **rg_type** is the type for range, it can be ['flow'|'time']
        """
        abstract_method()

    def get_max(self, fea, rg=None, rg_type=None):
        """ get the max value of feature during a range
        - **fea** is a list of feature name
        - **rg** is the range
        - **rg_type** is the range type
        the output is the a list of element which contains the max
        value of the feature in **fea**
        """
        abstract_method()
    def get_min(self, fea, rg=None, rg_time=None):
        """ get min value of feature within a range. see **get_max** for
        the meaning of the parameters
        """
        abstract_method()

class DataHandler(object):
    """virtual base class for Data Hanlder. Data Handler contains one or more
    Data class as the data source. And it generate the emperical measure based
    on the data class.
    """
    def get_em(self, rg=None, rg_type='time'):
        """get emperical measure within a range. emeprical measure is used to
        represent the data in this range. For example, it can the probability
        distribution of flow quantization state within and range(*for the model
        free case*), or the markovian trantion probability for the *model based*
        case"""
        abstract_method()


##############################################################
####     For Hard Disk File Generated by fs-simulator   ######
##############################################################
from DataParser import RawParseData
class PreloadHardDiskFile(Data):
    """ for hard Disk File Generated by fs-simulator"""
    def __init__(self, f_name):
        """ data_order can be flow_first | feature_first
        """
        self.f_name = f_name
        self._init()

    def _init(self):
        self.fea_vec, self.fea_name = RawParseData(self.f_name)
        self.zip_fea_vec = None
        self.t = [ float(t) for t in self._get_value_list('start_time')]
        self.min_time = min(self.t)
        self.max_time = max(self.t)
        self.flow_num = len(self.t)

    def _get_fea_idx(self, key):
        return self.fea_name.index(key)

    def _get_value_list(self, key):
        """get a value list for a single key"""
        # fidx = self.fea_name.index(key)
        fidx = self._get_fea_idx(key)
        self.zip_fea_vec = self.zip_fea_vec if self.zip_fea_vec else zip(*self.fea_vec)
        return self.zip_fea_vec[fidx]

    def _get_where(self, rg=None, rg_type=None):
        """get the absolute position of flows records that within the range.
        some times this function is called by outside function thus break
        the interoperability"""
        if not rg: return 0, self.flow_num-1
        if rg_type == 'flow':
            sp, ep = rg
            if sp >= self.flow_num: raise DataEndException()
        elif rg_type == 'time':
            sp = Find(self.t, rg[0]+self.min_time)
            ep = Find(self.t, rg[1]+self.min_time)
            # if rg[1] + self.min_time > self.max_time :
                # import pdb;pdb.set_trace()
                # raise Exception('Probably you set wrong range for normal flows? Go to check DETECTOR_DESC')
            assert(sp != -1 and ep != -1)
            if (sp == len(self.t)-1 or ep == len(self.t)-1):
                raise DataEndException()
        else:
            raise ValueError('unknow window type')
        return sp, ep


    def get_fea_slice(self, fea=None, rg=None, rg_type=None, data_order='flow_first'):
        """this function is to get a chunk of feature vector.
        The feature belongs flows within the range specified by **rg**
        **rg_type** can be ['flow' | 'time' ].
        data_order can be flow_first | feature_first
        """
        sp, ep = self._get_where(rg, rg_type)
        if fea:
            fea_idx = [self.fea_name.index(f) for f in fea]
            if data_order == 'flow_first':
                return [[ v[i] for i in fea_idx] for v in self.fea_vec[sp:ep]]
            elif data_order == 'feature_first':
                return [self._get_value_list(f)[sp:ep] for f in fea]

        if data_order == 'flow_first':
            return self.fea_vec[sp:ep]
        elif data_order == 'feature_first':
            return [fv[sp:ep] for fv in self.zip_fea_vec]

    def get(self, handler, fea, rg, rg_type):
        """ get value list for each feature within the range and return
        the output of handler function in this value.
        **handler** is a function handler that take a list as input
        """
        fea = fea if fea else self.fea_name
        sl = self.get_fea_slice(fea, rg, rg_type)
        zip_sl = zip(*sl)
        res = []
        i = -1
        for f in fea:
            i += 0
            res.append( handler( zip_sl[i] ) )
        return res

    def get_max(self, fea, rg=None, rg_type=None):
        def max_fea(l):
            return max(float(v) for v in l )
        return self.get(max_fea, fea, rg, rg_type)
        # return [max(self._get_value_list(f)[sp:ep]) for f in fea]
        # return [max(float(val) for val in self._get_value_list(f)[sp:ep]) for f in fea]

    def get_min(self, fea, rg=None, rg_type=None):
        def min_fea(l):
            return min(float(v) for v in l )
        return self.get(min_fea, fea, rg, rg_type)
        # sp, ep = self._get_where(rg, rg_type)
        # fea = fea if fea else self.fea_name
        # import pdb;pdb.set_trace()
        # return [min(self._get_value_list(f)[sp:ep]) for f in fea]
        # return [min(float(val) for val in self._get_value_list(f)[sp:ep]) for f in fea]

from DetectorLib import get_feature_hash_list
class HardDiskFileHandler(object):
    """Data is stored as Hard Disk File"""
    def __init__(self, fname, fr_win_size=None, fea_option=None):
        self._init_data(fname)
        self.fr_win_size = fr_win_size
        self.fea_option  = fea_option
        self.direct_fea_list = [ k for k in fea_option.keys() if k not in ['cluster', 'dist_to_center']]
        self.fea_QN = [fea_option['cluster'], fea_option['dist_to_center']] + [fea_option[k] for k in self.direct_fea_list]

        self._cluster_src_ip(fea_option['cluster'])
        self._set_fea_range()

    def _init_data(self, f_name):
        self.data = PreloadHardDiskFile(f_name)

    def _to_dotted(self, ip): return tuple( [int(v) for v in ip.rsplit('.')] )

    def _cluster_src_ip(self, cluster_num):
        src_ip_int_vec_tmp = self.data.get_fea_slice(['src_ip']) #FIXME, need to only use the training data
        src_ip_str_vec = [x[0] for x in src_ip_int_vec_tmp]
        print 'finish get ip address'
        unique_src_IP_str_vec_set = list( set( src_ip_str_vec ) )
        unique_src_IP_vec_set = [self._to_dotted(ip) for ip in unique_src_IP_str_vec_set]
        # print 'start kmeans...'
        # unique_src_cluster, center_pt = KMeans(unique_src_IP_vec_set, cluster_num, DF)
        unique_src_cluster, center_pt = KMedians(unique_src_IP_vec_set, cluster_num, DF)
        self.cluster_map = dict(zip(unique_src_IP_str_vec_set, unique_src_cluster))
        # self.center_map = dict(zip(unique_src_IP_vec_set, center_pt))
        dist_to_center = [DF( unique_src_IP_vec_set[i], center_pt[ unique_src_cluster[i] ]) for i in xrange(len(unique_src_IP_vec_set))]
        self.dist_to_center_map = dict(zip(unique_src_IP_str_vec_set, dist_to_center))

    def _set_fea_range(self):
        """set the global range for the feature list, used for quantization"""
        # set global fea range
        min_dist_to_center = min(self.dist_to_center_map.values())
        max_dist_to_center = max(self.dist_to_center_map.values())

        min_vec = self.data.get_min(self.direct_fea_list)
        max_vec = self.data.get_max(self.direct_fea_list)

        self.global_fea_range = [
                [0, min_dist_to_center] + min_vec,
                [self.fea_option['cluster']-1, max_dist_to_center] + max_vec,
                ]

    def get_fea_list(self):
        return ['cluster', 'dist_to_center'] + self.direct_fea_list

    def get_fea_slice(self, rg=None, rg_type=None):
        """get a slice of feature. it does some post-processing after get feature
        slice from Data. First it get *direct_fea_vec* from data, which is defined
        in **self.direct_fea_list**. then it cluster
        the source ip address, and insert the cluster label and distance to the
        cluster center to the feature list.
        """
        # get direct feature
        direct_fea_vec = self.data.get_fea_slice(self.direct_fea_list, rg, rg_type)
        if not direct_fea_vec:
            raise FetchNoDataException("Didn't find any data in this range")

        # calculate indirect feature
        src_ip_tmp = self.data.get_fea_slice(['src_ip'], rg, rg_type)
        src_ip = [x[0] for x in src_ip_tmp]
        fea_vec = []
        for i in xrange(len(src_ip)):
            ip = src_ip[i]
            fea_vec.append( [self.cluster_map[ip], self.dist_to_center_map[ip]] + [float(x) for x in direct_fea_vec[i]])

        # min_vec = self.data.get_min(self.direct_fea_list, rg, rg_type)
        # max_vec = self.data.get_max(self.direct_fea_list, rg, rg_type)

        # dist_to_center_vec = [self.dist_to_center_map[ip] for ip in src_ip]
        # min_dist_to_center = min(dist_to_center_vec)
        # max_dist_to_center = max(dist_to_center_vec)

        # fea_range = [
        #         [0, min_dist_to_center] + min_vec,
        #         [self.fea_option['cluster']-1, max_dist_to_center] + max_vec,
        #         ]

        # quan_flag specify whether a data need to be quantized or not.
        self.quan_flag = [QUAN] * len(self.fea_option.keys())
        self.quan_flag[0] = NOT_QUAN
        # return fea_vec, fea_range
        return fea_vec

    def get_em(self, rg=None, rg_type=None):
        """get empirical measure"""
        q_fea_vec = self._quantize_fea(rg, rg_type )
        pmf = model_free( q_fea_vec, self.fea_QN )
        Pmb, mpmb = model_based( q_fea_vec, self.fea_QN )
        return pmf, Pmb, mpmb

    def _quantize_fea(self, rg=None, rg_type=None):
        """get quantized features for part of the flows"""
        # fea_vec, fea_range = self.get_fea_slice(rg, rg_type)
        fea_vec = self.get_fea_slice(rg, rg_type)
        q_fea_vec = vector_quantize_states(zip(*fea_vec), self.fea_QN, zip(*self.global_fea_range), self.quan_flag)
        return q_fea_vec

    def hash_quantized_fea(self, rg, rg_type):
        q_fea_vec = self._quantize_fea(rg, rg_type)
        return get_feature_hash_list(q_fea_vec, self.fea_QN)

##############################################################
####  For Hard Disk File Generated by pcap2netflow tool,######
####  for more information about pcap2netflow, please   ######
####  visit https://bitbucket.org/hbhzwj/pcap2netflow   ######
##############################################################
import re
def get_ip_port(val):
    ip_tmp, port = val.rsplit(':')
    ip = ip_tmp[1:-1]
    return ip, port

def ParseData_pcap2netflow(fileName):
    """
    the input is the filename of the flow file that needs to be parsed.
    the ouput is list of dictionary contains the information for each flow in the data. all these information are strings, users need
    to tranform them by themselves
    """
    flow = []
    # FORMAT = dict(start_time=3, end_time=4, src_ip=5, sc_port=6, octets=13, ) # Defines the FORMAT of the data file
    fid = open(fileName, 'r')
    while True:
        line = fid.readline()
        if not line or not line.startswith('FLOW'):
            break
        if line == '\n': # Ignore Blank Line
            continue
        item = re.split('[ ]', line) #FIXME need to be changed if want to use port information
        f = dict()
        for i in xrange(1, len(item)-1, 2):
            f[item[i]] = item[i+1]
        src_ip, src_port = get_ip_port(f['src'])
        dst_ip, dst_port = get_ip_port(f['dst'])
        f['src_ip'] = src_ip
        f['src_port'] = src_port
        f['dst_ip'] = dst_ip
        f['dst_port'] = dst_port
        f['flow_size'] = f['octets']

        flow.append(f.values())
    fid.close()

    if not flow: raise Exception('Not even a flow is found. Are you specifying the right filename?')

    return flow, f.keys()

# from DataFile import PreloadHardDiskFile

class PreloadHardDiskFile_pcap2netflow(PreloadHardDiskFile):
    def _init(self):
        self.fea_vec, self.fea_name = ParseData_pcap2netflow(self.f_name)
        self.zip_fea_vec = None
        self.flow_num = len(self.fea_vec)

# from DataFile import HardDiskFileHandler
class HardDiskFileHandler_pcap2netflow(HardDiskFileHandler):
    def _init_data(self, f_name):
        self.data = PreloadHardDiskFile_pcap2netflow(f_name)


##############################################################
####  For simpleweb.org labled dataset, it is stored in ######
####  mysql server.                                     ######
####  visit http://www.simpleweb.org/wiki/Traces for    ######
####  more information (trace 8)                        ######
##############################################################
try:
    import _mysql
    from socket import inet_ntoa
    from struct import pack
except ImportError as e:
    print '--> [warning] cannot import sql related function, \
            reading for sql server is not supported'
    # print '--> e:', e

def long_to_dotted(ip):
    ip_addr = inet_ntoa(pack('!L', ip))
    return [int(val) for val in ip_addr.rsplit('.')]

get_sec_msec = lambda x: [int(x), int( (x-int(x)) * 1e3)]


# from types import ListType
class SQLFile_SperottoIPOM2009(Data):
    def __init__(self, spec):
        self.db = _mysql.connect(**spec)
        self._init()

    def _init(self):
        # select minimum time
        self.db.query("""SELECT start_time, start_msec FROM flows WHERE (id = 1);""")
        r = self.db.store_result()
        self.min_time_tuple = r.fetch_row()[0]
        self.min_time = float("%s.%s"%self.min_time_tuple)

        self.db.query("""SELECT MAX(id) FROM flows;""")
        r = self.db.store_result()
        self.flow_num = int(r.fetch_row()[0][0])

        self.db.query("""SELECT end_time, end_msec FROM flows WHERE (id = %d);"""%(self.flow_num))
        r = self.db.store_result()

        self.max_time_tuple = r.fetch_row()[0]
        self.max_time = float("%s.%s"%self.max_time_tuple)

    def _get_sql_where(self, rg=None, rg_type=None):
        if rg:
            if rg_type == 'flow':
                SQL_SEN_WHERE = """ WHERE ( (id >= %f) AND (id < %f) )""" %tuple(rg)
                if rg[0] > self.flow_num:
                    raise DataEndException("reach data end")

            elif rg_type == 'time':
                st = get_sec_msec (rg[0] + self.min_time)
                ed = get_sec_msec (rg[1] + self.min_time)
                SQL_SEN_WHERE = """ WHERE ( (start_time > %d) OR ( (start_time = %d) AND (start_msec >= %d)) ) AND
                             ( (end_time < %d) OR ( (end_time = %d) and (end_msec < %d) ) )""" %(st[0], st[0], st[1], ed[0], ed[0], ed[1])

                # print 'rg[0]', rg[0]
                # print 'self.min_time', self.min_time
                # print 'current time, ', rg[0] + self.min_time
                # print 'self.maxtime', self.max_time
                if rg[0] + self.min_time > self.max_time:
                    raise DataEndException("reach data end")
            else:
                print 'rg_type', rg_type
                raise ValueError('unknow window type')
        else:
            SQL_SEN_WHERE = ""
        return SQL_SEN_WHERE

    def get_max(self, fea, rg=None, rg_type=None):
        fea_str = ['MAX(%s)'%(f) for f in fea]
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea_str)) + self._get_sql_where(rg, rg_type) + ";"
        self.db.query(SQL_SEN)
        r = self.db.store_result().fetch_row(0)
        return r[0]

    def get_min(self, fea, rg=None, rg_type=None):
        fea_str = ['MIN(%s)'%(f) for f in fea]
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea_str)) + self._get_sql_where(rg, rg_type) + ";"
        self.db.query(SQL_SEN)
        r = self.db.store_result().fetch_row(0)
        return r[0]

    def get_fea_slice(self, fea, rg=None, rg_type=None):
        """this function is to get a chunk of feature vector.
        The feature belongs flows within the range specified by **rg**
        **rg_type** can be ['flow' | 'time' ].
        """
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea)) + self._get_sql_where(rg, rg_type) + ";"
        # print SQL_SEN
        self.db.query(SQL_SEN)
        result = self.db.store_result().fetch_row(0)
        # return [line[0] for line in result] if len(fea) == 1 else result
        return result

class SQLDataFileHandler_SperottoIPOM2009(HardDiskFileHandler):
    """"Data File wrapper for SperottoIPOM2009 format. it is store in mysql server, visit
    http://traces.simpleweb.org/traces/netflow/netflow2/dataset_description.txt
    for more information"""
        # self.quan_flag[ fea_option.keys().index('cluster')] = NOT_QUAN
    def _init_data(self, db_info):
        self.data = SQLFile_SperottoIPOM2009(db_info)

    def _to_dotted(self, ip): return long_to_dotted(int(ip))

