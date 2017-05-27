from geoip import geolite2
START_TTL = 5

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
        if self.loc_src and self.loc_dst and self.loc_src.location and self.loc_dst.location:
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

    def console_info(self):
        return self.__repr__()
