import mistune
from .renderers import GeminiRenderer, NEWLINE, PARAGRAPH_DELIM, LINK_DELIM, LINEBREAK
import argparse
import sys
import os
import re


def __text_between(text, delim, n=0):
    """Get the text between two delimeters.

    n: Which occurence of the delimeter pair to act on, zero-indexed.
    """

    return text.split(delim)[n + 1]


def __replace_between(text, delim, new_text, n=0):
    """Replace the text between two delimeters, and get the full text back.

    n: Which occurence of the delimeter pair to act on, zero-indexed.
    """

    start = delim.join(text.split(delim)[: n + 1])
    end = delim.join(text.split(delim)[n + 2 :])
    # return start + delim + new_text + delim + end
    return start + new_text + end


def md2gemini(
    markdown,
    code_tag="",
    img_tag="[IMG]",
    indent=" ",
    ascii_table=False,
    frontmatter=False,
    jekyll=False,
    links="newline",
    plain=False,
    strip_html=False,
    base_url="",
    md_links=False,
    link_func=None,
    table_tag="table",
    checklist=True,
):
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

    if len(markdown) == 0:
        return ""

    # Pre processing
    # Remove frontmatter
    frontmatterExists = False
    if frontmatter:
        lines = markdown.strip().splitlines()
        if lines[0] == "---" or lines[0] == "+++":
            frontmatterExists = True
    elif jekyll:
        lines = markdown.strip().splitlines()
        if lines[0] == "---":
            frontmatterExists = True

    if frontmatterExists:
        md_lines = []
        for i, line in enumerate(lines[1:]):  # Skip first front matter line
            if ((frontmatter or jekyll) and line == "---") or (
                frontmatter and line == "+++"
            ):
                # End of frontmatter, add all the lines below it
                md_lines.extend(lines[i + 2 :])
                break
        # Turn it back into text
        if md_lines != []:
            # If md_lines was empty, then effectively no removal would occur, and frontmatter would be processed
            markdown = NEWLINE.join(md_lines)

    # Conversion
    renderer = GeminiRenderer(
        code_tag=code_tag,
        img_tag=img_tag,
        indent=indent,
        ascii_table=ascii_table,
        links=links,
        plain=plain,
        strip_html=strip_html,
        base_url=base_url,
        md_links=md_links,
        link_func=link_func,
        table_tag=table_tag,
        checklist=checklist,
    )
    gem = mistune.create_markdown(
        escape=False, renderer=renderer, plugins=["table", "url", "task_lists"]
    )
    gemtext = gem(markdown)

    # Post processing

    # Remove newlines within paragraphs, and add two newlines after them.
    while PARAGRAPH_DELIM in gemtext:  # While there's still unprocessed paragraphs
        pg = __text_between(gemtext, PARAGRAPH_DELIM).strip()
        pg = pg.replace("\r\n", "\n")  # Make all newlines the same
        pg = pg.replace(
            "\n", " "
        )  # Get rid of newlines in the same paragraph, like markdown does
        pg += NEWLINE * 2  # Add a blank line between paragraphs
        gemtext = __replace_between(gemtext, PARAGRAPH_DELIM, pg)

    # Add in hard linebreaks
    gemtext = gemtext.replace(LINEBREAK, NEWLINE)

    # Add remaining footnotes at and of file
    gemtext += NEWLINE + renderer._render_footnotes() + NEWLINE

    # Remove double link delims, which are produced by multiple footnotes
    gemtext = gemtext.replace(LINK_DELIM + LINK_DELIM, LINK_DELIM)
    # Remove all the link delims that are next to newlines,
    # so that when link delims are replaced with newlines later in the code,
    # we don't end up with double newlines.
    gemtext = re.sub(
        r"((?<=\r\n)|(?<=\n)" + LINK_DELIM + r")|(" + LINK_DELIM + r"(?=\r\n|\n))",
        "",
        gemtext,
    )
    gemtext = gemtext.replace(LINK_DELIM, NEWLINE)

    # Remove left whitespace in the lines after links
    gemlines = gemtext.splitlines()
    if gemlines[-1] == "":
        gemlines = gemlines[:-1]
    pre = False  # Whether we're in a preformatted area or not
    length = len(gemlines)
    for i, line in enumerate(gemlines):
        # Maintain preformatted state
        if line.startswith("```"):
            pre = not pre
            continue
        if i + 1 < length - 1 and line.startswith("=>") and not pre:
            # It's a link, fix the next line by removing left whitespace
            gemlines[i + 1] = gemlines[i + 1].lstrip()
    gemtext = NEWLINE.join(gemlines)
    gemtext = gemtext.rstrip().lstrip("\r\n")

    # Remove more than two newlines in a row, as there's no way to induce that in valid markdown
    # So any time there's more than two newlines in output that's a bug with md2gemini
    # So it gets fixed here. Hacky, but it works.
    gemtext = re.sub(
        r"(?:" + NEWLINE + r"){3}(?:" + NEWLINE + r")*", NEWLINE * 2, gemtext
    )

    return gemtext


# Main functions, for running as a script


