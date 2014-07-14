# from random import randint
from __future__ import print_function, division, absolute_import

### -- [2012-03-04 12:12:42] add binary_search
### -- [2012-03-26 14:01:02] add docstring for each function.

def IN(*val_list):
    """Generate a string command that import object variables
    to locals() in the class methods"""
    return ";".join(['%s=self.%s'%(v, v) for v in val_list])

def OUT(*val_list):
    """Generate a string command that export object variables
    to locals() in the class methods"""
    return ";".join(['self.%s=%s'%(v, v) for v in val_list])

def binary_search(a, x, lo=0, hi=None):
    """
    Find the index of largest value in a that is smaller than x.
    a is sorted Binary Search
    """
    # import pdb;pdb.set_trace()
    if hi is None: hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        midval = a[mid]
        if midval < x:
            lo = mid + 1
        elif midval > x:
            hi = mid
        else:
            return mid
    return hi-1

Find = binary_search

import types
def Load(var):
    '''Load is useful when the some elements in var is specified as random value.
    for example, if the var is ['rand(1)', 1], var[0] will be different random
    value at each time.'''
    t = type(var)
    if t == types.TupleType or t == types.ListType:
        return [Load(x) for x in var]
    elif t == types.DictType:
        res = dict()
        for k, v in var.iteritems():
            # If cannot properly loaded, use origianl value
            try:
                res[k] = Load(v)
            except Exception:
                res[k] = v
        return res
    elif t == types.StringType:
        return eval(var)
    elif t == types.FloatType or t == types.IntType:
        return var
    else:
        raise TypeError('unknown type of var')

def Dump2Txt(var, fname, op):
    """Dump2Txt will dump the variable to text file for use of other programs like Matlab.

    - *fname* : is the name for output file
    - *op* : is a option flag, ::

        if op[0:2] == '1d':
            m = len(var)
            for i in xrange(m): fid.write("%f "%(var[i]))
            fid.write('\\n')
        elif op[0:2] == '2d':
            if op[2:] == 'np': m, n = var.shape
            elif op[2:] == 'list':
                m = len(val)
                m = len(val[0])
            else:
                raise ValueError('unknown op')

            for i in xrange(m):
                for j in xrange(n):
                    fid.write("%s "%(var[i,j]))
                fid.write("\\n")


    """
    fid = open(fname, 'w')
    if op[0:2] == '1d':
        m = len(var)
        for i in xrange(m): fid.write("%f "%(var[i]))
        fid.write('\n')
    elif op[0:2] == '2d':
        if op[2:] == 'np': m, n = var.shape
        elif op[2:] == 'list':
            m = len(var)
            m = len(var[0])
        else:
            raise ValueError('unknown op')

        for i in xrange(m):
            for j in xrange(n):
                fid.write("%s "%(var[i,j]))
            fid.write("\n")
    else:
        raise ValueError('unknow op')

    fid.close()


try:
    import numpy as np
    from numpy import arange, pi, linspace
except ImportError:
    print('no numpy')

import inspect
def PrintVar(namespace, outputFile = ''):
    '''Print all variances in the namespace into .py file'''
    fid = -1
    if outputFile != '':
        fid = open(outputFile, 'w')
    for k, v in namespace.iteritems():
        if k.startswith("__")==0 and k not in imports:
            # print 'type(v), ', type(v)
            if type(v) == types.StringType:
                expr ='%s = \'%s\'\n' %(k, str(v))
            elif type(v) == types.FunctionType:
                expr = inspect.getsource(v) + '\n'
                # removing the leading blankspace
                leadingSpace = expr.rfind('def')
                if leadingSpace != 0 and leadingSpace != -1:
                    srcLine = inspect.getsourcelines(v)
                    expr = ''
                    for line in srcLine[0]:
                        expr = expr + line[leadingSpace:]
                if leadingSpace != -1:
                    GetFuncName = lambda s: s[s.find('def')+4:s.find('(')]
                    funcName = GetFuncName(expr)
                    if funcName != k: expr += '\n%s = %s\n' %(k, funcName)

            elif type(v) == types.BuiltinFunctionType:
                module =inspect.getmodule(v)
                expr = 'from %s import %s\n' %(module.__name__,  v.__name__)
            elif type(v) == types.ModuleType:
                expr = 'import %s as %s\n' %(v.__name__, k)
            elif type(v) == np.ndarray:
                expr = k + ' = ' + str(v.tolist()) + '\n'
            else:
                expr = '%s = %s\n' %(k, str(v))
            if fid == -1:
                print(expr,)
                continue
            fid.write( expr )
    if fid != -1:
        fid.close()


def PrintModelFree(mfIndi, mbIndi):
    '''Print the ModelFree Derivative which is not nan value'''
    # mfIndi = ModelFreeDetectAnoType()
    # mbIndi = ModelBaseDetectAnoType()
    for i in xrange(len(mfIndi)):
        if not np.isnan( mfIndi[i]):
            print('[%d]\t%f'%(i, mfIndi[i]))
    print('\n')


