# -*- coding: utf-8 -*-

# The below code was NOT written by me.
# It was taken from https://github.com/fariello/texttable/blob/master/unitable.py
# which is a fork by @fariello of the original texttable python package by @foutaise
# According to the LICENSE file in that repo, this code is under the MIT license,
# meaning it is legal for me to reuse it here.
# Here is the LICENSE text, that applies to this file ONLY:
# The MIT License (MIT)

# Copyright (c) 2019 Gerome Fournier

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# After this line, the original copied file begins:

# texttable - module for creating simple ASCII tables
# Copyright (C) 2003-2019 Gerome Fournier <jef(at)foutaise.org>

"""module for creating simple ASCII tables


Example:

    table = UniTable()
    table.set_cols_align(["l", "r", "c"])
    table.set_cols_valign(["t", "m", "b"])
    table.add_rows([["Name", "Age", "Nickname"],
                    ["Mr\\nXavier\\nHuon", 32, "Xav'"],
                    ["Mr\\nBaptiste\\nClement", 1, "Baby"],
                    ["Mme\\nLouise\\nBourgeau", 28, "Lou\\n\\nLoue"]])
    print table.draw() + "\\n"

    table = UniTable()
    table.set_deco(UniTable.HEADER)
    table.set_cols_dtype(['t',  # text
                          'f',  # float (decimal)
                          'e',  # float (exponent)
                          'i',  # integer
                          'a']) # automatic
    table.set_cols_align(["l", "r", "r", "r", "l"])
    table.add_rows([["text",    "float", "exp", "int", "auto"],
                    ["abcd",    "67",    654,   89,    128.001],
                    ["efghijk", 67.5434, .654,  89.6,  12800000000000000000000.00023],
                    ["lmn",     5e-78,   5e-78, 89.4,  .000000000000128],
                    ["opqrstu", .023,    5e+78, 92.,   12800000000000000000000]])
    print table.draw()

Result:

    +----------+-----+----------+
    |   Name   | Age | Nickname |
    +==========+=====+==========+
    | Mr       |     |          |
    | Xavier   |  32 |          |
    | Huon     |     |   Xav'   |
    +----------+-----+----------+
    | Mr       |     |          |
    | Baptiste |   1 |          |
    | Clement  |     |   Baby   |
    +----------+-----+----------+
    | Mme      |     |   Lou    |
    | Louise   |  28 |          |
    | Bourgeau |     |   Loue   |
    +----------+-----+----------+

    text   float       exp      int     auto
    ===========================================
    abcd   67.000   6.540e+02   89    128.001
    efgh   67.543   6.540e-01   90    1.280e+22
    ijkl   0.000    5.000e-78   89    0.000
    mnop   0.023    5.000e+78   92    1.280e+22
"""

from __future__ import division

# @makeworld-the-better-one removed the first underscore of each of those variables
# to help make sure packages don't get messed up

_all__ = ["UniTable", "ArraySizeError"]

_author__ = 'Gerome Fournier <jef(at)foutaise.org>'
_license__ = 'MIT'
_version__ = '1.6.2'
_credits__ = """\
Jeff Kowalczyk:
    - textwrap improved import
    - comment concerning header output

Anonymous:
    - add_rows method, for adding rows in one go

Sergey Simonenko:
    - redefined len() function to deal with non-ASCII characters

Roger Lew:
    - columns datatype specifications

Brian Peterson:
    - better handling of unicode errors

Frank Sachsenheim:
    - add Python 2/3-compatibility

Maximilian Hils:
    - fix minor bug for Python 3 compatibility

frinkelpi:
    - preserve empty lines

gfariello:
    - Added unicode box border options, made errors more informative, corrected typos
"""

import sys
import unicodedata

# define a text wrapping function to wrap some text
# to a specific width:
# - use cjkwrap if available (better CJK support)
# - fallback to textwrap otherwise
try:
    import cjkwrap
    def textwrapper(txt, width):
        return cjkwrap.wrap(txt, width)
except ImportError:
    try:
        import textwrap
        def textwrapper(txt, width):
            return textwrap.wrap(txt, width)
    except ImportError:
        sys.stderr.write("Can't import textwrap module!\n")
        raise

