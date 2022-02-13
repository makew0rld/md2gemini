"""
All the renderers that convert markdown to gemini.
"""

import mistune
import functools
from .unitable import UniTable, ArraySizeError


NEWLINE = "\r\n"  # For Windows support
PARAGRAPH_DELIM = "\x02"  # The marker for paragraph start and end, for post processing
LINK_DELIM = "\x03"
LINEBREAK = "\x01"  # Represents a hard linebreak that should not be changed


class GeminiRenderer(
    mistune.HTMLRenderer
):  # Actually BaseRenderer should be used but this isn't available

    # NAME = "gemini"

    def __init__(
        self,
        code_tag="",
        img_tag="[IMG]",
        indent=" ",
        ascii_table=False,
        links="newline",
        plain=False,
        strip_html=False,
        base_url="",
        md_links=False,
        link_func=None,
        table_tag="table",
        checklist=True,
    ):
        # Disable all the HTML renderer's messing around:
        super().__init__(escape=False, allow_harmful_protocols=True)

        self.md_links = md_links
        self.link_func = link_func
        if base_url is None:
            base_url = ""
        if len(base_url) > 0 and base_url[-1] == "/":
            base_url = base_url[:-1]
        self.base_url = base_url
        self.plain = plain
        self.strip_html = strip_html
        self.ascii = ascii_table
        if indent is None:
            self.indent = "  "
        else:
            self.indent = indent
        if code_tag is None:
            code_tag = ""
        self.code_tag = code_tag
        if img_tag is None:
            img_tag = ""
        self.img_tag = " " + img_tag
        if table_tag is None:
            table_tag = "table"
        self.table_tag = table_tag
        self.checklist = checklist
        # Tables
        self.unitable = None
        self.table_cols_align = []  # List of column alignments: ["l", "r", "c"]
        # Footnote links
        self.links = links
        if self.links in ["paragraph", "at-end", "copy"]:
            self.footnotes_enabled = True
        else:
            self.footnotes_enabled = False
        self.footnote_num = 0  # The number of the last footnote is stored here
        self.footnotes = (
            []
        )  # ["https://example.com/", ...] - footnotes per paragraph/document stored here
        self.footnote_texts = (
            []
        )  # ["link text", ...] - used for links "copy" mode, when link text also needs to be stored

    def _gem_link(self, link, text=None):
        # Links are handled in post processing, these control characters
        # are just used to denote paragraph start and end. They were picked
        # because they will never be typed in normal text editing.

        link = link.strip()
        if link.startswith("/"):
            link = self.base_url + link

        if text is None:
            return LINK_DELIM + "=> " + link.strip() + LINK_DELIM
        return LINK_DELIM + "=> " + link.strip() + " " + text.strip() + LINK_DELIM

    def _add_footnote(self, link, text):
        self.footnote_num += 1
        self.footnotes.append(link)

        if self.links == "copy":
            self.footnote_texts.append(text)
            return text
        return text + "[" + str(self.footnote_num) + "]"

    def _render_footnotes(self):
        if not self.footnotes_enabled:
            return ""
        if self.footnotes == []:
            return ""

        ret = ""
        length = len(self.footnotes)
        if self.links == "copy":
            for i, url in enumerate(self.footnotes):
                # Calculate the relative footnote number - there could be five footnotes
                # for this paragraph, but now 10 in total.

                # Example footnote, in a client view:
                # copied link text
                # Actual footnote output:
                # => gemini://gus.guru/ copied link text
                ret += self._gem_link(url, self.footnote_texts[i])
        else:
            for i, url in enumerate(self.footnotes):
                # Example footnote, in a client view:
                # 10: gemini://gus.guru/
                # Actual footnote output:
                # => gemini://gus.guru/ 10: gemini://gus.guru/
                ret += self._gem_link(
                    url, str((self.footnote_num - length) + 1 + i) + ": " + url.strip()
                )

        return ret

    # Inline elements

    def text(self, text):
        return text

    def link(self, link, text=None, title=None):
        # title is ignored because it doesn't apply to Gemini

        if link.startswith("#"):
            # Invalid for Gemini
            if text is None:
                return link
            return text
        if self.links == "off":
            # Don't link, just leave the text as it was written
            if text is None:
                return link
            return text

        if self.md_links and "//" not in link:
            # Relative link, and md -> gmi conversion is enabled
            if link.endswith(".md"):
                link = link[:-2] + "gmi"
            elif ".md#" in link:
                index = link.index(".md#")
                link = link[: index + 1] + "gmi"

        if callable(self.link_func):
            # A custom function to treat links is provided
            link = self.link_func(link)

        if self.footnotes_enabled:
            if text is None or text.strip() == "":
                # Insert the link inline, but with a footnote too
                return self._add_footnote(link, link)
            else:
                return self._add_footnote(link, text)

        return self._gem_link(link, text)

    def image(self, src, alt="", title=None):
        """Turn images into regular Gemini links."""

        if alt is None:
            alt = ""

        if self.links == "off":
            if alt == "":
                return src
            return alt

        # Images shouldn't need footnotes, so it's just added as a link no matter what

        return self._gem_link(src, alt.strip() + self.img_tag)

    def emphasis(self, text):
        if self.plain:
            return text
        return "*" + text + "*"

    def strong(self, text):
        if self.plain:
            return text
        return "**" + text + "**"

    def codespan(self, text):
        if self.plain:
            return text
        return "`" + text + "`"

    def linebreak(self):
        # return "<LB>"
        return LINEBREAK

    def newline(self):
        # return "<NL>"
        return ""

    def inline_html(self, html):
        if self.plain or self.strip_html:
            return ""
        return html

    # Block level elements

    def paragraph(self, text):
        # Paragraphs are handled in post processing, these control characters
        # are just used to denote paragraph start and end. They were picked
        # because they will never be typed in normal text editing.

        if (
            self.links == "paragraph"
            and self.footnotes_enabled
            and text.count("\n") <= 1
            and len(self.footnotes) == 1
            and text.rstrip().endswith("[" + str(self.footnote_num) + "]")
        ):
            # The whole paragraph is just one line, just the link
            # So there shouldn't be a footnote
            ret = (
                PARAGRAPH_DELIM
                + self._gem_link(
                    self.footnotes[0],
                    # Remove the footnote part from the text, the [X] at the end
                    text.rstrip()[: -(len(str(self.footnote_num)) + 2)],
                )
                + PARAGRAPH_DELIM
            )
            # Remove footnote from list
            self.footnotes.pop()
            self.footnote_num -= 1
            self.footnotes = []  # Reset them for the next paragraph
            return ret

        if (
            self.links == "copy"
            and len(self.footnotes) == 1
            and self.footnote_texts[0] == text
        ):
            # The whole paragraph is just one big link, so it should just be added as a link
            ret = (
                PARAGRAPH_DELIM
                + self._gem_link(self.footnotes[0], text)
                + PARAGRAPH_DELIM
            )
            self.footnotes = []
            self.footnote_texts = []
            return ret

        text += self._end_of_paragraph()

        return PARAGRAPH_DELIM + text + PARAGRAPH_DELIM

    def _end_of_paragraph(self):
        # Process footnotes if it should
        if self.links in ["paragraph", "copy"] and len(self.footnotes) > 0:
            ret = PARAGRAPH_DELIM + self._render_footnotes() + PARAGRAPH_DELIM
            self.footnotes = []
            self.footnote_texts = []  # For self.links == "copy"
            return ret

        return ""

    def heading(self, text, level):
        return self._end_of_paragraph() + "#" * level + " " + text + NEWLINE * 2

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
        start = "```" + self.code_tag + NEWLINE
        if not info is None:
            start = "```" + info + NEWLINE

        if code.endswith("\n"):
            code = code[:-1]
        if code.endswith("\n"):
            code = code[:-1]
        return start + code + NEWLINE + "```" + NEWLINE * 2

    def block_quote(self, text):
        """Add a quote mark to the beginning of each line."""

        lines = (
            text.replace(PARAGRAPH_DELIM, "\n")
            .replace(LINEBREAK, "\n")
            .strip()
            .splitlines()
        )
        ret = ""
        for line in lines:
            ret += (
                "> " + line.strip() + LINEBREAK
            )  # Linebreak used to prevent removal later
        return PARAGRAPH_DELIM + ret + PARAGRAPH_DELIM

    def block_html(self, html):
        if self.strip_html:
            return NEWLINE
        return self.block_code(html, "html")

    def block_error(self, html):
        return self.block_code(html, "html")

    def list_item(self, text, level):
        # It is necessary to split the text on newline, since markdown
        # allows for list items to be split across multiple lines.
        # We need to strip whitespace from these items and add it ourselves,
        # since the text doesn't guarantee any particular formatting for
        # these items.
        items = [item.strip() for item in text.splitlines()]
        text = functools.reduce(lambda x, y: x + " " + y, items)
        return text + NEWLINE

    def list(self, text, ordered, level, start=None):
        """Gemini only defines single-level unordered lists.

        This uses indenting to do sub-levels.
        Ordered list items just use 1. 2. etc, as plain text.
        """

        # First level of list means `level = 1`

        if start is None:
            start = 1
        # Any empty lines should have been consumed by list_item,
        # so no need to check for empty lines here.
        items = text.splitlines()
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
                    ret_items.append(
                        self.indent * (level - 1) + str(i + start) + ". " + item.strip()
                    )

        else:
            # Return an unordered list using the official Gemini list character: *
            # Indenting is used for sub-levels
            for item in items:
                if item.startswith(self.indent):
                    # See the comment above for why this check is required.
                    ret_items.append(item)
                else:
                    ret_items.append(self.indent * (level - 1) + "* " + item.strip())

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
        return (
            "```"
            + self.table_tag
            + NEWLINE
            + self.unitable.draw()
            + NEWLINE
            + "```"
            + NEWLINE
        )

    def table_head(self, text):
        self._init_table()
        # The table_cell func splits each column using newlines
        try:
            self.unitable.header(
                text.split("\n")[:-1]  # \n is used to delimit cells internally
            )
        except ArraySizeError:
            # raise Exception("Malformed table")
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
                text.split("\n")[:-1]  # \n is used to delimit cells internally
            )
        except ArraySizeError:
            # raise Exception("Malformed table")
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
        return (
            text.strip() + "\n"
        )  # \n is used to separate cells from each other in other funcs

    # Task list / check list support
    # https://github.com/makeworld-the-better-one/md2gemini/issues/19

    def task_list_item(self, text, level, checked):
        if self.checklist:
            if checked:
                symbol = "\U0001f5f9"  # BALLOT BOX WITH BOLD CHECK
            else:
                symbol = "\u2610"  # BALLOT BOX
        else:
            if checked:
                symbol = "[x]"
            else:
                symbol = "[ ]"
        return self.list_item(symbol + " " + text, level)

    # Strikethough can't be supported
    # Footnotes aren't supported right now
