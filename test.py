from md2gemini import md2gemini

with open("test.md", "r") as f:
    md = f.read()

out = md2gemini(md, frontmatter=True, links="paragraph", md_links=True)
print(out)