def PrintModelBase(mbIndi):
    '''print the model based derivative which is not nan value.'''
    m, n = mbIndi.shape
    for i in xrange(m):
        for j in xrange(n):
            if not np.isnan(mbIndi[i,j]):
                print('[%d, %d]\t%f' %(i, j, mbIndi[i,j]))
    print('\n')


def abstract_method():
    """ This should be called when an abstract method is called that should have been
    implemented by a subclass. It should not be called in situations where no implementation
    (i.e. a 'pass' behavior) is acceptable. """
    raise NotImplementedError('Method not implemented!')

def FROM_CLS(*val_list):
    return ";".join(['%s=self.%s'%(v, v) for v in val_list])

def TO_CLS(*val_list):
    return ";".join(['self.%s=%s'%(v, v) for v in val_list])


class DataEndException(Exception):
    pass

class FetchNoDataException(Exception):
    pass



QUAN = 1
NOT_QUAN = 0

# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

def zeros(s):
    if len(s) == 1:
        return [0] * s[0]
    elif len(s) == 2:
        return [[0 for i in xrange(s[1])] for j in xrange(s[0])]
    else:
        raise Exception('unknown size in zeros')


# import inspect
def get_help_docs(dic):
    docs = []
    for k, v in dic.iteritems():
        doc  = inspect.getdoc(v)
        comp_doc = "%s %s"%(v.__name__, doc.rsplit('\n')[0]) \
                if doc else v.__name__
        docs.append("'%s': %s"%(k, comp_doc))

    return docs

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)


def load_para(f_name, encap=None, allow_types=(list, str, dict, float, int),
        kwargs={}):
    """load parameters.

    Parameters:
    ----------------------
    f_name : str
        is the path of the configuration file
    allow_types : tuple
        specify the allowed types in parameter file.
    encap : function
        is the additional operation done to the data, for example,
        the default value encap=Namespace is to change parameters from dict
        to Namespace class.
    kwargs : dict
        contains some additional parameters
    """
    ss = kwargs
    execfile(f_name, ss)
    if allow_types is not None:
        res = dict()
        for k, v in ss.iteritems():
            for t_ in allow_types:
                if isinstance(v, t_):
                    res[k] = v
                    break
        ss = res
    del ss['__builtins__']

    return ss if encap is None else encap(ss)


def check_pipe_para(para):
    from numpy import loadtxt
    """

    Parameters
    ---------------
    para : list or str
        if para is list, return itself, if para is str starts with "< " and
            follows by a file name, load the parameters in the txt

    Returns
        para : lsit
            a list of parameters
    --------------
    """
    if isinstance(para, str) and para.startswith('< '):
        f_name = para.split('< ')[0]
        return loadtxt(f_name)
    return para


import csv
def save_csv(f_name, names, *args):
    with open(f_name, 'w') as f:
        w = csv.writer(f)
        valid_idx = [i for i in xrange(len(args)) if args[i] is not None]
        valid_names = [names[i] for i in valid_idx]
        valid_args = [args[i] for i in valid_idx]
        w.writerow(valid_names)
        w.writerows(zip(*valid_args))


import collections
def mkiter(e):
    """make e iteratable"""
    if not isinstance(e, collections.Iterable):
        return [e]
    else:
        return e

# import numpy as np
def meval(cmd):
    """to make arange, pi and linespace to be able to used directly in eval()"""
    return eval(cmd)

def del_none_key(dt):
    """delete key whose value is None"""
    res = dict()
    for k, v in dt.iteritems():
        if v is not None:
            res[k] = v
    return res


def update_not_none(d1, d2):
    for k, v in d2.iteritems():
        if v is not None:
            d1[k] = v

# class List(object):
#     """ List that support add with another List and division over a float or int.

#     Examples
#     -------------
#     >>> a = List([1, 2, 3])
#     >>> b = List([2, 3, 4])
#     >>> c = a + b
#     >>> d = a / 2
#     """
#     def __init__(self, d):
#         self.d = d
#         self.n = len(d)

#     def __add__(self, val):
#         if val is None:
#             return self

#         for i in xrange(self.n):
#             self.d[i] = self.d[i] + val[i]
#         return self

#     def __div__(self, val):
#         for i in xrange(self.n):
#             self.d[i] /= val
#         return self

#     def __str__(self):
#         return str(self.d)

#     def __getitem__(self, k):
        # return self.d[k]

##############################
# Data Storage and Load
###############################
try:
    import cPickle as pickle
except ImportError:
    import pickle
import gzip
proto = pickle.HIGHEST_PROTOCOL
def zdump(obj, f_name):
    f = gzip.open(f_name,'wb', proto)
    pickle.dump(obj,f)
    f.close()

def zload(f_name):
    f = gzip.open(f_name,'rb', proto)
    obj = pickle.load(f)
    f.close()
    return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()

