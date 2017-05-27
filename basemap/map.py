import random
import matplotlib
import matplotlib.pyplot as plt
import json, requests

matplotlib.use('Agg')
fig = plt.figure(figsize = (16,10))
fig.patch.set_facecolor('black')
fig.patch.set_alpha(1.0)
ax = fig.add_subplot(111)
plt.subplots_adjust(left=0.00, right=1.00, top=1.00, bottom=0.00)

import numpy as np
import matplotlib.animation as animation
import matplotlib.lines as lines
from mpl_toolkits.basemap import Basemap

my_map = Basemap(projection='robin', resolution = 'c', area_thresh = 1000.0, lat_0=0, lon_0=0)
my_map.drawmapboundary(fill_color = 'black')
my_map.drawcoastlines(color='lightblue')
my_map.drawcountries(color='lightblue')

def get_current_coords():
    url = 'http://localhost:8080/data'
    resp = requests.get(url=url)

    try:
        json = resp.json();
        return json;
    except:
        return {}


def animate(i):
    ret = set()
    cur = get_current_coords()
    for elem in cur:
        ret.add(my_map.drawgreatcircle(elem["src_long"], elem["src_lat"], elem["dst_long"], elem["dst_lat"], color='y', linewidth=2)[0])

    return ret

anim = animation.FuncAnimation(fig, animate, frames=1, interval=500, blit=True)
plt.show()

