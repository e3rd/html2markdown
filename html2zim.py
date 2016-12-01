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
            contents = el.replace("\n", " ")
        except:
            import pdb;pdb.set_trace()
                
        
        definition, form = self._getFormat(el)                
        
        if self.prevStep[1] == definition:            
            self.prevStep = self.prevStep[0]+contents, self.prevStep[1], self.prevStep[2],  self.prevStep[3]
        else:
            self.addToBuffer(self.prevStep)
            self.prevStep = (contents, definition, form, el)
        
    
    def addToBuffer(self, triple):
        contents, definition, form, el = triple
        if not contents:
            return
        
        if definition == "header":
            self._saveBuffer()
            self._bufferName = contents
            
        #import pdb;pdb.set_trace()        
        
        if definition == "anchor":
            self._buffer += (form).format(el.parent.attrs["href"], contents)
        elif definition:        
            self._buffer += (form).format(contents) 
        else:                
            self._buffer += contents

    def _saveBuffer(self):
        if self._buffer:
            fn = self._bufferName.replace(" ","_") + ".txt"
            with open(fn, "a") as f:
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

        for el in soup.findAll("p"):
            if el.text == "Created with Microsoft OneNote 2010\nOne place for all your notes and information":
                continue  
            self.prevStep = (False, False, False, False)
            self.loopEl(el)
            self.addToBuffer(self.prevStep)
            self._buffer += "\n"
        
        self._saveBuffer()

        #print(self._buffer)
        
if __name__ == "__main__":
    Html2Zim()
