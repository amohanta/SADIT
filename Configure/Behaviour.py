#!/usr/bin/env python
"""This file defines the behaviour"""
from __future__ import print_function, division, absolute_import
# from sadit.util import abstract_method
from random import randint
from .mod_util import RandDist

# class Behaviour(object):
#     """  Abstract Class For Behaviour """
#     def behave(self):
#         """  the Behaviour
#         """
#         abstract_method()

from random import expovariate as exponential
class DTMCBehaviour(object):
    """ Discrete Time Markov Chain

    Parameters
    ------------------
    P : list of list
        transition probability
    states : list of any type
        list of states
    interval : float
        interval between two transitions

    Attributes
    --------------------
    cs : int
        current state
    """
    def __init__(self, P, states, interval):
        # Behaviour.__init__(self)

        self.interval = interval
        self.P = P
        self.states = states

        sn = len(states)
        self.cs = randint(0, sn-1) # cs: current state

    def get_new_state(self):
        """  Generate next state accoding to transition probability """
        return RandDist(self.P[self.cs])
        # return RandDist(self.P) # FIXME use stationary prob

    def get_interval(self):
        """  accessor for self.interval """
        return self.interval

    def behave_with_profile(self, start, profile, func):
        """  behave according to profile

        Parameters
        ---------------
        start : float
            start time
        profile : tuple of tuple
            has the same meaning as `profile` in fs. The first tuple are the
            the durations, the second tupleself are the number of runs.
            specify

        Returns
        --------------
        None

        """
        for dur, num in zip(*profile):
            end = start + dur
            for i in xrange(num):
                self.behave(start, end, func)
            start = end

    def behave(self, start, end, func):
        """  call func during `start` and `end`.

        Parameters
        ---------------
        start, end : float
            start and end time
        func : function handle
            the function will be called during each stage. it should has the
            prototype:
                func(r_start, r_end, state)

        Returns
        --------------
        None
        """
        t = start
        while True:
            self.cs = self.get_new_state()
            inter = self.get_interval()
            if t + inter > end:
                break
            func(r_start=t, r_end=t+inter, state=self.states[self.cs])
            t += inter


def get_embed_MC(P):
    """  Calculate Embedded Markov Chain of a Continuous Time M.C>

    Parameters
    ---------------
    P : nxn matrix
        number with position (i, j) is the rate of possion process that
        transition (i, j) will happen

    Returns
    --------------
    EP : nxn matrix
        transition matrix of embedded MC
    v : nx1 list
        v[i] is the rate of leave state i
        v[i] = sum(P[i][j] for j noteq i)

    Examples
    ---------------
    >>> P = [[1, 2], [4, 3]]
    >>> EP, v = get_embed_MC(P)
    >>> EP
    [[0, 1.0], [1.0, 0]]
    >>> v
    [2, 4]
    """
    n = len(P)
    v = [sum(pl) - pl[i] for i, pl in zip(range(n), P)]
    EP = [[0] * n for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j : continue
            EP[i][j] = P[i][j] * 1.0 / v[i]
    return EP, v

class CTMCBehaviour(DTMCBehaviour):
    """ Continuous Time Markoc Chain

    Parameters
    ------------------
    P : list of list
        rate matrix
    states : list of any type
        list of states

    Attributes
    --------------------
    cs : int
        current state
    """
    def __init__(self, P, states):
        super(CTMCBehaviour, self).__init__(P, states, 0)
        self.embed_P, self.v = get_embed_MC(P)

    def get_new_state(self):
        """  generate new state accoding to transition probability of embedded
        markov chain
        """
        return RandDist(self.embed_P[self.cs])

    def get_interval(self):
        """  generate interval between two consequent transitions accoding to
        expontial distribution
        """
        val = exponential(self.v[self.cs])
        return val

# try:
#     import numpy as np
# except:
#     print('[Warning] MultiServer Detector requires numpy')

# class MVBehaviour(MarkovBehaviour):
# class MVBehaviour(DTMCBehaviour):
#     """
#     Description:
#         - will make choice every other t time.
#         - the generators is selected according to multi-variate distribution

#     Required Variables:
#         - states: states for all possible value. it is a list of list,
#             the first dimension is the id of servers, the second dimension is the possible
#             for type of generator for a specific server.
#         - joint_dist: the joint distribution for indicator variable to each server.

#     The traffic is generated according to multi-variable distribution
#     if there are m servers, then the joint distribution will be m dimension
#     matrix. For each component, there are n possible values. So we need m*n
#     possible generators
#     """
#     def __init__(self, joint_dist, interval, generator_states):
#         self.joint_dist = joint_dist
#         self.states = generator_states
#         self.interval = interval
#         self.record = []

#     @property
#     def dim(self): return self.joint_dist.shape

#     @property
#     def srv_num(self): return len(self.dim)

#     def get_sample(self):
#         """generate a sample according to joint distribution"""
        # assert(np.sum(self.joint_dist) == 1 )
#         assert( abs( np.sum(self.joint_dist) - 1) < 1e-3)
#         x = RandDist( self.joint_dist.ravel() )
#         idx = np.unravel_index(x, self.dim)
#         return idx

#     def get_new_state(self):
#         ns = self.get_sample()
#         self.record.append(ns)
#         return ns

#     def get_interval(self):
#         return self.interval
        # return exponential(1.0 / self.interval)

#     def _sample_freq(self):
#         freq = np.zeros(self.dim)
#         for r in self.record:
#             freq[r] += 1
#         freq /= np.sum(freq)
        # print 'freq, ', freq

if __name__ == "__main__":
    import doctest
    doctest.testmod()
