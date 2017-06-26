This cybermonitor is very cyber.

The idea is to hook a device into an ethernet link as a bridge, and, through a connected display device, visualize the connections passing through on a map. The intermediate device itself does not need an IP address on the monitored network.

use python2.7 or pyrhon 3

install:

pip install python-geoip

pip install python-geoip-geolite2

pip install IPy

you need root for promiscious mode:

sudo python ip_monitor.py -i &lt;device&gt;

if you are behind a NAT, you need to use -n so that the Private IP is replaced with the public IP of your ISP

add -s to start a local webbrowser for rendering (http://localhost:8080/world)

additionally (suggested) you can install matplotlib, python-mpltoolkits.basemap and use basemap/map.py:

![basemap map client](basemap/screenshot.png)

or get marble.kde.org and qt and compile the yacm-marble viewer in the "marble" subdirectory.
if no lines show up, please use marble 16.12 or older, or any version after d1c9bb096f52, or apply this patch: https://phabricator.kde.org/D6072

![marble map client](marble/screenshot.png)

