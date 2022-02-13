# md2gemini

[![PyPI downloads](https://img.shields.io/pypi/dm/md2gemini)](https://pypi.org/project/md2gemini)
[![License image](https://img.shields.io/github/license/makeworld-the-better-one/md2gemini)](https://www.gnu.org/licenses/lgpl-3.0.en.html)

Converter from Markdown to the [Gemini](https://gemini.circumlunar.space/) text format. It works as a Python module, or a command line application.

One of its key features is that it can convert inline links into footnotes. It also supports tables, and will convert them into Unicode (or ASCII) tables.

Anything else that it doesn't understand will remain the same as when you wrote it, like strikethrough for example.

## Link modes

md2gemini has several link modes, because text/gemini doesn't support inline links. These modes can be set by passing different strings to the `-l` or `--links` flags on the command line, or the `links=` argument in Python.

Here is some example markdown, to show what each link mode does:
```markdown
This is a paragraph with an [inline](https://example.com) link.
Here is [another](https://example.org/) link, part of the same paragraph.

This is a second paragraph, with a different [link](https://duck.com) in it.
```

Link modes:

### default
This is what happens when don't specify what link mode you want, or put any invalid string. It is also called "newline" mode. It is likely the worst link mode for reading.

Output:
```
This is a paragraph with an
=> https://example.com inline
link.
Here is
=> https://example.org/ another
link, part of the same paragraph.

This is a second paragraph, with a different
=> https://duck.com link
in it.
```

### off
This will remove all links.

Output:
```
This is a paragraph with an inline link. Here is another link, part of the same paragraph.

This is a second paragraph, with a different link in it.
```

### paragraph
This will result in footnotes being added to the document, and the links for each footnote being added at the end of each paragraph.

Output:
```
This is a paragraph with an inline[1] link. Here is another[2] link, part of the same paragraph.

=> https://example.com 1: https://example.com
=> https://example.org/ 2: https://example.org/

This is a second paragraph, with a different link[3] in it.

=> https://duck.com 3: https://duck.com
```

### at-end
This is the same as **paragraph**, but all the links for the footnotes are added at the very end of the document.

Output:
```
This is a paragraph with an inline[1] link. Here is another[2] link, part of the same paragraph.

This is a second paragraph, with a different link[3] in it.

=> https://example.com 1: https://example.com
=> https://example.org/ 2: https://example.org/
=> https://duck.com 3: https://duck.com
```

### copy
This link mode doesn't add any footnotes inside the paragraph, but creates a link with the inline link text at the end of the paragraph. [Here's](https://user-images.githubusercontent.com/25111343/85186965-0b0e8580-b26a-11ea-8cb7-aa22ca6745af.png) a screenshot showing what this mode ends up looking like - using my [Amfora](https://github.com/makeworld-the-better-one/amfora) browser.

Output:
```
This is a paragraph with an inline link. Here is another link, part of the same paragraph.

=> https://example.com inline
=> https://example.org/ another

This is a second paragraph, with a different link in it.

=> https://duck.com link
```

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
usage: md2gemini [-h] [--version] [-w] [-d DIR] [-a] [-f] [-j]
                 [--code-tag CODE_TAG] [--img-tag IMG_TAG]
                 [--table-tag TABLE_TAG] [-i INDENT] [-l LINKS] [-p] [-s]
                 [-b BASE_URL] [-m]
                 [file [file ...]]

Convert markdown to gemini.

positional arguments:
  file                  Files to convert. If no files are specified then data
                        will be read from stdin and printed to stdout.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -w, --write           Write output to a new file of the same name, but with
                        a .gmi extension.
  -d DIR, --dir DIR     The directory to write files to, if --write is used.
  -a, --ascii-table     Use ASCII to create tables, not Unicode.
  -f, --frontmatter     Remove Jekyll and Zola style front matter before
                        converting.
  -j, --jekyll          Skip jekyll frontmatter when processing - DEPRECATED.
  --code-tag CODE_TAG   What alt text to add to unlabeled code blocks.
                        Defaults to empty string.
  --img-tag IMG_TAG     What text to add after image links. Defaults to
                        '[IMG]'. Write something like --img-tag='' to remove
                        it.
  --table-tag TABLE_TAG
                        What alt text to add to table blocks. Defaults to
                        'table'. Write something like --table-tag='' to remove
                        it.
  -i INDENT, --indent INDENT
                        The number of spaces to use for list indenting. Put
                        'tab' to use a tab instead.
  -l LINKS, --links LINKS
                        Set to 'off' to turn off links, 'paragraph' to have
                        footnotes at the end of each paragraph, or 'at-end' to
                        have footnotes at the end of the document. You can
                        also set it to 'copy' to put links that copy the
                        inline link text after each paragraph. Not using this
                        flag, or having any other value will result in
                        regular, newline links.
  -p, --plain           Remove special markings from output that text/gemini
                        doesn't support, like the asterisks for bold and
                        italics, and inline HTML
  -s, --strip-html      Strip all inline and block HTML from Markdown. Note
                        that using --plain will strip inline HTML as well.
  -b BASE_URL, --base-url BASE_URL
                        All links starting with a slash will have this URL
                        prepended to them.
  -m, --md-links        Convert all links to local files ending in .md to end
                        with .gmi instead.
  -c, --no-checklist    Disable rendering of GitHub-style checklist list
                        items: [ ] and [x]

```

### In Python
```python
from md2gemini import md2gemini
# Load a markdown file's contents into memory and get conversion
with open("example.md", "r") as f:
    gemini = md2gemini(f.read())
# Now the gemini variable contains your converted text as a string
```
Options for the `md2gemini` function are similar to the command line ones above, except for the parameter `link_func` which cannot be used from the command line.
```python
def md2gemini(markdown, code_tag="", img_tag="[IMG]", indent=" ",
              ascii_table=False, frontmatter=False, jekyll=False,
              links="newline", plain=False, strip_html=False,
              base_url="", md_links=False, link_func=None,
              table_tag="table", checklist=True):
    """Convert the provided markdown text to the gemini format.
    code_tag: The default alt text for code blocks.

    img_tag: The text added after an image link, to indicate it's an image.
    
    indent: How much to indent sub-levels of a list. Put several spaces, or \\t for a tab.
    
    ascii_table: Use ASCII to create tables, not Unicode.

    frontmatter: Remove Jekyll and Zola style front matter before converting.

    jekyll: Skip jekyll frontmatter when processing - DEPRECATED.

    links: Set to 'off' to turn off links, 'paragraph' to have footnotes at the end of each
    paragraph, or 'at-end' to have footnotes at the end of the document. You can also set it
    to 'copy' to put links that copy the inline link text after each paragraph. Not using this
    flag, or having any other value will result in regular, newline links.

    plain: Set to True to remove special markings from output that text/gemini doesn't support,
    like the asterisks for bold and italics, as well as inline HTML.

    strip_html: Strip all inline and block HTML from Markdown.

    base_url: All links starting with a slash will have this URL prepended to them.

    md_links: Convert all links to local files ending in .md to end with .gmi instead.

    link_func: Custom function to apply to links. This function takes a string containing the link
    URL as parameter, and should return the new link.

    table_tag: "The default alt text for table blocks."

    checklist: whether to support GitHub-style checklist list items: [ ] and [x]
    """
```
