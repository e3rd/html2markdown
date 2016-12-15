#!/usr/bin/env python3
from collections import OrderedDict
import re, json, ipdb, sys, os, traceback
from bs4 import BeautifulSoup as bs
from argparse import ArgumentParser
from contextlib import contextmanager
from subprocess import run, DEVNULL
from time import time
__help__ = """Converts html (output from OneNote) to Zim format."""

@contextmanager
def d():
    try:
        yield
    except:
        type, value, tb = sys.exc_info()
        tb= traceback.print_exc()        
        ipdb.post_mortem(tb)

class Html2Markdown:           
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
            if accords and "parent-name" in par:
                accords = (el.parent.parent.name == par["parent-name"])          

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
        #if "Microso" in el: import ipdb; ipdb.set_trace()
                   
        el.sout = el.replace("\n", " ")            
        el.sout = re.sub('\s+', ' ', el.sout) #.strip()                                                    
        with d():
            el.definition, el.form = self._getFormat(el)                                
        
        #ipdb.set_trace()
                
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
                if el.myTr and self.prevEl.myTr and el.findParent("table").tr == self.prevEl.myTr: # this was the first table row
                    for i in range(len(self.prevEl.myTr.findChildren("td"))):
                        self._buffer += "|----"
                    self._buffer += "|\n"
                    #ipdb.set_trace()
                    #el.findParent("table")self.prevEl.myTr # this was the first row
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
        elif el.definition == "stupid-nested-anchor":
            self._buffer += (el.form).format(el.parent.parent.attrs["href"], el.sout)
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
        self._buffer = self._buffer.strip()
        if self._buffer:            
            fn = self.saveDir + self._bufferName.replace(" ","_") + "." + self.extension
            #if os.path.isfile(fn) and fn not in self.createdFiles: print("Warning: File {} already exists, overwrite".format(fn))            
            with open(fn, "a" if fn in self.createdFiles else "w") as f:
                # for each header, we create a file but there might be multiple identical headers in the formatted file -> append
                f.write(self._buffer)
            self.createdFiles.add(fn)
            print("Saved to " + fn)
            self._buffer = ""
    
    def __init__(self, definitions_file, formatted_file, extension):
        self.definitions_file = definitions_file
        self.formatted_file = formatted_file
        self.extension = extension
        self.createdFiles = set()
        self._bufferName = os.path.splitext(os.path.basename(formatted_file))[0] #"out"
        self._buffer = ""        
        self.lastTd = None
        self.lastTr = None                
        self.saveDir = os.path.dirname(os.path.realpath(self.formatted_file)) + "/"
        
        self._checkMht()
        
        try:
            with open(self.formatted_file) as f: #, encoding="ISO-8859-1"
                soup = bs(f.read(), "lxml")
            with open(self.definitions_file) as data_file:    
                self.defs = json.load(data_file, object_pairs_hook=OrderedDict)
        except FileNotFoundError as e:
            #print("CHYBA")
            print(e.strerror + ": " + e.filename)            
            quit(-1)
        self.prevEl = soup.find("html")
        for el in soup.findAll(text=True):                        
            if el.strip("\n") == "":
                continue
            if el.parent and el.parent.text == "Created with Microsoft OneNote 2010\nOne place for all your notes and information":
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
    
    def _checkMht(self):
        if os.path.splitext(args.file)[1] in [".mht",".mhtml"]: # we should unpack MHT
            try: 
                os.mkdir("/tmp/mhtifier")
            except FileExistsError:
                pass
            mhtdir = "/tmp/mhtifier/"+os.path.basename(args.file) + "_" + str(time())    
            sys.argv = ["external-import-hack", "--unpack", args.file, mhtdir]
            from lib.mhtifier import main as Mhtifier        
            Mhtifier()            
            if not os.path.exists(mhtdir):
                print("Can't unpack MHT to {}".format(mhtdir))
                quit()
                
            # loop unpacked files
            found = []
            for root, _, files in os.walk(mhtdir):
                for file in files:
                    if ".htm" in file:
                        found.append(root + '/' + file)
                        
            # change formatted_file to current unpacked htm file
            if len(found) == 0:
                print("No files unpacked from MHT.")
                quit()
            elif len(found) > 1:
                print("Multiple files unpacked from MHT: {}. Not implented what to do now.".format(found))
                quit()
            else:
                self.formatted_file = found[0]                
                print("File to be reformatted: {}".format(self.formatted_file))
        
        
if __name__ == "__main__":    
    parser = ArgumentParser()    
    parser.add_argument('-z','--zim', help='use zim syntax',action="store_true")
    parser.add_argument('-m','--markdown', help='use markdown syntax',action="store_true")
    parser.add_argument('file', help="source file for reformatting", default="None")
    if len(sys.argv) < 2:  
        print(__help__)
        parser.print_help()
        quit()    
    args = parser.parse_args()
                                 
    # load definition file
    if args.zim: 
        file, ext = "zim", "txt"    
    else: 
        file, ext = "markdown", "md" # markdown is default
    def_file = os.path.dirname(os.path.realpath(sys.argv[0]))+"/definitions/"+file+".json"
    if not os.path.isfile(def_file):
         print("Definition file doesnt exist at " + def_file)
         quit()        

    # launch reformatting
    Html2Markdown(def_file, args.file, ext)    