# define a function to calculate the rendering width of a unicode character
# - use wcwidth if available
# - fallback to unicodedata information otherwise
try:
    import wcwidth
    def uchar_width(c):
        """Return the rendering width of a unicode character
        """
        return max(0, wcwidth.wcwidth(c))
except ImportError:
    def uchar_width(c):
        """Return the rendering width of a unicode character
        """
        if unicodedata.east_asian_width(c) in 'WF':
            return 2
        elif unicodedata.combining(c):
            return 0
        else:
            return 1

from functools import reduce

if sys.version_info >= (3, 0):
    unicode_type = str
    bytes_type = bytes
    str_class = str
else:
    unicode_type = unicode
    bytes_type = str
    str_class = basestring
    pass

def obj2unicode(obj):
    """Return a unicode representation of a python object"""
    if isinstance(obj, unicode_type):
        return obj
    elif isinstance(obj, bytes_type):
        try:
            return unicode_type(obj, 'utf-8')
        except UnicodeDecodeError as strerror:
            sys.stderr.write("UnicodeDecodeError exception for string '%s': %s\n" % (obj, strerror))
            return unicode_type(obj, 'utf-8', 'replace')
    else:
        return unicode_type(obj)


def len(iterable):
    """Redefining len here so it will be able to work with non-ASCII characters    """
    if isinstance(iterable, bytes_type) or isinstance(iterable, unicode_type):
        return sum([uchar_width(c) for c in obj2unicode(iterable)])
    else:
        return iterable.__len__()


class ArraySizeError(Exception):
    """Exception raised when specified rows don't fit the required size"""
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg, '')
    def __str__(self):
        return self.msg

class FallbackToText(Exception):
    """Used for failed conversion to float"""
    pass

2
class UTableBaseClass:
    """
    This is the base class for all UTable classes. It should probably not be instantiated directly.
    """
    def __init__(self,parent=None):
        self.parent = parent
        self.needs_recalc = True
        pass
    def _chktype(self,what,clss,val,none_ok=False):
        if none_ok and val is None:
            return val
        if not isinstance(val, clss):
            raise ValueError("ERROR: %s must be an instance of %s, '%s' is a %s." %(what,clss.__name__,val,type(val).__name__))
        return val
    def set_parent(self,val,clss):
        self._parent = self._chktype('parent',clss,val,True)
        pass
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self,val):
        self.set_parent(val)
        pass
    @property
    def needs_recalc(self):
        return self._needs_recalc
    @needs_recalc.setter
    def needs_recalc(self,val):
        self._chktype('needs_recalc',bool,val)
        if self.parent is not None:
            self.parent.needs_recalc = val
            pass
        self._needs_recalc = val
        pass
    @property
    def width(self):
        return self._width;
    @width.setter
    def width(self,val):
        self._width = self._chktype('width',int,val,True)
    @property
    def witdth(self): return self._width;
    @width.setter
    def height(self,val):
        self._height = self._chktype('height',int,val,True)

class UTable:
    def __init__(self,rows=[],parent=None):
        super().__init__(self,parent)
        self._min_width = None
        self._max_width = None
        self._height = None
        self._rows = []
        self._cols = []
        pass
    pass

class URow:
    def __init__(self,table,cells=[]):
        super().__init__(parent)
        pass
    pass

class UCol:
    def __init__(self,table,cells=[]):
        super().__init__(parent)
        pass
    pass

class Cell:
    def __init__(self,value="",row=None,col=None):
        self._recalc = True
        self.value = value
        self.row = row
        self.col = column
        pass
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self,val):
        if val == self._value:
            return
        self._recalc = True
        if isinstance(val,str_class):
            self._value = val.splitlines()
        else:
            self._value = [val]
            pass
        pass
    @property
    def row(self):
        return self._row
    @row.setter
    def row(self,val):
        if val == self._row:
            return
        if val is None or isinstance(val,int):
            self._row = val
            self._recalc = True
            pass
        raise ValueError("ERROR: row must be an integer. Received '%s' which is a %s." %(val,type(val).__name__))
    @property
    def col(self):
        return self._col
    @col.setter
    def col(self,val):
        if val == self._col:
            return
        if val is None or isinstance(val,int):
            self._col = val
            self._recalc = True
            pass
        raise ValueError("ERROR: col must be an integer. Received '%s' which is a %s." %(val,type(val).__name__))
    @property
    def width(self):
        return self._width

