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

# vim: tabstop=4 shiftwidth=4 softtabstop=4

import unittest
import logging
from nose.tools import *
from ryu.ofproto.nx_match import *
from ryu.lib import mac

LOG = logging.getLogger('test_nx_match')


class TestClsRule(unittest.TestCase):
    """ Test case for nx_match.ClsRule
    """

    c = ClsRule()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        # flow
        flow = self.c.flow
        eq_(0, flow.in_port)
        eq_(mac.DONTCARE, flow.dl_src)
        eq_(mac.DONTCARE, flow.dl_dst)
        eq_(0, flow.dl_type)
        eq_(0, flow.nw_tos)

        # wildcards
        wc = self.c.wc
        eq_(0, wc.tun_id_mask)
        eq_(FWW_ALL, wc.wildcards)

    def test_set_in_port(self):
        a_wildcards = 0b111111111111
        b_wildcards = 0b111111111110
        port = 0xffff

        self.c.wc.wildcards = a_wildcards
        self.c.set_in_port(port)

        eq_(b_wildcards, self.c.wc.wildcards)
        eq_(port, self.c.flow.in_port)

    def test_set_dl_dst(self):
        a_wildcards = 0b111111111111
        b_wildcards = 0b111111110101
        dl_dst = '\xe4\xc8\x4d\xb8\x97\x9b'

        self.c.wc.wildcards = a_wildcards
        self.c.set_dl_dst(dl_dst)

        eq_(b_wildcards, self.c.wc.wildcards)
        eq_(dl_dst, self.c.flow.dl_dst)

    def _test_set_dl_dst_masked(self, a_wildcards, b_wildcards,
                                a_dl_dst, b_dl_dst, mask):
        self.c.wc.wildcards = a_wildcards

        self.c.set_dl_dst_masked(a_dl_dst, mask)
        (dl_dst, ) = struct.unpack('!6s', "".join(self.c.flow.dl_dst))

        eq_(b_wildcards, self.c.wc.wildcards)
        eq_(b_dl_dst, dl_dst)

    def test_set_dl_dst_masked_00(self):
        mask = '\x00\x00\x00\x00\x00\x00'

        a_wildcards = 0b00000000000
        b_wildcards = 0b00000001010
        a_dl_dst = '\xff' + '\x01' * 5
        b_dl_dst = '\x00' + '\x00' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

        a_wildcards = 0b11111111111
        b_wildcards = 0b11111111111
        a_dl_dst = '\xfe' + '\x00' * 5
        b_dl_dst = '\x00' + '\x00' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

    def test_set_dl_dst_masked_01(self):
        mask = '\x01\x00\x00\x00\x00\x00'

        a_wildcards = 0b00000000000
        b_wildcards = 0b00000001000
        a_dl_dst = '\xff' + '\x01' * 5
        b_dl_dst = '\x01' + '\x00' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

        a_wildcards = 0b11111111111
        b_wildcards = 0b11111111101
        a_dl_dst = '\xfe' + '\x00' * 5
        b_dl_dst = '\x00' + '\x00' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

    def test_set_dl_dst_masked_fe(self):
        mask = '\xfe\xff\xff\xff\xff\xff'

        a_wildcards = 0b000000000000
        b_wildcards = 0b000000000010
        a_dl_dst = '\xff' + '\x01' * 5
        b_dl_dst = '\xfe' + '\x01' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

        a_wildcards = 0b111111111111
        b_wildcards = 0b111111110111
        a_dl_dst = '\xfe' + '\x00' * 5
        b_dl_dst = '\xfe' + '\x00' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

    def test_set_dl_dst_masked_ff(self):
        mask = '\xff\xff\xff\xff\xff\xff'

        a_wildcards = 0b00000000000
        b_wildcards = 0b00000000000
        a_dl_dst = '\xff' + '\x01' * 5
        b_dl_dst = '\xff' + '\x01' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

        a_wildcards = 0b11111111111
        b_wildcards = 0b11111110101
        a_dl_dst = '\xfe' + '\x00' * 5
        b_dl_dst = '\xfe' + '\x00' * 5
        self._test_set_dl_dst_masked(a_wildcards, b_wildcards,
                                     a_dl_dst, b_dl_dst, mask)

    def test_set_dl_src(self):
        a_wildcards = 0b00000000000
        b_wildcards = 0b11111110001
        dl_src = '\x44\xea\xe0\x7c\x1d\x67'
        self.c.set_dl_src(dl_src)

        eq_(b_wildcards, self.c.wc.wildcards)
        eq_(dl_src, self.c.flow.dl_src)

    def test_set_dl_type(self):
        a_wildcards = 0b00000000000
        b_wildcards = 0b11111100001
        dl_type = '\x08\x00'
        self.c.set_dl_type(dl_type)

        eq_(b_wildcards, self.c.wc.wildcards)
        eq_(dl_type, self.c.flow.dl_type)

    def _test_set_nw_dscp(self, a_tos, b_tos, nw_dscp):
        a_wildcards = 0b111111111111
        b_wildcards = 0b111110111111

        self.c.wc.wildcards = a_wildcards
        self.c.flow.nw_tos = a_tos
        self.c.set_nw_dscp(nw_dscp)

        eq_(b_wildcards, self.c.wc.wildcards)
        eq_(b_tos, self.c.flow.nw_tos)

    def test_set_nw_dscp_f(self):
        # dscp uses the first 4-bits of tos field.
        dscp = 0b11111100
        a_tos = 0b00000000
        b_tos = 0b11111100

        self._test_set_nw_dscp(a_tos, b_tos, dscp)

    def test_set_nw_dscp_0(self):
        # dscp uses the first 4-bits of tos field.
        dscp = 0b00000000
        a_tos = 0b11111100
        b_tos = 0b00000000

        self._test_set_nw_dscp(a_tos, b_tos, dscp)

    def test_set_tun_id(self):
        a_tun_id = 0xfffffffffffffffff
        b_tun_id = 0xffffffffffffffff

        self.c.set_tun_id(a_tun_id)

        eq_(UINT64_MAX, self.c.wc.tun_id_mask)
        eq_(b_tun_id, self.c.flow.tun_id)

    def _test_set_nw_ecn(self, a_tos, b_tos, nw_ecn):
        a_wildcards = 0b111111111111
        b_wildcards = 0b111101111111

        self.c.wc.wildcards = a_wildcards
        self.c.flow.nw_tos = a_tos
        self.c.set_nw_ecn(nw_ecn)

        eq_(b_wildcards, self.c.wc.wildcards)
        eq_(b_tos, self.c.flow.nw_tos)

    def test_set_nw_ecn_f(self):
        # ecn uses the last 2-bits of tos field.
        ecn = 0b00000011
        a_tos = 0b00000000
        b_tos = 0b00000011

        self._test_set_nw_ecn(a_tos, b_tos, ecn)

    def test_set_nw_ecn_0(self):
        # ecn uses the last 2-bits of tos field.
        ecn = 0b00000000
        a_tos = 0b00000011
        b_tos = 0b00000000

        self._test_set_nw_ecn(a_tos, b_tos, ecn)

    def test_flow_format_tunnel_id(self):
        c = ClsRule()
        c.wc.tun_id_mask = UINT64_MAX

        res = c.flow_format()

        eq_(ofproto_v1_0.NXFF_NXM, res)

    def test_flow_format_dl_dst(self):
        c = ClsRule()
        c.wc.wildcards = 0b111111110111

        res = c.flow_format()

        eq_(ofproto_v1_0.NXFF_NXM, res)

    def test_flow_format_enc(self):
        c = ClsRule()
        c.wc.wildcards = 0b111100000000

        res = c.flow_format()

        eq_(ofproto_v1_0.NXFF_NXM, res)

    def test_flow_format(self):
        c = ClsRule()
        c.wc.wildcards = 0b111111111111

        res = c.flow_format()

        eq_(ofproto_v1_0.NXFF_OPENFLOW10, res)

    def test_match_tuple(self):
        # data
        wildcards = 0b1111111111111111111111
        in_port = 0xffff
        dl_dst = '\xe4\xc8\x4d\xb8\x97\x9b'
        dl_src = '\x44\xea\xe0\x7c\x1d\x67'
        dl_type = '\x08\x00'
        nw_dscp = 0b11111100

        # fix data
        b_wildcards = 0b1111111111111111100010
        b_nw_tos = 0b11111100

        # set
        c = ClsRule()
        c.wc.wildcards = wildcards
        c.set_in_port(in_port)
        c.set_dl_dst(dl_dst)
        c.set_dl_src(dl_src)
        c.set_dl_type(dl_type)
        c.set_nw_dscp(nw_dscp)

        (r_wildcards, r_in_port, r_dl_src, r_dl_dst, r_dl_vlan,
        r_dl_vlan_pcp, r_dl_type, r_nw_tos, r_nw_proto,
        r_nw_src, r_nw_dst, r_tp_src, r_tp_dst) = c.match_tuple()

        eq_(b_wildcards, r_wildcards)
        eq_(in_port, r_in_port)
        eq_(dl_src, r_dl_src)
        eq_(dl_dst, r_dl_dst)
        eq_(0, r_dl_vlan)
        eq_(0, r_dl_vlan)
        eq_(dl_type, r_dl_type)
        eq_(b_nw_tos, r_nw_tos)
        eq_(0, r_nw_proto)
        eq_(0, r_nw_src)
        eq_(0, r_nw_dst)
        eq_(0, r_tp_src)
        eq_(0, r_tp_dst)


