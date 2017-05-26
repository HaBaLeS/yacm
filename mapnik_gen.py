#!/usr/bin/env python
import mapnik
stylesheet = 'world_style.xml'
image = 'world_style.png'
m = mapnik.Map(1280, 720)
mapnik.load_map(m, stylesheet)
m.zoom_all()
mapnik.render_to_file(m, image)
print "rendered image to '%s'" % image