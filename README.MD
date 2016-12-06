html2zim is an utility to convert HTML code produced by OneNote to Zim markup.
For every header found, it creates a .txt file that can be placed to a zim notebook folder.
It converts headers, boldness, italic font, anchor, as defined in definitions.json . It handles <li> lists and tables as well.

Look, this is not a magic box. I recommend to check the result every time. But if you're stucked in the migration and you would copy-paste all the text and reformat every bold text manually, then this may really really help you.

Installation
=============
* `pip3 install --user beautifulsoup4`
* Download this.

Usage
=============
* `./html2zim <your_html.html>`
* Place the .txt output to your zim folder.

Tip
=============
I installed a "gem" in OneNote that allows me to export whole section as HTML. This utility will produce a text file for every section subpage.

Not implemented so far
=============
* Nested lists.
* Nested bold text in an anchor -> anchor link gets skipped.
* Convert rather to Markdown; to zim with flag.
* When accessed "[[" in the text, ask if it's meant to be a link
