import mistune
from .renderers import GeminiRenderer, NEWLINE
import argparse
import sys
import os

def md2gemini(markdown, img_tag="[IMG]", indent="  ", ascii_table=False, jekyll=False):
    """Convert the provided markdown text to the gemini format.
    
    img_tag: The text added after an image link, to indicate it's an image.
    
    indent: How much to indent sub-levels of a list. Put several spaces, or \\t for a tab.
    
    ascii_table: Use ASCII to create tables, not Unicode.

    jekyll: Skip jekyll frontmatter when processing.
    """

    # Pre processing
    # Remove jekyll frontmatter
    frontmatter = False
    if jekyll:
        lines = markdown.strip().splitlines()
        if lines[0] == "---":
            frontmatter = True
    
    if frontmatter:
        md_lines = []
        for i, line in enumerate(lines[1:]):  # Skip first front matter line
            if line == "---":
                # End of frontmatter, add all the lines below it
                md_lines.extend(lines[i+2:])
                break
        # Turn it back into text
        if md_lines != []:
            markdown = "\n".join(md_lines)
    
    # Conversion
    renderer = GeminiRenderer(img_tag=img_tag, indent=indent, ascii_table=ascii_table)
    gem = mistune.create_markdown(escape=False, renderer=renderer, plugins=["table"])
    gemtext = gem(markdown)
    
    # Post processing
    gemlines = gemtext.splitlines()[:-1]
    pre = False  # Whether we're in a preformatted area or not
    for i, line in enumerate(gemlines):
        # Maintain preformatted state
        if line.startswith("```"):
            pre = not pre
            continue
        if line.startswith("=>") and not pre:
            # It's a link, fix the next line by removing left whitespace
            gemlines[i+1] = gemlines[i+1].lstrip()

    gemtext = NEWLINE.join(gemlines)
    return gemtext

# Main functions, for running as a script

args = None

def __convert_file(file):
    if file == sys.stdin:
        gem = md2gemini(file.read(), img_tag=args.img_tag, indent=args.indent, ascii_table=args.ascii_table, jekyll=args.jekyll)
        print(gem)
    else:
        with open(file, "r") as f:
            gem = md2gemini(f.read(), img_tag=args.img_tag, indent=args.indent, ascii_table=args.ascii_table, jekyll=args.jekyll)
        if args.write:
            newfile = os.path.splitext(os.path.basename(file))[0] + ".gmi"
            with open(os.path.join(args.dir, newfile), "w") as f:
                f.write(gem)
        else:
            print(gem)

def main():
    global args

    parser = argparse.ArgumentParser(description="Convert markdown to gemini.", prog="md2gemini")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("file", nargs="*", help="Files to convert. If no files are specified then data will be read from stdin and printed to stdout.")
    parser.add_argument("-w", "--write", action="store_true", help="Write output to a new file of the same name, but with a .gmi extension.")
    parser.add_argument("-d", "--dir", help="The directory to write files to, if --write is used.")
    parser.add_argument("-a", "--ascii-table", action="store_true", help="Use ASCII to create tables, not Unicode.")
    parser.add_argument("-j", "--jekyll", action="store_true", help="Remove jekyll frontmatter from parsing and output.")
    parser.add_argument("--img-tag", type=str, help="What text to add after image links. Defaults to '[IMG]'.\nWrite something like --img-tag='' to remove it.")
    parser.add_argument("-i", "--indent", type=str, help="The number of spaces to use for list indenting. Put 'tab' to use a tab instead.")
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
            print("Invalid indent value. Must be an integer, or 'tab'.", file=sys.stderr)
            sys.exit(1)

    # If there aren't any files then read from stdin
    if args.file == []:
        __convert_file(sys.stdin)
        sys.exit(0)

    # Process each file sequentially
    for file in args.file:
        if not os.path.isfile(file):
            print("File", file, "cannot be found.", file=sys.stderr)
            sys.exit(1)
        __convert_file(file)


__all__ = ["GeminiRenderer", "md2gemini", "main"]
__version__ = "1.0.1"
