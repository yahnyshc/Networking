#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
import struct
import time
from NetworkApplications import NetworkApplication

class Ping(NetworkApplication):

    def receiveOnePing(self, icmpSocket, destinationAddress, ID):
        # 1. Wait for the socket to receive a reply
        try:
            resp, addr = icmpSocket.recvfrom(4096)
            # 2. If reply received, record time of receipt, otherwise, handle timeout
            timeReceived = time.time() * 1000
        except TimeoutError:
            # Handle timeout
            return None

        # 3. Unpack the imcp and ip headers for useful information, including Identifier, TTL, sequence number
        IPv4_names = ["version", "type", "length", "id", "flags", "ttl", "protocol", "checksum", "src_ip", "dest_ip"]
        IPv4_header = dict(zip(IPv4_names, struct.unpack_from("BBHHHBBHII", resp[0:20], 0)))

        ICMP_names = ["type", "code", "checksum", "packetID", "sequence"]
        ICMP_header = dict(zip(ICMP_names, struct.unpack_from("bbHHh", resp[20:28], 0)))

        # 5. Check that the Identifier (ID) matches between the request and reply
        if ICMP_header["packetID"] != ID:
            print("incorrect packet")

        # 6. Return time of receipt, TTL, packetSize, sequence number
        return {"receipt_time": timeReceived,
                "ttl": IPv4_header["ttl"],
                "length": len(resp),
                "sequence": ICMP_header["sequence"],
                "dest_ip": addr[0]}

    def sendOnePing(self, icmpSocket, destinationAddress, ID, seq_num):
        # 1. Build ICMP header
        header = struct.pack("bbHHh", self.ICMP_ECHO, 0, 0, ID, seq_num)
        # 2. Checksum ICMP packet using given function
        checksum = self.checksum(header)
        # 3. Insert checksum into packet
        header = struct.pack("bbHHh", self.ICMP_ECHO, 0, checksum, ID, seq_num)
        # 4. Send packet using socket
        icmpSocket.sendto(header, (destinationAddress, 1))
        # 5. Return time of sending
        return time.time() * 1000

    def doOnePing(self, destinationAddress, packetID, seq_num, timeout):
        # 1. Create ICMP socket
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW, proto=socket.IPPROTO_ICMP)
        s.settimeout(timeout)
        # 2. Call sendOnePing function
        sendtime = self.sendOnePing(s, destinationAddress, packetID, seq_num)
        # 3. Call receiveOnePing function
        ping = self.receiveOnePing(s, destinationAddress, packetID)
        # 4. Close ICMP socket
        s.close()

        if ping:
            try:
                hostname = socket.gethostbyaddr(ping["dest_ip"])[0]
            except socket.herror:
                hostname = ping["dest_ip"]
            # 5. Print out the delay (and other relevant details) using the printOneResult method, below is just an example.
            self.printOneResult(destinationAddress, ping["length"], ping["receipt_time"] - sendtime, ping["sequence"],
                                ping["ttl"], hostname)
        else:
            print(f"From {destinationAddress} icmp_seq={seq_num} Request timed out")

    def __init__(self, args):
        self.ICMP_ECHOREPLY = 0  # Echo reply
        self.ICMP_ECHO = 8  # Echo request
        print('Ping to: %s...' % (args.hostname))
        # 1. Look up hostname, resolving it to an IP address
        ipaddress = socket.gethostbyname(args.hostname)
        # 2. Repeat below args.count times
        for seq_num in range(1, args.count + 1):
            # 3. Call doOnePing function, approximately every second, below is just an example
            self.doOnePing(ipaddress, os.getpid() & 0xFFFF, seq_num, args.timeout)
            time.sleep(1)