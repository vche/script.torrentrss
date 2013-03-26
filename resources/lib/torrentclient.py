# -*- coding: utf-8 -*-
import gzip
from StringIO import StringIO
import urllib, urllib2 , re, sys

try:
  import xbmc
except ImportError:  
  import resources.lib.stubs.xbmc as xbmc

def log(txt):
  xbmc.log(msg = "[SCRIPT] 'torrentrss.torrentclient': %s" % (txt, ), level=xbmc.LOGDEBUG)


class TorrentConnectionError(Exception):
  def __init__(self, value=""):
    self.value = value
  def __str__(self):
    return repr(self.value)


class TorrentClientError(Exception):
  def __init__(self, value=""):
    self.value = value
  def __str__(self):
    return repr(self.value)


class TorrentClient:
  "Base class for interfacing with a torrent client"
  
  def __init__(self, clienturl="", clientport="", desc="", timeout=0):
    if (clienturl == None): self.clientUrl = "127.0.0.1"
    else: self.clientUrl = clienturl
    if (clientport == None): self.clientPort = "80"
    else: self.clientPort=clientport
    self.description=desc
    if (timeout < 1): self.timeout = 20
    else: self.timeout = timeout

  
  def getClientUrl(self):
    "Get the url to use to connect to the client"
    return self.clientUrl


  def getDesc(self):
    "Get the url to use to get the latest articles"
    return self.description

  
  def addLink(self, link):
    "Add the torrent/magnet link to the client's download queue"
    log("adding url %s" % link)
    #TODO: return connectionexception if cannot get the page and/or timeout
    #TODO: return clientexception if retunred page contains error
    addlink = self.encodeUrl(link)
    log("Add torrent url: " + addlink)
    
    try:
      resultsocket = urllib2.urlopen(addlink, timeout=self.timeout)
      resultpage = resultsocket.read()
      if resultsocket.info().get('Content-Encoding') == 'gzip':
        resultpage = gzip.GzipFile(fileobj=StringIO(resultpage)).read()
      self.parseResponse(resultpage)
      resultsocket.close() 
    except  urllib2.URLError:
      log("Url error: (%s = %s)" % (sys.exc_info()[0], sys.exc_info()[1]))
      log(sys.exc_info()[2])
      raise TorrentConnectionError()

            
  def __str__(self):
    return self.descrption + ' (' + self.sourceUrl + ')'

  
  def encodeUrl(self, link):
    return "http://"+self.clientUrl+":"+self.clientPort+self.addUrlPath+urllib.quote(link)
  
  
  def parseResponse(self, resultpage):
    pass


class TorrentClientVuze(TorrentClient):
  "Specialized class to interface with vuze client"
  
  addUrlPath="/index.tmpl?d=u&upurl="
  successStrings = ['chargé avec succès'] # In UTF-8 as declared in header

  def __init__(self, clienturl="", clientport="", desc="", timeout=0):
    if (clientport == None): clientport = "6886"
    TorrentClient.__init__(self, clienturl, clientport, desc, timeout)
    self.ulmsgreg = re.compile('<span id="up_msg".*?>(.*?)</span>', re.IGNORECASE|re.DOTALL)
    

  def parseResponse(self, resultpage):
    ulmsg = self.ulmsgreg.findall(resultpage)
    if (ulmsg) and (len(ulmsg)>0) and (ulmsg[0] != None):
      for successstr in self.successStrings:
        if (successstr in ulmsg[0]): return
    raise TorrentClientError(ulmsg[0])
