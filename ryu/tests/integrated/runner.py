# Copyright (C) 2012 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from nose.tools import ok_, eq_

from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process, Queue
import time

from mininet.net import Mininet
from mininet.node import RemoteController

from ryu.tests.integrated.ovs12 import OVS12KernelSwitch


RYU_HOST = '127.0.0.1'
RYU_PORT = 6633
TIMEOUT = 15
WRAPPER = './tools/with_venv.sh'
RYU_MGR = './bin/ryu-manager'


class TestWithOVS12(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mn = Mininet()
        cls.mn.addController(controller=RemoteController,
                              ip=RYU_HOST, port=RYU_PORT)
        for controller in cls.mn.controllers:
            controller.start()

        s1 = cls.mn.addSwitch('s1', cls=OVS12KernelSwitch)
        s1.start(cls.mn.controllers)

        h1 = cls.mn.addHost('h1', ip='0.0.0.0/0')
        h2 = cls.mn.addHost('h2', ip='0.0.0.0/0')

        for h in (h1, h2):
            link = cls.mn.addLink(h, s1)
            s1.attach(link.intf2)

    @classmethod
    def tearDownClass(cls):
        cls.mn.stop()

    def _run_ryu_manager_and_check_output(self, app):
        cmd = [RYU_MGR, app]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        print "ryu-manager's pid is %s" % p.pid

        start = time.time()
        while True:
            if time.time() - start > TIMEOUT:
                raise Exception('TIMEOUT')

            if p.poll() != None:
                raise Exception('Another ryu-manager already running?')

            line = p.stdout.readline().strip()
            if line == '':
                time.sleep(1)
                continue

            print line
            if line.find('TEST_FINISHED') != -1:
                ok_(line.find('Completed=[True]') != -1)
                p.terminate()
                p.communicate()  # wait for subprocess is terminated
                break

    def test_add_flow_v10(self):
        app = 'ryu/tests/integrated/test_add_flow_v10.py'
        self._run_ryu_manager_and_check_output(app)
