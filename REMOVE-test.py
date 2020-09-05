from md2gemini import md2gemini

with open("REMOVE-test.md", "r") as f:
    md = f.read()

out = md2gemini(md, frontmatter=True, links="copy")
print(out)
