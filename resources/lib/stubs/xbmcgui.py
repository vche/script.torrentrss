
class xbmcgui:

  def __init__(self):
    self
    
  def __repr__(self):
    return "%s(%r)" % (self.__class__, self.__dict__)

class Dialog:

  def __init__(self):
    self
    
  def ok(self, label="", line1="", line2="", line3=""):
    print(label+":")
    if (len(line1) >0): print("  "+ line1+"")
    if (len(line2) >0): print("  "+ line2+"")
    if (len(line3) >0): print("  "+ line3+"")
