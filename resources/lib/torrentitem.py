
class TorrentItem:
  "Represents a single torrent result item"

  title = ""
  srcurl = ""
  date = []
  magnet = ""
  torrent = ""
  size = ""
  peers = 0
  seeds = 0
  vip = "false"
    
  def __init__(self, title="", magnet="", torrent="", srcurl=""):
    self.title = title
    self.magnet = magnet
    self.torrent = torrent
    self.srcurl = srcurl
    self.tracker = ""
    self.trackerlogo = ""
    self.size = ""
    self.seeds = 0
    self.peers = 0
    self.vip = "false"

  def __repr__(self):
    return "%s(%r)" % (self.__class__, self.__dict__)

  def __str__(self):
    return "Title:%s\n\tUrl:%s\n\tSeeds:%s\n\tPeers:%s\n\tSize:%s" % (self.title, self.srcurl, self.seeds, self.size)


  def dump(self):
    sstr ="Name: %s\n" % self.title
    sstr += "Link: %s\n" % self.srcurl
    sstr += "Magnet: %s\n" % self.magnet
    sstr += "Torrent: %s\n" % self.torrent
    sstr += "Size: %s\n" % self.size
    sstr += "Date: %s\n" % self.date
    sstr += "Seeds: %s\n" % self.seeds
    sstr += "Leech: %s\n" % self.peers
    sstr += "VIP: %s\n" % self.vip
    return sstr
