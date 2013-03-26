#!/usr/bin/python

#TODO: languages interfaces vuze
#TODO: accept identification vuze
#TODO: module utorrent
#TODO: modules zone-telechargement, rlslog
#TODO: design logo + icon
#TODO: french translations
#TODO: display torrent list ?
import sys, os, traceback

##########################################
# If xbmc libs can't be loaded import stubs for local testing
try:
  import xbmc, xbmcaddon, xbmcgui
  isStandalone = False
except ImportError:  
  import resources.lib.stubs.xbmc as xbmc
  import resources.lib.stubs.xbmcaddon as xbmcaddon
  import resources.lib.stubs.xbmcgui as xbmcgui
  isStandalone = True

def log(txt):
  xbmc.log(msg=txt, level=xbmc.LOGDEBUG)
##########################################

  
# Launch xbmc script
try:
  # Script constants
  __addon__      = xbmcaddon.Addon()
  __version__    = __addon__.getAddonInfo('version')
  __cwd__        = __addon__.getAddonInfo('path')
  __language__   = __addon__.getLocalizedString
  getLS   = __addon__.getLocalizedString

  log("[SCRIPT] '%s': Version %s initialized path %s" % (__addon__, __version__, __cwd__))

  if (__name__ == "__main__"):
    
    # Load feed sources settings
    import resources.lib.feedsources as feedsources
    feedSourceList = []
    if (__addon__.getSetting("feed_yifi") == "true"):
      feedSourceList.append(feedsources.FeedSourceYifi(getLS(55001)))
    if (__addon__.getSetting("feed_rls_mov") == "true"):
      feedSourceList.append(feedsources.FeedSourceRlsLogMovies(getLS(55002)))
    if (__addon__.getSetting("feed_rls_tv") == "true"):
      feedSourceList.append(feedsources.FeedSourceRlsLogShows(getLS(55003)))

    # Load tracker sources settings
    import resources.lib.trackersources as trackersources
    trackerSourceList = []
    if (__addon__.getSetting("tracker_tpb") == "true"):
      trackerSourceList.append(trackersources.TrackerSourceTpb(getLS(55101)))
    if (__addon__.getSetting("tracker_kat") == "true"):
      trackerSourceList.append(trackersources.TrackerSourceKat(getLS(55102)))
   
    #Load client settings
    import resources.lib.torrentclient as torrentclient
    oClient = None
    if (__addon__.getSetting("client_remote") == "true"):
      clientip= __addon__.getSetting("client_ip")
      clientport= __addon__.getSetting("client_port")
    else:
      clientip = None
      clientport = None
    if (__addon__.getSetting("client") == getLS(55202)): oClient = torrentclient.TorrentClientVuze(clientip, clientport, getLS(55202))
    else: xbmcgui.Dialog().ok(getLS(50003), getLS(50004), getLS(50005))
    
    # Start controllers
    import resources.lib.feedmgr as feedmgr
    import resources.lib.trackermgr as trackermgr
    oFeedMgr = feedmgr.FeedMgr(__cwd__, feedSourceList)
    oTrackerMgr = trackermgr.TrackerMgr(trackerSourceList)
    #TODO: start torrent client controler

    # Start gui
    if (isStandalone):
      log("[SCRIPT] '%s': Running in Standalone mode" % (__addon__))
      # Test feedupdate
      #oFeedMgr.update()    
      #oFeedMgr.dumpFeed()
      
      # Test tracker search
      #results = oTrackerMgr.search("robot chicken")
      #oTrackerMgr.dumpResults()
      
      # Test client download
      try:
        if (oClient): 
          oClient.addLink("magnet:?xt=urn:btih:4d5ddf26aa17566e7101fea2ae6f424189d3804d&dn=The+Client+List+1x07..avi&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80")
          log("Upload ok")
      except torrentclient.TorrentClientError as ex:
        log("Client error: (%s = %s)" % (sys.exc_info()[0], sys.exc_info()[1]))
      except torrentclient.TorrentConnectionError as ex2:
        log("Connection error: %s (%s = %s)" % (ex2.__str__(), sys.exc_info()[0], sys.exc_info()[1]))
      
    else:
      import resources.lib.feedgui as feedgui
      ui = feedgui.FeedGUI("script-torrentrss-feedgui.xml", __cwd__, "default", feedMgr=oFeedMgr, trackerMgr=oTrackerMgr, torrentClient=oClient)
      ui.doModal()
      del ui

    # Free objects
    del oFeedMgr
            
    log("[SCRIPT] '%s': Execution completed" % (__addon__))

# If exception occurred
except:
  log("[SCRIPT] '%s: Execution failure: %s" % (__addon__, traceback.format_exc(),))

sys.modules.clear()
