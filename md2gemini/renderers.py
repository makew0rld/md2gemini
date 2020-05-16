"""
All the renderers that convert markdown to gemini.
"""

import mistune
from .unitable import UniTable, ArraySizeError

NEWLINE = "\r\n"

class GeminiRenderer(mistune.HTMLRenderer):  # Actually BaseRenderer should be used but this isn't available
    
    #NAME = "gemini"

    def __init__(self, img_tag="[IMG]", indent="  ", ascii_table=False):
        # Disable all the HTML renderer's messing around:
        super().__init__(escape=False, allow_harmful_protocols=True)

        if indent is None:
            self.indent = "  "
        else:
            self.indent = indent
        self.ascii = ascii_table
        if img_tag is None:
            img_tag = ""
        self.img_tag = " " + img_tag
        self.unitable = None
        self.table_cols_align = []  # List of column alignments: ["l", "r", "c"]

    def _gem_link(self, link, text=None):
        if text is None:
            return "=> " + link.strip()# + NEWLINE
        return "=> " + link.strip() + " " + text.strip()# + NEWLINE

    # Inline elements

    def text(self, text):
        """No HTML escaping required."""
        
        return text

    def link(self, link, text=None, title=None):
        # title is ignored because it doesn't apply to Gemini
        # TODO: Support using footnotes instead of putting inline links on their own line
        return NEWLINE + self._gem_link(link, text) + NEWLINE
    
    def image(self, src, alt="", title=None):
        """Turn images into regular Gemini links."""

        if alt is None or alt == "":
            return self._gem_link(src)
        return self._gem_link(src, alt.strip() + self.img_tag)
    
    def emphasis(self, text):
        return text
    
    def strong(self, text):
        return text
    
    def codespan(self, text):
        """Leave inline code as it was written. Don't turn it into a code block."""

        return "`" + text + "`"
    
    def linebreak(self):
        return NEWLINE
        #return "<LB>"
    
    def newline(self):        
        #return "<NL>"
        return ""
    
    def inline_html(self, html):
        return html

    # Block level elements

    def paragraph(self, text):
        return text + NEWLINE * 2
        #return text + "<PG>"
    
    def heading(self, text, level):
        return "#" * level + " " + text + NEWLINE
    
    def thematic_break(self):
        """80 column split using hyphens."""

        return "-" * 80 + NEWLINE * 2
    
    def block_text(self, text):
        # Idk what this is, it's not defined in the CommonMark spec,
        # and the HTML renderer also just returns text
        return text + NEWLINE
    
    def block_code(self, code, info=None):
        # Gemini doesn't support code block infos, but it doesn't matter
        # Adding them might make this more compatible
        start = "```" + NEWLINE
        if not info is None:
            start = "```" + info + NEWLINE
        return start + code + "```" + NEWLINE
    
    def block_quote(self, text):
        return "> " + text
    
    def block_html(self, html):
        return self.block_code(html, "html")
    
    def block_error(self, html):
        return self.block_code(html, "html")
    
    def list_item(self, text, level):
        # No modifications, the func below handles that
        return text + NEWLINE

    def list(self, text, ordered, level, start=None):
        """Gemini only defines single-level unordered lists.

        This uses indenting to do sub-levels.
        Ordered list items just use 1. 2. etc, as plain text.
        """
        
        # First level of list means `level = 1`

        if start is None:
            start = 1
        text = text.replace("\r\n", "\n")  # Make sure there's no extra <CR>s
        items = text.split("\n")
        # Remove possible empty strings
        items = [x for x in items if x != ""]
        ret_items = []

        if ordered:
            # Recreate the ordered list for each item, then return it
            # This just returns a plain text list.
            for i, item in enumerate(items):
                if item.startswith(self.indent):
                    # It's an already processed sub-level item, don't do anything.
                    # This kind of check is needed because mistune passes nested list items
                    # to the renderer multiple times. Once as N-level list, and then once again
                    # as a part of a flattened level 1 list.
                    # This check prevents the item from being processed again when it appears
                    # in that second list.
                    ret_items.append(item)
                else:
                    ret_items.append(self.indent * (level-1) + str(i+start) + ". " + item.strip())

        else:   
            # Return an unordered list using the official Gemini list character: *
            # Indenting is used for sub-levels
            for item in items:
                if item.startswith(self.indent):
                    # See the comment above for why this check is required.
                    ret_items.append(item)
                else:
                    ret_items.append(self.indent * (level-1) + "* " + item.strip())
        
        return NEWLINE.join(ret_items) + NEWLINE * 2

    # Elements that rely on plugins:

    # Tables
    # Most of the funcs just return the text unchanged because the actual text processing
    # is done at the end, using the UniTable class.

    def _init_table(self):
        self.unitable = UniTable()
        if self.ascii:
            self.unitable.set_style("default")
        else:
            self.unitable.set_style("light")

    def table(self, text):
        # Called at the end I think, once all the table elements
        # have been processed
        # Put the table in a preprocessed block
        return "```table" + NEWLINE + self.unitable.draw() + NEWLINE + "```" + NEWLINE

    def table_head(self, text):
        self._init_table()
        # The table_cell func splits each column using newlines
        try:
            self.unitable.header(
                text.split("\n")[:-1]
            )
        except ArraySizeError:
            #raise Exception("Malformed table")
            pass
        # Set and clear the alignment data, now that the number of columns should be known
        self.unitable.set_cols_align(self.table_cols_align)
        self.unitable.set_cols_valign(["m"] * len(self.table_cols_align))
        self.table_cols_align = []
        return text
    
    def table_body(self, text):
        return ""

    def table_row(self, text):
        try:
            self.unitable.add_row(
                # The table_cell func splits each column using newlines
                text.split("\n")[:-1]
            )
        except ArraySizeError:
            #raise Exception("Malformed table")
            pass
        self.table_cols_align = []
        # The text processing is done in other funcs
        return text
    
    def table_cell(self, text, align=None, is_head=False):
        if align in ["left", "right", "center"]:
            self.table_cols_align.append(align[0])  # l, r, or c
        else:
            # If align is None or something unknown happened
            self.table_cols_align.append("l")
        return text.strip() + "\n"  # \n is used to separate cells from each other in other funcs

    # Strikethough can't be supported
    # Footnotes aren't supported right now
