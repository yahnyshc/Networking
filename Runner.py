#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
from Ping import Ping
from Traceroute import Traceroute
from WebServer import WebServer
from Proxy import Proxy

def setupArgumentParser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='A collection of Network Applications developed for SCC.203.')
    parser.set_defaults(func=Ping, hostname='lancaster.ac.uk')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_p = subparsers.add_parser('ping', aliases=['p'], help='run ping')
    parser_p.set_defaults(timeout=2, count=10)
    parser_p.add_argument('hostname', type=str, help='host to ping towards')
    parser_p.add_argument('--count', '-c', nargs='?', type=int,
                          help='number of times to ping the host before stopping')
    parser_p.add_argument('--timeout', '-t', nargs='?',
                          type=int,
                          help='maximum timeout before considering request lost')
    parser_p.set_defaults(func=Ping)

    parser_t = subparsers.add_parser('traceroute', aliases=['t'],
                                     help='run traceroute')
    parser_t.set_defaults(timeout=2, protocol='icmp')
    parser_t.add_argument('hostname', type=str, help='host to traceroute towards')
    parser_t.add_argument('--timeout', '-t', nargs='?', type=int,
                          help='maximum timeout before considering request lost')
    parser_t.add_argument('--protocol', '-p', nargs='?', type=str,
                          help='protocol to send request with (UDP/ICMP)')
    parser_t.set_defaults(func=Traceroute)

    parser_w = subparsers.add_parser('web', aliases=['w'], help='run web server')
    parser_w.set_defaults(port=8080)
    parser_w.add_argument('--port', '-p', type=int, nargs='?',
                          help='port number to start web server listening on')
    parser_w.set_defaults(func=WebServer)

    parser_x = subparsers.add_parser('proxy', aliases=['x'], help='run proxy')
    parser_x.set_defaults(port=8000)
    parser_x.add_argument('--port', '-p', type=int, nargs='?',
                          help='port number to start web server listening on')
    parser_x.set_defaults(func=Proxy)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = setupArgumentParser()
    args.func(args)