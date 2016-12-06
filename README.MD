html2markdown is an utility to convert HTML code produced by OneNote to Markdown markup OR Zim markup.

The HTML has often invalid semantics so that it seems that parsers give up and skip some formatting. IE header are not h1 tag but a superfluous fancy styling. This project aims to convert such invalid semantics – you can setup what style means the tags.

For every header found, it creates a .txt file that can be placed to a zim notebook folder.
It converts headers, boldness, italic font, anchor, as defined in definitions.json . It handles lists and tables as well.

Look, this is not a magic box. I recommend to check the result every time. But if you're stucked in the migration and you would copy-paste all the text and reformat every bold text manually, then this may really really help you.

Installation
=============
* `pip3 install --user beautifulsoup4`
* Download this.

Usage
=============
* `./html2zim --zim/--markdown <your_html.html>`
* Place the .txt output to your zim folder.

Tip
=============
* I installed a "gem" in OneNote that allows me to export whole section as HTML. This utility will produce a text file for every section subpage.
* If you prefer to export MHT from OneNote, you can unpack it with https://github.com/Modified/MHTifier (included in lib)

Missing features
=============
* Nested lists.
* Nested bold text in an anchor -> anchor link gets skipped.
* Convert rather to Markdown; to zim with flag.
* When accessed "[[" in the text in zim mode, ask if it's meant to be a link
* Images.
* Table aligning.
* Integrate mht unpacker as a lib.