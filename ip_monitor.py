from scapy.all import *
from threading import Thread, Lock
from time import sleep
from geoip import geolite2
import argparse

START_TTL = 5
CONN_TRACK = set()
listlock = Lock()
running = True

import os

clear = lambda : os.system('tput reset')

def pkt_callback(pkt):

  if IP in pkt:
      ip = pkt[IP]

      if UDP in pkt and pkt[UDP].dport == 5353:
          mdns = pkt[UDP]
          

      if TCP in pkt:
          addTrack(ip.src, ip.dst)
          #print(mdns.load)

          #name = str(load[12:])

          #print (pkt[UDP].underlayer.summary())
          #print (pkt[UDP].payload_guess)

def addTrack(src, dst):
    ct = ConnTrack(src, dst)
    if ct not in CONN_TRACK:
        listlock.acquire()
        CONN_TRACK.add(ct)
        listlock.release()
        ct.location_lookup()
    else:
        for c in CONN_TRACK:
            if ct == c:
                c.reset_ttl()


class ConnTrack:

    def __init__(self, src, dst):
        self.TTL = START_TTL
        self.src = src
        self.dst = dst

    def reset_ttl(self):
        self.TTL = START_TTL

    def location_lookup(self):
        self.loc_src = geolite2.lookup(self.src)
        self.loc_dst = geolite2.lookup(self.dst)

    def __hash__(self):
        #return ("%s %s" % (self.src, self.dst)).__hash__()
        return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(str(self.src), str(self.dst))).__hash__()

    def __eq__(self, other):
        return (self.src == other.src or self.src == other.dst) and (self.dst == other.dst or self.dst == other.src)

    def __repr__(self):

        srcl = "(???)"
        dstl = "(???)"
        if self.loc_src:
            srcl = self.loc_src.location

        if self.loc_dst:
            dstl = self.loc_dst.location

        return ("%s <-> %s TTL: %s %s <-> %s" % (self.src, self.dst, self.TTL,srcl,dstl))

    def is_alive(self):
        self.TTL = self.TTL-1
        return self.TTL>0

def update_conntrack():
    #sort list
    while running:
        clear()
        listlock.acquire()
        for con in list(CONN_TRACK): #iterate over copy of list to avoid concurrent modification
            if con.is_alive():
                print(con)
            else:
                CONN_TRACK.remove(con)
        listlock.release()
        sleep(1)


def run(device):

    update_runner = Thread(target = update_conntrack)
    update_runner.setDaemon(True)
    update_runner.start()

    print("start PCAP")
    sniff(iface=device, prn=pkt_callback, store=0)

    running = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Network monitor. Print connections and geoip locations for src and dst ')
    parser.add_argument('-i', help='Device to monitor', required=True)
    args = parser.parse_args()
    run(args.i)