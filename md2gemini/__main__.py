#!/usr/bin/env python3

# This file is run when md2gemini is called as a command.

from md2gemini import md2gemini, __version__
import argparse
import sys
import os

def convert_file(file):
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
    convert_file(sys.stdin)
    sys.exit(0)

# Process each file sequentially
for file in args.file:
    if not os.path.isfile(file):
        print("File", file, "cannot be found.", file=sys.stderr)
        sys.exit(1)
    convert_file(file)
