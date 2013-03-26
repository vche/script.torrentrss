# -*- coding: utf-8 -*-
import HTMLParser
import gzip
from StringIO import StringIO
import urllib, urllib2, re, sys
import torrentitem
#from BeautifulSoup import BeautifulSoup

#trackeritem: name, date, size, vip, seeds, leech

try:
  import xbmc
except ImportError:  
  import resources.lib.stubs.xbmc as xbmc

def log(txt):
  xbmc.log(msg = "[SCRIPT] 'torrentrss.trackerources': %s" % (txt, ), level=xbmc.LOGDEBUG)


class TrackerSource:
  "Base class of tracker source"
  
  def __init__(self, srcurl="", logo="", desc="", timeout=0):
    self.sourceUrl=srcurl
    self.description=desc
    self.logo=logo
    if (timeout < 1): self.timeout = 10
    else: self.timeout = timeout
    
  
  def getUrl(self):
    "Get the url to use to get the latest articles"
    return self.sourceUrl

    
  def getLogo(self):
    "Get the logo file name"
    return self.logo


  def getDesc(self):
    "Get the url to use to get the latest articles"
    return self.description

  
  def Search(self, keywords):
    "Search the given keywords on the tracker"
    searchurl = self.encodeSearchUrl(keywords)
    log("opening url %s" % searchurl)
    
    try:
      resultsocket = urllib2.urlopen(searchurl, timeout = self.timeout)
      resultpage = resultsocket.read()
      if resultsocket.info().get('Content-Encoding') == 'gzip':
        resultpage = gzip.GzipFile(fileobj=StringIO(resultpage)).read()
      resultsocket.close() 
      return self.ParseResults(resultpage)
    except:
      log("Cannot get search results due to exception %s = %s" % (sys.exc_info()[0], sys.exc_info()[1]))
      log(sys.exc_info()[2])
      return []
        
  
  def encodeSearchUrl(self, keywords):
    return self.sourceUrl + "/search/"+ urllib.quote(keywords)

  def ParseResults(self, htmlpage):
    #log(resultpage)
    return []
    
  def __str__(self):
    return self.descrption + ' (' + self.sourceUrl + ')'

  def extractProperty(self, reg, content):
    "Search given regular expression in content and returns first result or None"
    searchResults = reg.findall(content)
    if (searchResults) and (len(searchResults)>0) and (searchResults[0] != None): 
      return searchResults[0]
    else: return None


class TrackerSourceTpb(TrackerSource):
  "Specialized class to process The Pirate Bay tracker search"

  def __init__(self, desc=""):
    TrackerSource.__init__(self, "http://thepiratebay.se", "tpblogosmall.gif", desc)

    # Precompute regular expressions for info extraction    
    self.resulttablereg = re.compile('<table id="searchResult">(.*)</table>', re.IGNORECASE|re.DOTALL)
    self.resultreg = re.compile('<tr>(.*?)</tr>', re.IGNORECASE|re.DOTALL)
    self.resultinforeg = re.compile('<td.*?>(.*?)</td>', re.IGNORECASE|re.DOTALL)
    self.resultinfonamereg = re.compile('<a.*?href=["](.*?)["]\s*?class="detLink".*?>(.*?)</a>', re.IGNORECASE|re.DOTALL)
    self.resultinfomagnetreg = re.compile('<a.*?href=["](magnet.*?)["]\s*', re.IGNORECASE|re.DOTALL)
    self.resultinfotorrent = re.compile('<a.*?href=["](//torrent.*?)["]\s*', re.IGNORECASE|re.DOTALL)
    self.resultinfodatesizereg = re.compile('<font.*?Uploaded[\s*](.*)\,[\s*]Size[\s*](.*)\,', re.IGNORECASE|re.DOTALL)

  def encodeSearchUrl(self, keywords):
    log("encode url;");log(keywords)
    return self.sourceUrl + "/search/"+ urllib.quote(keywords) + "/0/7/0"

  def ParseResults(self, htmlpage):
    resultList = []
    searchTable = self.resulttablereg.findall(htmlpage)
    if (searchTable) and (len(searchTable)>0) and (searchTable[0] != None):
      searchResults = self.resultreg.findall(searchTable[0])
      for result in  searchResults:
        resultInfo = self.resultinforeg.findall(result)
        if (len(resultInfo) == 4):
          html = HTMLParser.HTMLParser()
          infoname = self.extractProperty(self.resultinfonamereg, resultInfo[1])
          resultitem = torrentitem.TorrentItem(title=infoname[1], srcurl=(self.sourceUrl + infoname[0]))
          resultitem.magnet = self.extractProperty(self.resultinfomagnetreg, resultInfo[1])
          torrentlink = self.extractProperty(self.resultinfotorrent, resultInfo[1])
          if (resultitem.torrent != None): resultitem.torrent = "http:" + torrentlink
          infodatesize = self.extractProperty(self.resultinfodatesizereg, resultInfo[1])
          resultitem.date = html.unescape(infodatesize[0])
          resultitem.size = html.unescape(infodatesize[1])
          resultitem.seeds = resultInfo[2]
          resultitem.peers = resultInfo[3]
          if "vip.gif" in resultInfo[1]: resultitem.vip ="true"
          resultitem.tracker = self.getDesc()
          resultitem.trackerlogo = self.getLogo()
          resultList.append(resultitem)
    return resultList


