#!/usr/bin/env python3
from bs4 import BeautifulSoup as bs
import re
from collections import OrderedDict
import json
import pdb
import sys
import os
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
        
        if hasattr(el, "children"):        
            for ch in el.children:
                self.loopEl(ch)              
            return  

        try:            
            el.sout = el.replace("\n", " ")            
            el.sout = re.sub('\s+', ' ', el.sout) #.strip()
        except:
            import pdb;pdb.set_trace()
                
        
        #if "j" == el: import ipdb; ipdb.set_trace()
        
        el.definition, el.form = self._getFormat(el)                        
        #el.parent.findPreviousSibling().contents
        #elPrev.findParent("p") == el.findParent("p")
        
        #if self.prevStep[1] == el.definition:            
        #    self.prevStep = self.prevStep[0]+contents, self.prevStep[1], self.prevStep[2],  self.prevStep[3]
        if self.prevEl.definition == el.definition and el.bigParent == self.prevEl.bigParent:
            self.prevEl.sout += el.sout
            #self.prevStep = self.prevEl.sout, self.prevEl.definition, self.prevEl.form,  self.prevStep[3]
        else:
            self.addToBuffer(self.prevEl) #
            if el.bigParent != self.prevEl.bigParent:
                self._buffer += "\n"
            #else:
            #    self._buffer +=  " "
            #self.prevStep = (contents, definition, form, el)
            self.prevEl = el
        
    
    def addToBuffer(self, el):
        #contents, definition, form, el = triple
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
            #import ipdb; ipdb.set_trace()
            #if (hasattr(firstChild, "text") and firstChild.text == el) or firstChild == el:
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
        
        with open(FORMATTED_FILE) as f:
            soup = bs(f.read(), "lxml")
        with open(DEFINITIONS_FILE) as data_file:    
            self.defs = json.load(data_file, object_pairs_hook=OrderedDict)

        #for el in soup.findAll("p") + soup.findAll("li"):
        #import pdb;pdb.set_trace()
        self.prevEl = soup.find("html")
        for el in soup.findAll(text=True):
            #print("Novy", el, el.parent.name)
            
            if el.strip("\n") == "":
                continue
            if el == "Created with Microsoft OneNote 2010\nOne place for all your notes and information":
                continue  
            el.bigParent = el.findParent("li") or el.findParent("p") or el.findParent("div")                        
            #self.prevStep = (False, False, False, False)
            self.loopEl(el)
            #self.addToBuffer(self.prevEl)
            #self._buffer += "\n"
        
        self._saveBuffer()

        #print(self._buffer)
        
if __name__ == "__main__":
    Html2Zim()
