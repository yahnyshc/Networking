#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
import struct
import time
from NetworkApplications import NetworkApplication

class Traceroute(NetworkApplication):
    def receivePacket(self, sock, ID):
        # 1. Wait for the socket to receive a reply
        try:
            resp, addr = sock.recvfrom(2048)
        except TimeoutError:
            return None

        # 2. If reply received, record time of receipt, otherwise, handle timeout
        timeReceived = time.time() * 1000

        # 3. Unpack the imcp and ip headers for useful information, including Identifier, TTL, sequence number
        IPv4_names = ["version", "type", "length", "id", "flags", "ttl", "protocol", "checksum", "src_ip", "dest_ip"]
        IPv4_header = dict(zip(IPv4_names, struct.unpack_from("BBHHHBBHII", resp[0:20], 0)))

        ICMP_names = ["type", "code", "checksum", "packetID", "sequence"]
        ICMP_header = dict(zip(ICMP_names, struct.unpack_from("bbHHh", resp[20:28], 0)))

        # 5. Check that the Identifier (ID) matches between the request and reply
        if ICMP_header["type"] == self.ECHOREPLY and ICMP_header["packetID"] != ID:
            print("incorrect packet")

        # 6. Return ICMP type, destination ip, time of receipt, TTL, packetSize, sequence number
        return {"type": ICMP_header["type"],
                "dest_ip": addr[0],
                "receipt_time": timeReceived,
                "ttl": IPv4_header["ttl"],
                "length": len(resp),
                "sequence": ICMP_header["sequence"]}

    def sendPacket(self, sock, destinationAddress, ID, seq_num, proto):
        if proto == socket.IPPROTO_ICMP:
            # 1. Build ICMP header
            header = struct.pack("bbHHh", self.ECHO, 0, 0, ID, seq_num)
            # 2. Checksum ICMP packet using given function
            checksum = self.checksum(header)
            # 3. Insert checksum into packet
            header = struct.pack("bbHHh", self.ECHO, 0, checksum, ID, seq_num)
            # 4. Send packet using socket
            sock.sendto(header, (destinationAddress, 1))
        elif proto == socket.IPPROTO_UDP:
            sock.sendto(b"", (destinationAddress, 33434))
        else:
            print("Unknown proto")
            raise OSError
        # 5. Return time of sending
        return time.time() * 1000

    def doTraceroute(self, destinationAddress, packetID, timeout, protocol):
        try:
            proto = socket.getprotobyname(protocol)
        except:
            print(f"Unknown protocol: {protocol}")
            return

        # 1. Create socket
        icmp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW, proto=socket.IPPROTO_ICMP)
        icmp_sock.settimeout(timeout)
        sender_sock = icmp_sock if proto != socket.IPPROTO_UDP else socket.socket(family=socket.AF_INET,
                                                                                  type=socket.SOCK_DGRAM,
                                                                                  proto=socket.IPPROTO_UDP)
        for ttl in range(1, self.maxTTL + 1):
            measurements = []
            packet = None
            sender_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            for tries in range(self.TRIES):
                # 2. Call sendPacket function
                sendtime = self.sendPacket(sender_sock, destinationAddress, packetID, tries, proto)

                # 3. Call receivePacket function
                receivedPacket = self.receivePacket(icmp_sock, packetID)
                if receivedPacket:
                    packet = receivedPacket
                    measurements.append(packet["receipt_time"] - sendtime)
                    # self.printOneResult(destinationAddress, packet["length"], packet["receipt_time"]-sendtime, packet["sequence"], packet["ttl"])
                else:
                    measurements.append(None)

            if packet:
                try:
                    hostname = socket.gethostbyaddr(packet["dest_ip"])[0]
                except socket.herror:
                    hostname = packet["dest_ip"]
                self.printOneTraceRouteIteration(ttl, packet["dest_ip"], measurements, hostname)
                if packet["type"] == self.TTL_EXCEEDED:
                    pass
                elif packet["type"] == self.ECHOREPLY or (
                        proto == socket.IPPROTO_UDP and packet["type"] == self.DEST_UNREACHABLE):
                    break
                else:
                    print("Packet with unknown ICMP type received: " + str(packet["type"]))
            else:
                self.printOneTraceRouteIteration(ttl, None, measurements, None)
        # 4. Close ICMP socket
        icmp_sock.close()
        if proto == socket.IPPROTO_UDP:
            sender_sock.close()

    def __init__(self, args):
        self.ECHOREPLY = 0  # Echo reply
        self.DEST_UNREACHABLE = 3  # Echo reply
        self.ECHO = 8  # Echo request
        self.TTL_EXCEEDED = 11  # TTL exceeded
        self.maxTTL = 64
        self.TRIES = 3
        print('traceroute to: %s...' % (args.hostname))
        # 1. Look up hostname, resolving it to an IP address
        ipaddress = socket.gethostbyname(args.hostname)
        # 2. Repeat below args.count times
        self.doTraceroute(ipaddress, os.getpid() & 0xFFFF, args.timeout, args.protocol)
