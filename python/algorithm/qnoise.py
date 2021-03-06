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

# @package algorithm

from abc import abstractmethod

import numpy as np


class QLearner:
    """
    Represent a QLearner.
    ase class for QValue based algorithms.
    """

    # TODO:: parametros da funcao nao sao os mesmos dos da doc.
    def __init__(self, alpha, lookback, hist_weight):
        """
        ## CTOR
        @param alpha Weight most recent values
        @param lookback How many qvalues we should kept in history. Integer.
        @param hist_weight Weight of the last QValues. Array of [nth, n-1th, n-2th, ..., 1st]


        @param noise_weight Weight of SINR
        @param reward_callback
        """
        self._qval = [0.0] * len(hist_weight)

        ##
        self._l = lookback 
        self._a = alpha
        self._h = hist_weight

    @abstractmethod
    def _reward(self, data):
        """
        Calculate the reward based on data.
        Should be implemented by the derived class.
        @param data
        """
        pass

    def get_q_val(self):
        """
        Return the current QValue.
        @return Last QValue.
        """
        return self._qval[-1]


    def add_q_val(self, value):
        """
        Append a value to QValues kept.
        @param value Value to append.

        Ex: lookback = 3;
            t=1;    Channel: [Qval t=1]
            t=2;    Channel: [Qval t=1][Qval t=2]
            t=3;    Channel: [Qval t=1][Qval t=2][Qval t=3]
            t=4;    Channel: [Qval t=2][Qval t=3][Qval t=4]
            t=5;    Channel: [Qval t=3][Qval t=4][Qval t=5]
        """
        self._qval.append(value)

        if len(self._qval) > self._l:
            self._qval.pop(0)

    def calc_q_val(self, data):
        """
        Calculate the QValue for the given sensing result.
        @param data Data utilized in the QValue calculation.
        """
        reward = self._reward(data)

        # Multiply each element on hist_weight by each column on historic table
        #  Ex: hist_weight = [0.2, 0.35, 0.45]
        #        historic table = [[0.4, 0.8, 0.6, 0.3], [0.6, 0.3, 0.5, 0.8], [0.5, 0.4, 0.4, 0.8]
        #  Calc:
        #        Channel 1:    0.2 * 0.4 + 0.35 * 0.6 + 0.45 * 0.5 
        #        Channel 2:    0.2 * 0.8 + 0.35 * 0.3 + 0.45 * 0.4
        #        Channel 3:    0.2 * 0.6 + 0.35 * 0.5 + 0.45 * 0.4
        #        Channel 4:    0.2 * 0.3 + 0.35 * 0.8 + 0.45 * 0.8
        hist_total = sum([q*h for q,h in zip(self._qval, self._h)])

        # Calculate the QValue
        # qvalue = alpha * reward + (1-alpha) * historic
        qval = self._a * reward + (1 - self._a) * hist_total

        self.add_q_val(qval)


