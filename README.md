# md2gemini

Converter from Markdown to the [Gemini](https://gemini.circumlunar.space/) text format. It works as a Python module, or a command line application.

Beyond regular Markdown, it supports tables! And converts them into Unicode plaintext tables like this:
```
┌──────────────┬──────┐
│     foo      │ bar  │
╞══════════════╪══════╡
│          baz │ bim  │
├──────────────┼──────┤
│ testdfsdfsdf │ yeah │
└──────────────┴──────┘
```
or like this for ASCII:
```
+--------------+------+
|     foo      | bar  |
+==============+======+
|          baz | bim  |
+--------------+------+
| testdfsdfsdf | yeah |
+--------------+------+
```
This means all your GFM tables will still work and look nice.

Anything else that it doesn't understand will remain the same as when you wrote it, like strikethrough for example.

## Installation
```
pip3 install md2gemini
```
You may also want to use the `--user` flag after install, to only install the package for your user.

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
                        the asterisks for bold and italics.
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
def md2gemini(markdown, img_tag="[IMG]", indent="  ", ascii_table=False, jekyll=False):
    """Convert the provided markdown text to the gemini format.
    
    img_tag: The text added after an image link, to indicate it's an image.
    
    indent: How much to indent sub-levels of a list. Put several spaces, or \\t for a tab.
    
    ascii_table: Use ASCII to create tables, not Unicode.

    jekyll: Skip jekyll frontmatter when processing.
    """
```
