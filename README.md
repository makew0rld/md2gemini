# md2gemini

[![PyPI downloads](https://img.shields.io/pypi/dw/md2gemini)](https://pypi.org/project/md2gemini)
[![License image](https://img.shields.io/github/license/makeworld-the-better-one/md2gemini)](https://www.gnu.org/licenses/lgpl-3.0.en.html)

Converter from Markdown to the [Gemini](https://gemini.circumlunar.space/) text format. It works as a Python module, or a command line application.

One of its key features is that it can convert inline links into footnotes - at the end of each paragraph, or all together at the end of the document.

Beyond regular Markdown, it supports tables! And converts them into Unicode plaintext tables like this:
```
┌──────────────┬──────┐
│     foo      │ bar  │
╞══════════════╪══════╡
│          baz │ bim  │
├──────────────┼──────┤
│      Testing │ yeah │
└──────────────┴──────┘
```
or like this for ASCII:
```
+--------------+------+
|     foo      | bar  |
+==============+======+
|          baz | bim  |
+--------------+------+
|      Testing | yeah |
+--------------+------+
```
This means all your GFM tables will still work and look nice.

Anything else that it doesn't understand will remain the same as when you wrote it, like strikethrough for example.

## Installation
```
pip3 install md2gemini
```
You may also want to use the `--user` flag after `install`, to only install the package for your user.

Note that this package only officially supports Python 3.

## Usage

It works directly in Python, or on the command line. The command line version can work with unix pipes as well, reading files from stdin and writing to stdout if desired.

### Command line
```
usage: md2gemini [-h] [--version] [-w] [-d DIR] [-a] [-j] [--img-tag IMG_TAG] [-i INDENT] [-l LINKS] [file [file ...]]

Convert markdown to gemini.

positional arguments:
  file                  Files to convert. If no files are specified then data will be read from
                        stdin and printed to stdout.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -w, --write           Write output to a new file of the same name, but with a .gmi extension.
  -d DIR, --dir DIR     The directory to write files to, if --write is used.
  -a, --ascii-table     Use ASCII to create tables, not Unicode.
  -f, --frontmatter     Remove Jekyll and Zola style front matter before converting.
  -j, --jekyll          Remove jekyll frontmatter from parsing and output.
  --img-tag IMG_TAG     What text to add after image links. Defaults to '[IMG]'. Write something
                        like --img-tag='' to remove it.
  -i INDENT, --indent INDENT
                        The number of spaces to use for list indenting. Put 'tab' to use a
                        tab instead.
  -l LINKS, --links LINKS
                        Set to 'off' to turn off links, 'paragraph' to have footnotes and the real
                        links at the end of each paragraph, or 'at-end' to have footnotes at the
                        end of the document. Not using this flag, or having any other value will
                        result in regular, newline links.
  -p, --plain           Remove special markings from output that text/gemini doesn't support, like
                        the asterisks for bold and italics, and inline HTML
  -s, --strip-html      Strip all inline and block HTML from Markdown. Note that using --plain will
                        strip inline HTML as well.
  -b BASE_URL, --base-url BASE_URL
                        All links starting with a slash will have this URL prepended to them.
  -m, --md-links        Convert all links to local files ending in .md to end with .gmi instead.

```

### In Python
```python
from md2gemini import md2gemini
# Load a markdown file's contents into memory and get conversion
with open("example.md", "r") as f:
    gemini = md2gemini(f.read())
# Now the gemini variable contains your converted text as a string
```
Options for the `md2gemini` function are similar to the command line ones above.
```python
def md2gemini(markdown, img_tag="[IMG]", indent="  ", ascii_table=False, frontmatter=False, jekyll=False, links="newline", plain=False):
    """Convert the provided markdown text to the gemini format.
    
    img_tag: The text added after an image link, to indicate it's an image.
    
    indent: How much to indent sub-levels of a list. Put several spaces, or \\t for a tab.
    
    ascii_table: Use ASCII to create tables, not Unicode.

    frontmatter: Remove Jekyll and Zola style front matter before converting.

    jekyll: Skip jekyll frontmatter when processing - DEPRECATED.

    links: Set to "off" to turn off links, "paragraph" to add footnotes and then have the actual
    links at the end of each paragraph, or "at-end" to put all the footnotes at the end.
    Any other value will result in links on a newline.

    plain: Set to True to remove special markings from output that text/gemini doesn't support,
    like the asterisks for bold and italics, as well as inline HTML.

    strip_html: Strip all inline and block HTML from Markdown.

    base_url: All links starting with a slash will have this URL prepended to them.

    md_links: Convert all links to local files ending in .md to end with .gmi instead.
    """
```
