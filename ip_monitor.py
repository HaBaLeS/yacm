from scapy.all import *
from threading import Thread, Lock
from time import sleep
from geoip import geolite2
import argparse


START_TTL = 5
CONN_TRACK = set()
listlock = Lock()
running = True
PORT_NUMBER = 8080

import os

clear = lambda : os.system('tput reset')

def pkt_callback(pkt):

  if IP in pkt:
      ip = pkt[IP]
      #if UDP in pkt and pkt[UDP].dport == 5353:
      #    mdns = pkt[UDP]
          

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
        listlock.acquire()
        for c in CONN_TRACK:
            if ct == c:
                c.reset_ttl()
        listlock.release()


class ConnTrack:

    def __init__(self, src, dst):
        self.TTL = START_TTL
        self.src = src
        self.dst = dst
        self.loc_src = None
        self.loc_dst = None

    def reset_ttl(self):
        self.TTL = START_TTL

    def location_lookup(self):
        self.loc_src = geolite2.lookup(self.src)
        self.loc_dst = geolite2.lookup(self.dst)

    def __hash__(self):
        #XOR src/dst so the can be ordered in any direction
        return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(str(self.src), str(self.dst))).__hash__()

    def __eq__(self, other):
        return (self.src == other.src or self.src == other.dst) and (self.dst == other.dst or self.dst == other.src)

    def to_web(self):
        if self.loc_src and self.loc_dst:
            srcl = self.loc_src.location
            dstl = self.loc_dst.location
            return '{"src_lat":%s,"src_long":%s, "dst_lat":%s,"dst_long":%s}'%(srcl[0],srcl[1],dstl[0],dstl[1])
        return None

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
        #clear()
        listlock.acquire()
        for con in list(CONN_TRACK): #iterate over copy of list to avoid concurrent modification
            if con.is_alive():
                print(con)
            else:
                CONN_TRACK.remove(con)
        listlock.release()
        sleep(1)

def http_server_start():
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

    class myHandler(BaseHTTPRequestHandler):
        # Handler for the GET requests
        def do_GET(self,):


            if self.path == "/data":
                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()
                resp = "["
                listlock.acquire()
                for con in list(CONN_TRACK):  # iterate over copy of list to avoid concurrent modification
                    resp = resp + str(con.to_web()) + ","
                resp =resp[:-1]
                listlock.release()
                resp = resp + "]"
                self.wfile.write(resp)
                return

            if self.path == "/jquery":
                self.send_file("jquery-3.2.1.min.js", 'application/javascript')
                return

            if self.path == "/":
                self.send_file("index.html",'text/html')
                return

            if self.path == "/world":
                self.send_file("bitsch/flight-animation.html", 'text/html')
                return

            ##fallback
            try:
                self.send_file("bitsch" + self.path, "application/javascript")
            except Exception:
                pass

        def send_file(self, file, content_type):
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            with open(file, 'r') as jquery:
                for line in jquery:
                    self.wfile.write(line)
            return

    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = HTTPServer(('localhost', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ', PORT_NUMBER

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()




def run(args):

    #if args.v:
    print("Start Logger")
    update_runner = Thread(target = update_conntrack)
    update_runner.setDaemon(True)
    update_runner.start()

    if args.s:
        print("Start Webserver")
        http_runner = Thread(target = http_server_start)
        http_runner.setDaemon(True)
        http_runner.start()

    print("start PCAP")
    sniff(iface=args.i, prn=pkt_callback, store=0)

    running = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Network monitor. Print connections and geoip locations for src and dst ')
    parser.add_argument('-i', help='Device to monitor', required=True)
    #parser.add_argument('-v', help='Verbose print Data to Console', action='store_true')
    parser.add_argument("-s", help='start webserver', action='store_true')
    args = parser.parse_args()
    run(args)