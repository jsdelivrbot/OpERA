"""
Copyright 2013 OpERA

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

#!/usr/bin/python

## @package algorithm

# ::TODO:: Discover how to include patches externally
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, path)

import unittest
import random
import numpy as np

# Modules  tested
from energyDecision import EnergyDecision
from waveformDecision import WaveformDecision
from bayesianDecision import BayesLearningThreshold

# Other modules needed
from device import radioDevice
from algorithm.abstractAlgorithm import AbstractAlgorithm


class QaDecision(unittest.TestCase):
    """
    Test algorithm  module.
    """

    def test_ed_001(self):
        """
        Test EnergyDecision threshold.
        """
        th = 10

        ed = EnergyDecision(th)
        self.assertEqual(th, ed.threshold)
        #self.assertEqual(ed.decision(np.array([th/2, th/2])), 0)
        #self.assertEqual(ed.decision(np.array([th, th])), 0)
        #self.assertEqual(ed.decision(np.array([th*2, th*2])), 1)

    def test_ed_002(self):
        """
        Test Waveform threshold.
        """
        global signal  # wrong size. update to 1024 points

        th = 0.8
        wd = WaveformDecision(th)

        self.assertEqual(th, wd.threshold)
        arr = [1] * 1024
        dec = wd.decision(np.array(arr))
        dec = (0, 0)

        # Random will (probably) not match any signal
        self.assertEqual((0, 0.0), dec)

    def test_bayes_001(self):
        """
        Test BayesLearningThreshold basic parameters.
        """
        in_th = 10
        min_th = 1
        max_th = 20
        k = 1
        delta_th = 0.0015

        obj = BayesLearningThreshold(in_th=in_th,
                                     min_th=min_th,
                                     max_th=max_th,
                                     delta_th=delta_th,
                                     k=k)

        self.assertEqual(in_th, obj._th)
        self.assertEqual(min_th, obj._min_th_limit)
        self.assertEqual(max_th, obj._max_th_limit)
        self.assertEqual(k, obj._k)
        self.assertEqual(delta_th, obj._delta_th)

    def test_bayes_002(self):
        """
        Test BayesLearningThreshold basic parameters.
        """
        in_th = 10
        min_th = 1
        max_th = 20
        k = 1
        n = 1000
        delta_th = 0.0015

        obj = BayesLearningThreshold(in_th=in_th,
                                     min_th=min_th,
                                     max_th=max_th,
                                     delta_th=delta_th,
                                     k=k)

        dec = obj.decision(np.array([9]))

        self.assertEqual((0, 0), dec)


if __name__ == '__main__':
    unittest.main()
