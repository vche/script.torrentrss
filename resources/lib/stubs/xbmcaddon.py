import os

def Addon():
  return xbmcaddon()

class xbmcaddon:

  def __init__(self):
    self
    
  def __repr__(self):
#    return "%s(%r)" % (self.__class__, self.__dict__)
    return "script.torrentrss"
   
  def getAddonInfo(self, attr):
    if attr == "version":
      return 1.0
    elif attr == "path":
      return os.getcwd()
    else:
      return 0
      
  def getLocalizedString(self, ustr=0):
    if ustr==0: return "en"
    elif ustr == 55101: return "The pirate bay"
    elif ustr == 55102: return "Kick ass torrents"
    elif ustr == 50003: return "Warning !"
    elif ustr == 50004: return "No bit torrent client is selected"
    elif ustr == 50005: return "Configure one in addon settings to download files"
    else: return "xbmcaddon stub: No label"


  def getSetting(self, sid):
    if sid == "feed_yifi": return "false"
    elif sid == "feed_rls_mov": return "false"
    elif sid == "feed_rls_tv": return "true"
    elif sid == "tracker_tpb": return "true"
    elif sid == "tracker_kat": return "true"
    elif sid == "client": return "Vuze"
    elif sid == "client_remote": return "false"
    elif sid == "client_ip": return "127.0.0.1"
    elif sid == "client_port": return "6886"
    