class UniTable:
    BORDER = 1
    HEADER = 1 << 1
    HLINES = 1 << 2
    VLINES = 1 << 3
    # --- gfariello -- Start -- Added to support new styles.
    TOP = 0
    MIDDLE  = 1
    BOTTOM = 2
    STYLES = {
        "bold":         "━┃┏┓┗┛┣┫┳┻╋━┣┫╋",
        "default":      "-|+=",
        "double":       "═║╔╗╚╝╠╣╦╩╬═╠╣╬",
        "very_light":   "─│┌┐└┘├┤┬┴┼─├┤┼",
        "light":        "─│┌┐└┘├┤┬┴┼═╞╡╪",
        "round":        "─│╭╮╰╯├┤┬┴┼─├┤┼",
        "round2":       "─│╭╮╰╯├┤┬┴┼═╞╡╪",
        "simple":       "-|+-",
        }
    STYLE_MAPPER = {
        "heavy": {
            "---w": " ",
            "--e-": " ",
            "--ew": "━",
            "-s--": " ",
            "-s-w": "┓",
            "-se-": "┏",
            "-sew": "┳",
            "n---": " ",
            "n--w": "┛",
            "n-e-": "┗",
            "n-ew": "┻",
            "ns--": "┃",
            "ns-w": "┫",
            "nse-": "┣",
            "nsew": "╋",
        },
        "light": {
            "---w": " ",
            "--e-": " ",
            "--ew": "-",
            "-s--": " ",
            "-s-w": "┐",
            "-se-": "┌",
            "-sew": "┬",
            "n---": " ",
            "n--w": "┘",
            "n-e-": "└",
            "n-ew": "┴",
            "ns--": "│",
            "ns-w": "┤",
            "nse-": "├",
            "nsew": "┼",
        },
        "round": {
            "---w": " ",
            "--e-": " ",
            "--ew": "-",
            "-s--": " ",
            "-s-w": "╮",
            "-se-": "╭",
            "-sew": "┬",
            "n---": " ",
            "n--w": "╯",
            "n-e-": "╰",
            "n-ew": "┴",
            "ns--": "│",
            "ns-w": "┤",
            "nse-": "├",
            "nsew": "┼",
        },
        "double": {
            "---w": " ",
            "--e-": " ",
            "--ew": "═",
            "-s--": " ",
            "-s-w": "╗",
            "-se-": "╔",
            "-sew": "╦",
            "n---": " ",
            "n--w": "╝",
            "n-e-": "╚",
            "n-ew": "╩",
            "ns--": "║",
            "ns-w": "╣",
            "nse-": "╠",
            "nsew": "╬",
        },
        "heavy:light": {
            "---w:--e-": "╾",
            "---w:-s--": "┑",
            "---w:-se-": "┲",
            "---w:n---": "┙",
            "---w:n-e-": "┺",
            "---w:ns--": "┥",
            "---w:nse-": "┽",
            "--e-:---w": "╼",
            "--e-:-s--": "┍",
            "--e-:-s-w": "┮",
            "--e-:n---": "┙",
            "--e-:n--w": "┶",
            "--e-:ns--": "┝",
            "--e-:ns-w": "┾",
            "--ew:-s--": "┰",
            "--ew:n---": "┸",
            "--ew:ns--": "┿",
            "-s--:---w": "┒",
            "-s--:--e-": "┎",
            "-s--:--ew": "┰",
            "-s--:n---": "╽",
            "-s--:n--w": "┧",
            "-s--:n-e-": "┟",
            "-s--:n-ew": "╁",
            "-s-w:--e-": "┱",
            "-s-w:n---": "┧",
            "-s-w:n-e-": "╅",
            "-se-:---w": "┲",
            "-se-:n---": "┢",
            "-se-:n--w": "╆",
            "-sew:n---": "╈",
            "n---:---w": "┖",
            "n---:--e-": "┚",
            "n---:--ew": "┸",
            "n---:-s--": "╿",
            "n---:-s-w": "┦",
            "n---:-se-": "┞",
            "n---:-sew": "╀",
            "n--w:--e-": "┹",
            "n--w:-s--": "┩",
            "n--w:-se-": "╃",
            "n-e-:---w": "┺",
            "n-e-:-s--": "┡",
            "n-e-:-s-w": "╄",
            "n-ew:-s--": "╇",
            "ns--:---w": "┨",
            "ns--:--e-": "┠",
            "ns--:--ew": "╂",
            "ns-w:--e-": "╉",
            "nse-:---w": "╊",
            }
            }
    # --- gfariello -- End -- Added to support new styles.

    # --- gfariello -- Start -- Added init with table def.
    # NOTE: See below about backward compatability
    def __init__(self, rows=None, max_width=80):
    # --- gfariello -- End -- Added init with table def.
        """Constructor

        - max_width is an integer, specifying the maximum width of the table
        - if set to 0, size is unlimited, therefore cells won't be wrapped
        """
        self._has_border = True
        self._has_header = True
        self._has_hline_between_headers = True
        self._has_hline_header_2_cell = True
        self._has_hline_between_cells = True
        self._has_vline_between_headers = True
        self._has_vline_header_2_cell = True
        self._has_vline_between_cells = True
        self.set_max_width(max_width)
        self._precision = 3

        self._deco = UniTable.VLINES | UniTable.HLINES | UniTable.BORDER | \
            UniTable.HEADER
        self.set_style("default")
        self._pad = 1
        self.reset()
        # --- gfariello -- Start -- Added to support rows arg (i.e., adding
        # entire table definition in initilization). NOTE: This changed the
        # order (max_width is now one arg later) and therefore has a chance of
        # breaking older code that called UniTable(50) but not
        # UniTable(max_width=50). It felt less intuitive to have the rows
        # definition after the max_width, but if backwards compatibility is
        # more important, just swap the order of rows and max_width.
        if rows is not None:
            self.add_rows(rows)
            pass
        # --- gfariello -- End -- Added to support rows arg.
        pass
    @property
    def has_border(self):
        return self._has_border
    @has_border.setter
    def has_border(self,value):
        self._has_border = value
        return value

    @property
    def has_header(self):
        return self._has_header
    @has_header.setter
    def has_header(self,value):
        self._has_header = value
        return value

    def reset(self):
        """Reset the instance

        - reset rows and header
        """

        self._hline_string = None
        self._row_size = None
        self._header = []
        self._rows = []
        return self

    def set_max_width(self, max_width):
        """Set the maximum width of the table

        - max_width is an integer, specifying the maximum width of the table
        - if set to 0, size is unlimited, therefore cells won't be wrapped
        """
        self._max_width = max_width if max_width > 0 else False
        return self

    def set_style(self, style="light"):
        """Set the characters used to draw lines between rows and columns to one of four box types:

        "light": Use unicode light box borders (─│┌┐└┘├┤┬┴┼)
        "bold":  Use unicode bold box borders (━┃┏┓┗┛┣┫┳┻╋)
        "double": Use unicode double box borders (═║╔╗╚╝╠╣╦╩╬)

        Default if none provided is "light"
        """
        if style in UniTable.STYLES:
            return self.set_chars(UniTable.STYLES[style])
        raise ValueError("style must be one of '%s' not '%s'" %("','".join(sorted(UniTable.STYLES.keys())),style))

    def _set_chars(self, array):
        """Set the characters used to draw lines between rows and columns in the following format:
        [
          ew,    # The character connecting east and west to use for a horizantal line (e.g. "-" or "─" )
          ns,    # The character connecting north and south to use for a vertical line (e.g. "|" or "|" )
          se,    # The character connecting south and east to use for the top- and left-most corner (e.g. "+", or "┌")
          sw,    # The character connecting south and west to use for the top- and right-most corner (e.g. "+" or "┐")
          ne,    # The character connecting north and east to use for the bottom- and left-most corner (e.g. "+" or "└")
          nw,    # The character connecting north and west to use for the bottom- and right-most corner (e.g. "+" or "┘")
          nse,   # The character connecting north, south, and east (e.g., "+" or "┤")
          nsw,   # The character connecting north, south, and west (e.g., "+" or "├")
          sew,   # The character connecting south, east, and west (e.g., "+" or "┬")
          new,   # The character connecting north, east, and west (e.g., "+" or "┴")
          nsew,  # The character connecting north, south, east, and west (e.g., "+" or "┴")
          hew,   # The character connecting east and west to use for a line separating headers (e.g. "=" or "═" )
          hnse,  # The character connecting north, south and east to use for a line separating headers (e.g. "+" or "╞" )
          hnsw,  # The character connecting north, south, and west to use for a line separating headers (e.g. "+" or "╡" )
          hnsew, # The character connecting north, south, east and west to use for a line separating headers (e.g. "+" or "╪" )
        ]
        For legacy default it would be "-|+++++++++=+++"
        """
        if len(array) != 15:
            raise ArraySizeError("string/array should contain 15 characters not %d as in '%s'" %(len(array),array))
        (
            self._char_ew,
            self._char_ns,
            self._char_se,
            self._char_sw,
            self._char_ne,
            self._char_nw,
            self._char_nse,
            self._char_nsw,
            self._char_sew,
            self._char_new,
            self._char_nsew,
            self._char_hew,
            self._char_hnse,
            self._char_hnsw,
            self._char_hnsew,
        ) = array
        return self

    def set_chars(self, array):
        """Set the characters used to draw lines between rows and columns

        - the array should contain 4 fields:

            [horizontal, vertical, corner, header]

        - default is set to:

            ['-', '|', '+', '=']
        """
        if len(array) == 15:
            return self._set_chars(array)
        if len(array) != 4:
            raise ArraySizeError("string/array should contain either 4 or 15 characters not %d as in '%s'" %(len(array),array))
        (hor,ver,cor,hea) = array
        return self._set_chars([hor,ver,cor,cor,cor,cor,cor,cor,cor,cor,cor,hea,cor,cor,cor])

    def set_deco(self, deco):
        """Set the table decoration

        - 'deco' can be a combinasion of:

            UniTable.BORDER: Border around the table
            UniTable.HEADER: Horizontal line below the header
            UniTable.HLINES: Horizontal lines between rows
            UniTable.VLINES: Vertical lines between columns

           All of them are enabled by default

        - example:

            UniTable.BORDER | UniTable.HEADER
        """

        self._deco = deco
        return self

    def set_header_align(self, array):
        """Set the desired header alignment

        - the elements of the array should be either "l", "c" or "r":

            * "l": column flushed left
            * "c": column centered
            * "r": column flushed right
        """

        self._check_row_size(array)
        self._header_align = array
        return self

    def set_cols_align(self, array):
        """Set the desired columns alignment

        - the elements of the array should be either "l", "c" or "r":

            * "l": column flushed left
            * "c": column centered
            * "r": column flushed right
        """

        self._check_row_size(array)
        self._align = array
        return self

    def set_cols_valign(self, array):
        """Set the desired columns vertical alignment

        - the elements of the array should be either "t", "m" or "b":

            * "t": column aligned on the top of the cell
            * "m": column aligned on the middle of the cell
            * "b": column aligned on the bottom of the cell
        """

        self._check_row_size(array)
        self._valign = array
        return self

    def set_cols_dtype(self, array):
        """Set the desired columns datatype for the cols.

        - the elements of the array should be either a callable or any of
          "a", "t", "f", "e" or "i":

            * "a": automatic (try to use the most appropriate datatype)
            * "t": treat as text
            * "f": treat as float in decimal format
            * "e": treat as float in exponential format
            * "i": treat as int
            * a callable: should return formatted string for any value given

        - by default, automatic datatyping is used for each column
        """

        self._check_row_size(array)
        self._dtype = array
        return self

    def set_cols_width(self, array):
        """Set the desired columns width

        - the elements of the array should be integers, specifying the
          width of each column. For example:

                [10, 20, 5]
        """

        self._check_row_size(array)
        try:
            array = list(map(int, array))
            if reduce(min, array) <= 0:
                raise ValueError
        except ValueError:
            sys.stderr.write("Wrong argument in column width specification\n")
            raise
        self._width = array
        return self

    def set_precision(self, width):
        """Set the desired precision for float/exponential formats

        - width must be an integer >= 0

        - default value is set to 3
        """

        if not type(width) is int or width < 0:
            raise ValueError('width must be an integer greater then 0')
        self._precision = width
        return self

    def set_padding(self, amount):
        """Set the amount of spaces to pad cells (right and left, we don't do top bottom padding)

        - width must be an integer >= 0

        - default value is set to 1
        """
        if not type(amount) is int or amount < 0:
            raise ValueError('padding must be an integer greater then 0')
        self._pad = amount
        return self

    def header(self, array):
        """Specify the header of the table
        """

        self._check_row_size(array)
        self._header = list(map(obj2unicode, array))
        return self

    def add_row(self, array):
        """Add a row in the rows stack

        - cells can contain newlines and tabs
        """

        self._check_row_size(array)

        if not hasattr(self, "_dtype"):
            self._dtype = ["a"] * self._row_size

        cells = []
        for i, x in enumerate(array):
            cells.append(self._str(i, x))
        self._rows.append(cells)
        return self

    def add_rows(self, rows, header=True):
        """Add several rows in the rows stack

        - The 'rows' argument can be either an iterator returning arrays,
          or a by-dimensional array
        - 'header' specifies if the first row should be used as the header
          of the table
        """

        # nb: don't use 'iter' on by-dimensional arrays, to get a
        #     usable code for python 2.1
        if header:
            if hasattr(rows, '__iter__') and hasattr(rows, 'next'):
                self.header(rows.next())
            else:
                self.header(rows[0])
                rows = rows[1:]
        for row in rows:
            self.add_row(row)
        return self

    def draw(self):
        """Draw the table

        - the table is returned as a whole string
        """

        if not self._header and not self._rows:
            return
        self._compute_cols_width()
        self._check_align()
        out = ""
        if self.has_border:
            out += self._hline(location=UniTable.TOP)
        if self._header:
            out += self._draw_line(self._header, isheader=True)
            if self.has_header:
                out += self._hline_header(location=UniTable.MIDDLE)
                pass
            pass
        num = 0
        length = len(self._rows)
        for row in self._rows:
            num += 1
            out += self._draw_line(row)
            if self.has_hlines() and num < length:
                out += self._hline(location=UniTable.MIDDLE)
        if self._has_border:
            out += self._hline(location=UniTable.BOTTOM)
        return out[:-1]

    @classmethod
    def _to_float(cls, x):
        if x is None:
            raise FallbackToText()
        try:
            return float(x)
        except (TypeError, ValueError):
            raise FallbackToText()

    @classmethod
    def _fmt_int(cls, x, **kw):
        """Integer formatting class-method.

        - x will be float-converted and then used.
        """
        return str(int(round(cls._to_float(x))))

    @classmethod
    def _fmt_float(cls, x, **kw):
        """Float formatting class-method.

        - x parameter is ignored. Instead kw-argument f being x float-converted
          will be used.

        - precision will be taken from `n` kw-argument.
        """
        n = kw.get('n')
        return '%.*f' % (n, cls._to_float(x))

    @classmethod
    def _fmt_exp(cls, x, **kw):
        """Exponential formatting class-method.

        - x parameter is ignored. Instead kw-argument f being x float-converted
          will be used.

        - precision will be taken from `n` kw-argument.
        """
        n = kw.get('n')
        return '%.*e' % (n, cls._to_float(x))

    @classmethod
    def _fmt_text(cls, x, **kw):
        """String formatting class-method."""
        return obj2unicode(x)

    @classmethod
    def _fmt_auto(cls, x, **kw):
        """auto formatting class-method."""
        f = cls._to_float(x)
        if abs(f) > 1e8:
            fn = cls._fmt_exp
        elif f != f:  # NaN
            fn = cls._fmt_text
        elif f - round(f) == 0:
            fn = cls._fmt_int
        else:
            fn = cls._fmt_float
        return fn(x, **kw)

    def _str(self, i, x):
        """Handles string formatting of cell data

            i - index of the cell datatype in self._dtype
            x - cell data to format
        """
        FMT = {
            'a':self._fmt_auto,
            'i':self._fmt_int,
            'f':self._fmt_float,
            'e':self._fmt_exp,
            't':self._fmt_text,
            }

        n = self._precision
        dtype = self._dtype[i]
        try:
            if callable(dtype):
                return dtype(x)
            else:
                return FMT[dtype](x, n=n)
        except FallbackToText:
            return self._fmt_text(x)

    def _check_row_size(self, array):
        """Check that the specified array fits the previous rows size
        """

        if not self._row_size:
            self._row_size = len(array)
        elif self._row_size != len(array):
            raise ArraySizeError("array should contain %d elements not %s (array=%s)" \
                %(self._row_size,len(array),array))

    def has_vlines(self):
        """Return a boolean, if vlines are required or not
        """

        return self._deco & UniTable.VLINES > 0

    def has_hlines(self):
        """Return a boolean, if hlines are required or not
        """

        return self._deco & UniTable.HLINES > 0

    def _hline_header(self,location=MIDDLE):
        """Print header's horizontal line
        """

        return self._build_hline(is_header=True,location=location)

    def _hline(self,location):
        """Print an horizontal line
        """
        # if not self._hline_string:
        #   self._hline_string = self._build_hline(location)
        # return self._hline_string
        return self._build_hline(is_header=False,location=location)

    def _build_hline(self, is_header=False, location=MIDDLE):
        """Return a string used to separated rows or separate header from
        rows
        """
        horiz_char = self._char_hew if is_header else self._char_ew
        if UniTable.TOP == location:
            left, mid, right = self._char_se, self._char_sew, self._char_sw
        elif UniTable.MIDDLE == location:
            if is_header:
                left, mid, right = self._char_hnse, self._char_hnsew, self._char_hnsw
            else:
                left, mid, right = self._char_nse, self._char_nsew, self._char_nsw
                pass
        elif UniTable.BOTTOM == location:
            # NOTE: This will not work as expected if the table is only headers.
            left, mid, right = self._char_ne, self._char_new, self._char_nw
        else:
            raise ValueError("Unknown location '%s'. Should be one of UniTable.TOP, UniTable.MIDDLE, or UniTable.BOTTOM." %(location))
        # compute cell separator
        s = "%s%s%s" % (horiz_char * self._pad, [horiz_char, mid][self.has_vlines()], horiz_char * self._pad)
        # build the line
        l = s.join([horiz_char * n for n in self._width])
        # add border if needed
        if self.has_border:
            l = "%s%s%s%s%s\n" % (left, horiz_char * self._pad , l, horiz_char * self._pad ,right)
        else:
            l += "\n"
        return l

    def _len_cell(self, cell):
        """Return the width of the cell

        Special characters are taken into account to return the width of the
        cell, such like newlines and tabs
        """

        cell_lines = cell.split('\n')
        maxi = 0
        for line in cell_lines:
            length = 0
            parts = line.split('\t')
            for part, i in zip(parts, list(range(1, len(parts) + 1))):
                length = length + len(part)
                if i < len(parts):
                    length = (length//8 + 1) * 8
            maxi = max(maxi, length)
        return maxi

    def _compute_cols_width(self):
        """Return an array with the width of each column

        If a specific width has been specified, exit. If the total of the
        columns width exceed the table desired width, another width will be
        computed to fit, and cells will be wrapped.
        """

        if hasattr(self, "_width"):
            return
        maxi = []
        if self._header:
            maxi = [ self._len_cell(x) for x in self._header ]
        for row in self._rows:
            for cell,i in zip(row, list(range(len(row)))):
                try:
                    maxi[i] = max(maxi[i], self._len_cell(cell))
                except (TypeError, IndexError):
                    maxi.append(self._len_cell(cell))

        ncols = len(maxi)
        content_width = sum(maxi)
        deco_width = 3*(ncols-1) + [0,4][self.has_border]
        if self._max_width and (content_width + deco_width) > self._max_width:
            """ content too wide to fit the expected max_width
            let's recompute maximum cell width for each cell
            """
            if self._max_width < (ncols + deco_width):
                raise ValueError('max_width too low to render data')
            available_width = self._max_width - deco_width
            newmaxi = [0] * ncols
            i = 0
            while available_width > 0:
                if newmaxi[i] < maxi[i]:
                    newmaxi[i] += 1
                    available_width -= 1
                i = (i + 1) % ncols
            maxi = newmaxi
        self._width = maxi

    def _check_align(self):
        """Check if alignment has been specified, set default one if not
        """

        if not hasattr(self, "_header_align"):
            self._header_align = ["c"] * self._row_size
        if not hasattr(self, "_align"):
            self._align = ["l"] * self._row_size
        if not hasattr(self, "_valign"):
            self._valign = ["t"] * self._row_size

    def _draw_line(self, line, isheader=False):
        """Draw a line

        Loop over a single cell length, over all the cells
        """

        line = self._splitit(line, isheader)
        space = " "
        out = ""
        topmost,leftmost = True, True
        for i in range(len(line[0])):
            if self.has_border:
                out += "%s%s" %(self._char_ns, " " * self._pad)
            length = 0
            for cell, width, align in zip(line, self._width, self._align):
                length += 1
                cell_line = cell[i]
                fill = width - len(cell_line)
                if isheader:
                    align = self._header_align[length - 1]
                if align == "r":
                    out += fill * space + cell_line
                elif align == "c":
                    out += (int(fill/2) * space + cell_line \
                            + int(fill/2 + fill%2) * space)
                else:
                    out += cell_line + fill * space
                if length < len(line):
                    out += "%s%s%s" %(" " * self._pad, [space, self._char_ns][self.has_vlines()], " " * self._pad)
            out += "%s\n" % ['', " " * self._pad + self._char_ns][self.has_border]
        return out

    def _splitit(self, line, isheader):
        """Split each element of line to fit the column width

        Each element is turned into a list, result of the wrapping of the
        string to the desired width
        """

        line_wrapped = []
        for cell, width in zip(line, self._width):
            array = []
            for c in cell.split('\n'):
                if c.strip() == "":
                    array.append("")
                else:
                    array.extend(textwrapper(c, width))
            line_wrapped.append(array)
        max_cell_lines = reduce(max, list(map(len, line_wrapped)))
        for cell, valign in zip(line_wrapped, self._valign):
            if isheader:
                valign = "t"
            if valign == "m":
                missing = max_cell_lines - len(cell)
                cell[:0] = [""] * int(missing / 2)
                cell.extend([""] * int(missing / 2 + missing % 2))
            elif valign == "b":
                cell[:0] = [""] * (max_cell_lines - len(cell))
            else:
                cell.extend([""] * (max_cell_lines - len(cell)))
        return line_wrapped



def test_styles(table):
    row = []
    for style in styles:
        table.set_style(style)
        row.append(t2.draw())
        pass
    return row

if __name__ == '__main__':
    table = UniTable()
    table.set_cols_align(["l", "r", "c"])
    table.set_cols_valign(["t", "m", "b"])
    table.add_rows([["Name", "Age", "Nickname"],
                    ["Mr\nXavier\nHuon", 32, "Xav'"],
                    ["Mr\nBaptiste\nClement", 1, "Baby"],
                    ["Mme\nLouise\nBourgeau", 28, "Lou\n \nLoue"]])
    print(table.draw() + "\n")

    table = UniTable()
    table.set_deco(UniTable.HEADER)
    table.set_cols_dtype(['t',  # text
                          'f',  # float (decimal)
                          'e',  # float (exponent)
                          'i',  # integer
                          'a']) # automatic
    table.set_cols_align(["l", "r", "r", "r", "l"])
    table.add_rows([["text",    "float", "exp", "int", "auto"],
                    ["abcd",    "67",    654,   89,    128.001],
                    ["efghijk", 67.5434, .654,  89.6,  12800000000000000000000.00023],
                    ["lmn",     5e-78,   5e-78, 89.4,  .000000000000128],
                    ["opqrstu", .023,    5e+78, 92.,   12800000000000000000000]])
    print(table.draw())

    # Create a table of tables that shows different table styles
    styles = sorted(UniTable.STYLES.keys())
    t1 = UniTable([["STYLES"] + styles])
    t1.set_max_width(0)
    t1.set_cols_align("l" + "c" * len(styles))
    t1.set_cols_valign("m" + "t" * len(styles))
    t1.set_style("light")
    style_rows =[["Header 1","Header 2"],["Cell 1","Cell 2"],["Cell 3","Cell 4"],]
    t2 = UniTable(style_rows)
    for style in styles:
        print("Style \"%s\"" %(style))
        t2.set_style(style)
        print(t2.draw())
        pass
    exit()
    t1.add_row(["DEFAULT"] + test_styles(t2))
    t2.set_padding(0)
    t1.add_row(["set_padding(0)"] + test_styles(t2))
    t2.set_padding(2)
    t1.add_row(["set_padding(2)"] + test_styles(t2))
    t2.set_deco(UniTable.HEADER)
    t2.set_padding(1)
    t1.add_row(["set_deco(HEADER)"] + test_styles(t2))
    print(t1.draw() + "\n")
