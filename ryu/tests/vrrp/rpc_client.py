#!/usr/bin/env python
from argparse import ArgumentParser
import socket
import sys

from ryu.lib import rpc
from ryu.services.vrrp import rpc_manager
from ryu.lib.packet import vrrp
from contextlib import closing


class VRRPRPCClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rpc_client = rpc.Client(self.sock)

    def config(self, vrid, vripaddr, ifname, ifipaddr, priority):
        vrrp_param = rpc_manager.VRRPParam(vrrp.VRRP_VERSION_V3, vrid, vripaddr)
        vrrp_param.setPort(ifname, ifipaddr, priority)

        result = self.rpc_client.call("vrrp_config", [vrrp_param.toArray()])
        print result

    def config_change(self, vrid, priority, interval):
        change_param = {
            rpc_manager.CONF_KEY_PRIORITY: priority,
            rpc_manager.CONF_KEY_ADVERTISEMENT_INTERVAL: interval}

        result = self.rpc_client.call("vrrp_config_change", [vrid, change_param])
        print result

    def list(self, vrid):
        result = self.rpc_client.call("vrrp_list", [vrid])
        info = result[0]
        for key in info:
            print key, " : ", info[key]

    def connect(self, rpc_server_ip='127.0.0.1'):
        self.sock.connect((rpc_server_ip, rpc_manager.VRRP_RPC_PORT))

    def close(self):
        print "VRRPClient: Closed"
        self.sock.close()


def main():
    args = _parse_args()

    client = VRRPRPCClient()
    with closing(client):
        client.connect()
        
        if args.method == "config":
            client.config(args.vrid, args.vripaddr, args.ifname, args.ifipaddr, args.priority)
        elif args.method == "list":
            client.list(args.vrid)
        elif args.method == "config_change":
            client.config_change(args.vrid, args.priority, args.interval)
        else:
            print "target method is nothing."


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument('--method', dest='method', type=str, default='config')
    parser.add_argument('--vrid', dest='vrid', type=int, default=16)
    parser.add_argument('--vripaddr', dest='vripaddr', type=str, default='172.16.10.10')
    parser.add_argument('--ifname', dest='ifname', type=str, default='veth1')
    parser.add_argument('--ifipaddr', dest='ifipaddr', type=str, default='172.16.10.1')
    parser.add_argument('--priority', dest='priority', type=int, default=100)
    parser.add_argument('--interval', dest='interval', type=int, default=3)
    return parser.parse_args()


if __name__ == '__main__':
    main()
