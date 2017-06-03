use python2.7 or pyrhon 3

install:

pip install python-geoip

pip install python-geoip-geolite2

pip install IPy

you need root for promiscious mode:

sudo python ip_monitor.py -i &lt;device&gt;

if you are behind a NAT, you need to use -n so that the Private IP is replaced with the public IP of your ISP

you can add  -s to start a local webbrowser for rendering http://localhost:8080/world

alternatively (suggested) you can install matplotlib, python-mpltoolkits.basemap and use basemap/map.py
