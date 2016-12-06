#!/usr/bin/env python3
from collections import OrderedDict
import re, json, ipdb, sys, os
from bs4 import BeautifulSoup as bs
__help__ = """
Converts html (output from OneNote) to Zim format.\n
Usage html2zim.py <output.html>
"""

if len(sys.argv) < 2:  
  print(__help__)
  quit()

FORMATTED_FILE = sys.argv[1] #"/home/edvard/edvard/www/html2zim/formatting.htm"
DEFINITIONS_FILE = os.path.dirname(os.path.realpath(sys.argv[0]))+"/definitions.json"

class Html2Zim:        
       
        
    def _getFormat(self, el):                        
        def _check(el, field):                               
            if not hasattr(el,"matches") or el.matches is None:
                el.matches = {"font-size" : 0, "color" : 0, "font-style":0, "font-weight":0}

                try:
                    styles = el.parent.attrs["style"]                
                except (AttributeError, KeyError) :
                    styles = ""            
                if styles:
                    for style in styles.split(";"):
                        name, val = style.split(":")
                        el.matches[name] = val                            

            if field in par:            
                for c, val in par[field].items():
                    try:
                        if el.matches[c] != val:
                            return False                        
                    except TypeError:
                        return False
            return True
        
        for definition, par in self.defs.items():                            
            accords = True                             
            
            if not _check(el, "style"):
                continue

            if not _check(el.parent, "parent-style"):                  
                continue

            if accords and "name" in par:
                accords = (el.parent.name == par["name"])          

            if not accords:
                continue            
            else:    
                return definition, self.defs[definition]["FORMAT"]
        return None, None

    def loopEl(self,el):        
        
        #if hasattr(el, "children"):        
        #    for ch in el.children:                
        #        self.loopEl(ch)              
        #    return  
        #if "spadv" in el: import ipdb; ipdb.set_trace()
                   
        el.sout = el.replace("\n", " ")            
        el.sout = re.sub('\s+', ' ', el.sout) #.strip()                                                    
        el.definition, el.form = self._getFormat(el)                                
                
        if self.prevEl.definition is el.definition and \
           el.myContext is self.prevEl.myContext and \
           el.myTr is self.prevEl.myTr and \
           el.myTd is self.prevEl.myTd:
            self.prevEl.sout += el.sout            
        else:   
            self.addToBuffer(self.prevEl) #
            
            if self.prevEl.myTd and el.myTd is not self.prevEl.myTd:
                self._buffer += "|"
            
            if el.myTr is not self.prevEl.myTr:
                self._buffer += "\n"
                if el.myTr: self._buffer += "|"
                
            if el.myContext is not self.prevEl.myContext:
                if self.prevEl.myTd and self.prevEl.myTd is el.myTd:
                    # zim prints newline in a cell, however, we cant print nl directly due to table syntax
                    self._buffer += "\\n"
                elif not el.myTr:
                    self._buffer += "\n"            

            self.prevEl = el
            
                    
    
    def addToBuffer(self, el):        
        if not el.sout:
            return
        
        if el.definition == "header":
            self._saveBuffer()
            self._bufferName = el.sout        
         
        if el.definition == "anchor":
            self._buffer += (el.form).format(el.parent.attrs["href"], el.sout)
        elif el.definition:        
            self._buffer += (el.form).format(el.sout) 
        elif el.findParent("li"):
            firstChild = next(el.findParent("li").children)
            if firstChild.text == el:
                self._buffer += ("* {}").format(el.sout) 
            else:
                self._buffer += el.sout
        else:
            self._buffer += el.sout                        

    def _saveBuffer(self):
        if self._buffer:
            fn = self._bufferName.replace(" ","_") + ".txt"
            with open(fn, "w") as f:
                f.write(self._buffer)
            print("Saved to " + fn)
            self._buffer = ""
    
    def __init__(self):
        self._bufferName = "out"
        self._buffer = ""        
        self.lastTd = None
        self.lastTr = None
        
        with open(FORMATTED_FILE) as f:
            soup = bs(f.read(), "lxml")
        with open(DEFINITIONS_FILE) as data_file:    
            self.defs = json.load(data_file, object_pairs_hook=OrderedDict)        
        self.prevEl = soup.find("html")
        for el in soup.findAll(text=True):                        
            if el.strip("\n") == "":
                continue
            if el == "Created with Microsoft OneNote 2010\nOne place for all your notes and information":
                continue        
            
            el.myContext = el.findParent("li") or el.findParent("p") or el.findParent("div")
            el.myTr = el.findParent("tr")
            el.myTd = el.findParent("td")
            self.loopEl(el)
        
        # adds the last self.prevEl to the buffer
        el = bs("<html><p>a</p></html>","lxml").findAll(text=True)[0]                
        el.myContext = el.findParent("html")        
        el.myTr = el.findParent("tr")
        el.myTd = el.findParent("td")
        self.loopEl(el) 
        
        self._saveBuffer()
        #print(self._buffer)
        
if __name__ == "__main__":
    Html2Zim()
