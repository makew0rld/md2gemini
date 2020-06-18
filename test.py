from md2gemini import md2gemini

with open("test.md", "r") as f:
    md = f.read()

out = md2gemini(md, frontmatter=True, links="paragraph", base_url="https://test.com")
print(out)