class TestMFInPort(unittest.TestCase):
    """ Test case for nx_match.MFInPort
    """

    pack_str = MF_PACK_STRING_BE16
    n_bytes = struct.calcsize(pack_str)
    n_bits = n_bytes * 8

    c = MFInPort.make()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_make(self):
        eq_(self.pack_str, self.c.pack_str)
        eq_(self.n_bytes, self.c.n_bytes)
        eq_(self.n_bits, self.c.n_bits)

    def test_put(self):
        buf = bytearray()
        in_port = 62897

        rule = ClsRule()
        rule.set_in_port(in_port)
        n_bytes = self.c.put(buf, 0, rule)

        (r_in_port, ) = struct.unpack(self.pack_str, str(buf))

        eq_(self.n_bytes, n_bytes)
        eq_(in_port, r_in_port)


class TestMFEthDst(unittest.TestCase):
    """ Test case for nx_match.MFEthDst
    """

    pack_str = MF_PACK_STRING_MAC
    n_bytes = struct.calcsize(pack_str)
    n_bits = n_bytes * 8

    c = MFEthDst.make()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_make(self):
        eq_(self.pack_str, self.c.pack_str)
        eq_(self.n_bytes, self.c.n_bytes)
        eq_(self.n_bits, self.c.n_bits)

    def test_put(self):
        buf = bytearray()
        n_bytes = self.n_bytes
        dl_dst = '\x31\x20\xbd\x7c\xd3\x49'

        rule = ClsRule()
        rule.set_dl_dst(dl_dst)

        r_n_bytes = self.c.put(buf, 0, rule)
        (r_dl_dst, ) = struct.unpack(self.pack_str, str(buf))

        eq_(n_bytes, r_n_bytes)
        eq_(dl_dst, r_dl_dst)

    def test_put_masked_00(self):
        buf = bytearray()
        n_bytes = 0
        dl_dst = '\x31\x20\xbd\x7c\xd3\x49'
        mask = '\x00\x00\x00\x00\x00\x00'

        rule = ClsRule()
        rule.set_dl_dst_masked(dl_dst, mask)

        r_n_bytes = self.c.put(buf, 0, rule)

        eq_(n_bytes, r_n_bytes)
        eq_(0, len(buf))

    def test_put_masked(self):
        buf = bytearray()
        n_bytes = 0
        # TODO Not yet.