def __convert_file(file, args):
    if file == sys.stdin:
        gem = md2gemini(
            file.read(),
            code_tag=args.code_tag,
            img_tag=args.img_tag,
            indent=args.indent,
            ascii_table=args.ascii_table,
            frontmatter=args.frontmatter,
            jekyll=args.jekyll,
            links=args.links,
            plain=args.plain,
            strip_html=args.strip_html,
            base_url=args.base_url,
            md_links=args.md_links,
            link_func=None,
            table_tag=args.table_tag,
            checklist=not args.no_checklist,
        )
        print(gem)
    else:
        with open(file, "r") as f:
            gem = md2gemini(
                f.read(),
                code_tag=args.code_tag,
                img_tag=args.img_tag,
                indent=args.indent,
                ascii_table=args.ascii_table,
                frontmatter=args.frontmatter,
                jekyll=args.jekyll,
                links=args.links,
                plain=args.plain,
                strip_html=args.strip_html,
                base_url=args.base_url,
                md_links=args.md_links,
                link_func=None,
                table_tag=args.table_tag,
                checklist=not args.no_checklist,
            )
        if args.write:
            newfile = os.path.splitext(os.path.basename(file))[0] + ".gmi"
            with open(os.path.join(args.dir, newfile), "w") as f:
                f.write(gem)
        else:
            print(gem)


def main():
    parser = argparse.ArgumentParser(
        description="Convert markdown to gemini.", prog="md2gemini"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "file",
        nargs="*",
        help="Files to convert. If no files are specified then data will be read from stdin and printed to stdout.",
    )
    parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="Write output to a new file of the same name, but with a .gmi extension.",
    )
    parser.add_argument(
        "-d", "--dir", help="The directory to write files to, if --write is used."
    )
    parser.add_argument(
        "-a",
        "--ascii-table",
        action="store_true",
        help="Use ASCII to create tables, not Unicode.",
    )
    parser.add_argument(
        "-f",
        "--frontmatter",
        action="store_true",
        help="Remove Jekyll and Zola style front matter before converting.",
    )
    parser.add_argument(
        "-j",
        "--jekyll",
        action="store_true",
        help="Skip jekyll frontmatter when processing - DEPRECATED.",
    )
    parser.add_argument(
        "--code-tag",
        type=str,
        help="What alt text to add to unlabeled code blocks. Defaults to empty string.",
    )
    parser.add_argument(
        "--img-tag",
        type=str,
        help="What text to add after image links. Defaults to '[IMG]'.\nWrite something like --img-tag='' to remove it.",
    )
    parser.add_argument(
        "--table-tag",
        type=str,
        help="What alt text to add to table blocks. Defaults to 'table'.\nWrite something like --table-tag='' to remove it.",
    )
    parser.add_argument(
        "-i",
        "--indent",
        type=str,
        help="The number of spaces to use for list indenting. Put 'tab' to use a tab instead.",
    )
    parser.add_argument(
        "-l",
        "--links",
        type=str,
        help="Set to 'off' to turn off links, 'paragraph' to have footnotes at the end of each paragraph, or 'at-end' to have footnotes at the end of the document. You can also set it to 'copy' to put links that copy the inline link text after each paragraph. Not using this flag, or having any other value will result in regular, newline links.",
    )
    parser.add_argument(
        "-p",
        "--plain",
        action="store_true",
        help="Remove special markings from output that text/gemini doesn't support, like the asterisks for bold and italics, and inline HTML",
    )
    parser.add_argument(
        "-s",
        "--strip-html",
        action="store_true",
        help="Strip all inline and block HTML from Markdown. Note that using --plain will strip inline HTML as well.",
    )
    parser.add_argument(
        "-b",
        "--base-url",
        type=str,
        help="All links starting with a slash will have this URL prepended to them.",
    )
    parser.add_argument(
        "-m",
        "--md-links",
        action="store_true",
        help="Convert all links to local files ending in .md to end with .gmi instead.",
    )
    parser.add_argument(
        "-c",
        "--no-checklist",
        action="store_true",
        help="Disable rendering of GitHub-style checklist list items: [ ] and [x]",
    )
    args = parser.parse_args()

    # Validation of command line args
    if args.write and args.dir is None:
        args.dir = "."
    if args.write and not os.path.isdir(args.dir):
        print("Directory", args.dir, "cannot be found.", file=sys.stderr)
        sys.exit(1)
    if args.indent == "tab":
        args.indent = "\t"
    elif not args.indent is None:
        try:
            args.indent = " " * int(args.indent)
        except ValueError:
            print(
                "Invalid indent value. Must be an integer, or 'tab'.", file=sys.stderr
            )
            sys.exit(1)
    if args.code_tag is None:
        args.code_tag = ""

    if args.img_tag is None:
        args.img_tag = "[IMG]"

    if args.table_tag is None:
        args.table_tag = "table"

    # If there aren't any files then read from stdin
    if args.file == []:
        __convert_file(sys.stdin, args)
        sys.exit(0)

    # Process each file sequentially
    for file in args.file:
        if not os.path.isfile(file):
            print("File", file, "cannot be found.", file=sys.stderr)
            sys.exit(1)
        __convert_file(file, args)


__all__ = ["GeminiRenderer", "md2gemini", "main", "NEWLINE", "__version__"]
__version__ = "1.9.0"
