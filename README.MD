html2zim is an utility to convert HTML code produced by OneNote to Zim markup.
For every header found, it creates a .txt file that can be placed to a zim notebook folder.
It converts headers, boldness, italic font and anchor, as defined in definitions.json .

Look, this is not a magic box. There is too much of things in HTML that may pose a problem. Double check the result, some obscure tag constructions may be just skipped :(. But if you're stucked in the migration and you would copy-paste all the text and reformat every bold text manually, and then, this may really really help you.

Installation
=============
1) pip3 install --user beautifulsoup4
2) Download this.

Usage
=============
1) ./html2zim <your_html.html>
2) Place the .txt output to your zim folder.

Tip
=============
I installed a "gem" in OneNote that allows me to export whole section as HTML. This utility will produce a text file for every section subpage.