class TrackerSourceKat(TrackerSource):
  "Specialized class to process KickAss Torrents tracker search"

  def __init__(self, desc=""):
    TrackerSource.__init__(self, "http://kat.ph", "kickasslogosmall.png", desc)

    # Precompute regular expressions for info extraction    
    self.resultreg = re.compile('<tr.*?class="(odd|even)".*?>(.*?)</tr>', re.IGNORECASE|re.DOTALL)
    self.resultinforeg = re.compile('<td.*?>(.*?)</td>', re.IGNORECASE|re.DOTALL)
    self.resultlinksreg = re.compile('<a.*?href=["](.*?)["]\s*', re.IGNORECASE|re.DOTALL)
    self.resultnamereg = re.compile('<div class="torrentname">.*?<a.*?<a.*?>(.*?)</a>', re.IGNORECASE|re.DOTALL)
    
  def encodeSearchUrl(self, keywords):
    return self.sourceUrl + "/usearch/"+ urllib.quote(keywords) + "/?field=seeders&sorder=desc"

  def ParseResults(self, htmlpage):
    resultList = []
    html = HTMLParser.HTMLParser()
    searchResults = self.resultreg.findall(htmlpage)
    for (col, result) in searchResults:
      resultInfo = self.resultinforeg.findall(result)
      if (len(resultInfo) == 6):
        # First bloc contains links and name
        infoname = self.extractProperty(self.resultnamereg, resultInfo[0])
        infoname = re.sub(r"(<.*?>)", "", infoname)
        
        resultitem = torrentitem.TorrentItem(title=infoname)
        if "verifup.png" in resultInfo[0]: resultitem.vip ="true"
        links = self.resultlinksreg.findall(resultInfo[0])
        for urllink in links:
          if ("magnet:?" in urllink): resultitem.magnet = urllink
          elif (".torrent?title=" in urllink): resultitem.torrent = "http:" + urllink
          elif (urllink.endswith(".html")): resultitem.srcurl = self.sourceUrl + urllink
        
        resultitem.size = html.unescape(re.sub(r"(<.*?>)", "", resultInfo[1]))
        resultitem.date = html.unescape(re.sub(r"(<.*?>)", "", resultInfo[3]))
        resultitem.seeds = resultInfo[4]
        resultitem.peers = resultInfo[5]
        resultitem.tracker = self.getDesc()
        resultitem.trackerlogo = self.getLogo()
        resultList.append(resultitem)
    return resultList
