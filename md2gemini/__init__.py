import mistune
from .renderers import GeminiRenderer, NEWLINE

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

__all__ = ["GeminiRenderer", "md2gemini"]
__version__ = "1.0.0"  # TODO: Change version
