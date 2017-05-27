from scapy.all import *
from threading import Thread, Lock
from time import sleep
from conntrack import ConnTrack
import argparse

import hax0r_log as hxl


CONN_TRACK = set()
listlock = Lock()
running = True
PORT_NUMBER = 8080



def pkt_callback(pkt):
  if IP in pkt:
      ip = pkt[IP]
      if TCP in pkt:
          addTrack(ip.src, ip.dst)

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



def update_conntrack():
    #sort list
    while running:
        #clear()
        listlock.acquire()
        for con in list(CONN_TRACK): #iterate over copy of list to avoid concurrent modification
            if con.is_alive():
                hxl.info(con.console_info())
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
                for con in list(CONN_TRACK)[:]:  # iterate over copy of list to avoid concurrent modification
                    bla = con.to_web()
                    if bla:
                        resp = resp + str(bla) + ","
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
        hxl.success('Started httpserver on port %s' % PORT_NUMBER)

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()


def run_tcpdump_subprocess(device):
    import subprocess
    proc = subprocess.Popen(['-i ' + device, '-nn', '-t', '-l', 'tcp and not ip6'], 1, 'tcpdump', stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
    while True:
        line = proc.stdout.readline()
        hxl.debug(line)
        if line != '':
            # the real code does filtering here
            data = str(line).split(' ')
            src = data[1]
            dst = data[3][:-1]  # remove last ':'

            dst_ip = ''
            for block in dst.split('.')[:-1]:
                dst_ip = dst_ip + '.' + block
            dst_ip = dst_ip[1:]

            src_ip = ''
            for block in src.split('.')[:-1]:
                src_ip = src_ip + '.' + block
            src_ip = src_ip[1:]

            addTrack(src_ip, dst_ip)



def run(args):

    hxl.debug_enabled = args.v
    hxl.info_enabled =  not args.q

    hxl.success("starting Connection tracking Thread")
    update_runner = Thread(target = update_conntrack)
    update_runner.setDaemon(True)
    update_runner.start()

    if args.s:
        hxl.success("starting simple python Webserver")
        http_runner = Thread(target = http_server_start)
        http_runner.setDaemon(True)
        http_runner.start()

    if args.scapy:
        hxl.success("Start PCAP")
        sniff(iface=args.i, prn=pkt_callback, store=0)
    else:
        hxl.success("starting tcpdump subprocess")
        run_tcpdump_subprocess(args.i)

    running = False


if __name__ == "__main__":
    hxl.newline()
    hxl.success("Welcome to YACM - Yet Another Cyber Map")
    hxl.newline()

    parser = argparse.ArgumentParser(description='YACM - Yet Another Cyber Map')
    parser.add_argument('-i', help='Device to monitor', required=True)
    parser.add_argument('--scapy', help='use scapy instead of tcpdum in subprocess', action='store_true')
    parser.add_argument("-s", help='start webserver', action='store_true')
    parser.add_argument("-v", help='enable debug logging', action='store_true')
    parser.add_argument("-q", help='quiet, suppress info messages', action='store_true', default=False)
    args = parser.parse_args()
    run(args)