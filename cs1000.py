#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cs1000: Module for communicating with the Minolta CS-1000

Copyright (C) 2012-2014 Ivar Farup

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import serial
import logging
import numpy as np


class CS1000:
    """
    Class for managing the Minolta CS-1000.
    """
    def __init__(self, port=None, baud_rate=19200, loglevel=logging.INFO):
        """
        Create CS1000 instance and connect if port is given.
        """
        self.results = dict()
        self.com = None
        self.remote = False
        if port:
            self.connect(port, baud_rate)
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=loglevel)

    def get_connected(self):
        """
        Is the CS1000 connected?
        """
        return not self.com is None

    def connect(self, port, baud_rate=19200):
        """
        Connect to the given serial port.
        """
        if self.remote:         # Turn off remote control if on.
            self.set_remote(False)
        self.com = serial.Serial(port, baudrate=baud_rate)
        logging.info('Connected to port ' + str(port) +
                     ' with baud rate ' + str(baud_rate))

    def disconnect(self):
        """
        Disconnect from the serial port.
        """
        if self.remote:         # Turn off remote control if on.
            self.set_remote(False)
        self.com = None
        logging.info('Disconnected')

    def get_remote(self):
        """
        Is remote control on?
        """
        return self.remote

    def set_remote(self, on=True):
        """
        Turn remote control on/off.
        """
        if on:
            if not self.remote:
                logging.info('Turning on remote control')
                logging.debug('Sent:     RMT,1')
                self.com.write(b'RMT,1\n')
                ans = self.com.readline().decode('utf-8')
                logging.debug('Received: ' + ans.strip())
                self.remote = True
        else:
            if self.remote:
                logging.info('Turning off remote control')
                logging.debug('Sent:     RMT,0')
                self.com.write(b'RMT,0\n')
                self.remote = False
                self.com = serial.Serial()

    def measure(self):
        """
        Perform measurement and read data according to protocol.
        """
        logging.info('Measuring')
        if not self.remote:
            self.set_remote(True)

        logging.debug('Sent:     MES,1')
        self.com.write(b'MES,1\n')
        ans = self.com.readline().decode('utf-8')
        logging.debug('Received: ' + ans.strip())
        ans = self.com.readline().decode('utf-8')
        logging.debug('Received: ' + ans.strip())

        logging.debug('Sent:     BDR,1,0,0')
        self.com.write(b'BDR,1,0,0\n')
        ans = self.com.readline().decode('utf-8')
        logging.debug('Received: ' + ans.strip())

        logging.debug('Sent:     &')
        self.com.write(b'&\n')
        ans = self.com.readline().decode('utf-8')
        logging.debug('Received: ' + ans.strip())
        ans = ans.split(',')
        self.results['Le2'] = float(ans[0])
        self.results['Lv2'] = float(ans[1])
        self.results['X2'] = float(ans[2])
        self.results['Y2'] = float(ans[3])
        self.results['Z2'] = float(ans[4])
        self.results['x2'] = float(ans[5])
        self.results['y2'] = float(ans[6])
        self.results['u2'] = float(ans[7])
        self.results['v2'] = float(ans[8])
        self.results['T2'] = ans[9]
        self.results['Duv2'] = ans[8]

        logging.debug('Sent:     BDR,1,1,0')
        self.com.write(b'BDR,1,1,0\n')
        ans = self.com.readline().decode('utf-8')
        logging.debug('Received: ' + ans.strip())

        logging.debug('Sendt:     &')
        self.com.write(b'&\n')
        ans = self.com.readline().decode('utf-8')
        logging.debug('Received: ' + ans.strip())
        ans = ans.split(',')
        self.results['Le10'] = float(ans[0])
        self.results['Lv10'] = float(ans[1])
        self.results['X10'] = float(ans[2])
        self.results['Y10'] = float(ans[3])
        self.results['Z10'] = float(ans[4])
        self.results['x10'] = float(ans[5])
        self.results['y10'] = float(ans[6])
        self.results['u10'] = float(ans[7])
        self.results['v10'] = float(ans[8])
        self.results['T10'] = ans[9]
        self.results['Duv10'] = ans[8]

        logging.debug('Sent:     BDR,0,0,0')
        self.com.write(b'BDR,0,0,0\n')
        ans = self.com.readline().decode('utf-8')
        logging.debug('Received: ' + ans.strip())
        spectrum = []
        for i in range(15):
            logging.debug('Sent:     &')
            self.com.write(b'&\n')
            ans = self.com.readline().decode('utf-8')
            logging.debug('Received: ' + ans.strip())
            ans = ans.split(',')
            for a in ans:
                spectrum.append(float(a.strip()))
        spectrum = np.array(spectrum)
        lambd = 380 + np.arange(len(spectrum))
        spectrum = np.array([lambd, spectrum]).T
        self.results['spectrum'] = np.array(spectrum)
        logging.info('Measuring completed')

    def get_results(self):
        """
        Pass the results as a dict().
        """
        return self.results