class QChannel:
    """
    Considers both RSSI and Historic occupancy to calculate the channel QValue.
    """

    class QNoiseLearner(QLearner):
        """
        Internal class that implements thq Noise QValue.
        """

        def __init__(self, alpha, lookback, hist_weight):
            """
            CTOR
            @param alpha Weight of the most recent reward. Integer.
            @param lookback How many qvalues we should kept in history. Integer.
            @hist_weight Weights of last N QValues. List of Integer.
            """
            QLearner.__init__(self, alpha=alpha, lookback=lookback, hist_weight=hist_weight)


        def _reward(self, data):
            """
            Inherited from parrent
            Calculate the reward based on a simple table that maps a RSSI value to a reward.
            @param data
            @return
            """
            # Sanity check
            if all(rssi == 1 or rssi == 0 for rssi, dec in data):
                raise ValueError("RSSI is all 0s and 1s. It this right?")

            def sinr_contribution(rssi):
                contribution = [(10e-7, 1), (10e-6, 0.75), (3 * 10e-6, 0.50), (6 * 10e-6, 0.25), (10e-4, 0.10)]
                for check, value in contribution:
                    if rssi < check:
                        return value
                return 0.0

            rssi = 0.0
            count = 0


            for _rssi, _dec in data:
                if _dec == 0:
                    rssi += _rssi
                    count += 1

            if count:
                return sinr_contribution(rssi / count)
            else:
                return 0.0


    class QHistoricLearner(QLearner):
        """
        Internal class that implements the Historic Occupancy QValue.
        """

        def __init__(self, alpha, lookback, hist_weight):
            """
            CTOR
            @param alpha Weight of the most recent reward. Integer.
            @param lookback How many qvalues we should kept in history. Integer.
            @hist_weight Weights of last N QValues. List of Integer.
            """
            QLearner.__init__(self, alpha=alpha, lookback=lookback, hist_weight=hist_weight)


        def _reward(self, data):
            """
            Inherited from parent.
            Calculated the reward by dividing the number of 'idles decisions' by the total of decisions.
            @param data
            """

            # Sanity check
            if not all(d == 1 or d == 0 for s, d in data ):
                raise ValueError("Decisions must be all 0s and 1s")

            idle = np.sum([1-d for s, d in data])
            return float(idle) / len(data)

    def __init__(self, h_weight, h_data, n_weight, n_data):
        """
        CTOR
        @param h_weight Weight of Historic QLearner instance.
        @param h_data Historic QLearner instance data. Tuple: (alpha, lookback, hist_weight).
        @param n_weight Weight of Noise QLearner instance.
        @param n_data Noise QLearner instance data. Tuple: (alpha, lookback, hist_weight).
        """

        self._historic = QChannel.QHistoricLearner(alpha=h_data[0],
                                                   lookback=h_data[1],
                                                   hist_weight=h_data[2]
                                                   )

        self._noise = QChannel.QNoiseLearner(alpha=n_data[0],
                                             lookback=n_data[1],
                                             hist_weight=n_data[2]
                                             )

        self._hw = h_weight
        self._nw = n_weight

    def get_q_val(self):
        """
        @return
        """
        print' historic: ', self._historic.get_q_val()
        print' noise:    ', self._noise.get_q_val()
        return self._hw * self._historic.get_q_val() + self._nw * self._noise.get_q_val()


    def calc_q_val(self, final_decision, usensing):
        """
        @param final_decision Final decision regarding channel occupancy.
        @param usensing Array of tuples (dec, rssi).
        """

        # calculate RSSI only if channel if idle
        if final_decision == 0:
            self._noise.calc_q_val(usensing)

        self._historic.calc_q_val(usensing)


class QNoise:
    """
    QNoise algorithm.
    Keeps the qvalue for all channels created.
    """

    def __init__(self, n_weight, n_data, h_weight, h_data):
        """
        CTOR
        @param n_weight
        @param n_data
        @param h_weight
        @param h_data
        """
        self._channel = {}

        # Weight of noise in the QChannel object
        self._n_weight = n_weight
        self._n_data = n_data

        # Weight of historic in the QChannel object
        self._h_weight = h_weight
        self._h_data = h_data


    def evaluate(self, matrix):
        """
        Calculate QValue for all channels.
        @param matrix Each row represents a channel. columns have the following semantics.
        [Channel][Array tuples (RSSI,decisions)].
        <---1---><---parameter udecisions------>
        """
        channel_list = []
        qvalue_list = []

        # Decides if the channel  is occupied/vacant based on udecisions
        def data_to_final_decision(dec_tuples):
            occupied = 0
            vacant = 0

            occupied = np.sum(1 if dec else 0 for rssi, dec in dec_tuples)
            vacant = np.sum(0 if dec else 1 for rssi, dec in dec_tuples)

            return 1 if occupied > vacant else 0

        for ch_data in matrix:
            ch = ch_data[0]

            # Check if ch is in channel dictionary
            if ch not in self._channel:
                self._channel[ch] = QChannel(h_weight=self._h_weight,
                                             h_data=self._h_data,
                                             n_weight=self._n_weight,
                                             n_data=self._n_data
                                             )

            # Calculate QValue
            self._channel[ch].calc_q_val(final_decision=data_to_final_decision(ch_data[1]),
                                         usensing=ch_data[1]
                                         )

            # Use leonard's format
            channel_list.append(ch)
            qvalue_list.append(self._channel[ch].get_q_val())

        # Return expect format
        return [channel_list, qvalue_list]
        
#if __name__ == '__main__':
#
#    alpha = 0.3
#    hist_weight = [0.2, 0.35, 0.45]
#    noise_weight = 0.5
#
#    l = QNoise( n_weight = 0.5, n_data = ( 0.5, 3, hist_weight ), h_weight = 0.5, h_data = ( 0.5, 3, hist_weight ) )
#
#    matrix = ([1,0,[(1, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (0, 0.0001)]], )
#
#    print l.evaluate( matrix )
