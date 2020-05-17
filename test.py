from md2gemini import md2gemini, NEWLINE
from hashlib import sha256
import sys

md = """---
these lines should
not appear

---

# Heading 1
## Heading 2
### Heading 3
#### Heading 4 - not supported by gemini

Sometimes you want numbered lists:
1. One
2. Two
3. Three

Sometimes you want bullet points:

* Start a line with a star
* Profit!

Alternatively,

- Dashes work just as well
- And if you have sub points, put two spaces before the dash or star:
  - Like this
  - And this

1. Item 1
   1. Item 1a
1. Item 2
1. Item 3
   1. Item 3a
   1. Item 3b

This is a single line.
This is another line, it SHOULD be joined with the one above.

This line should be separate.

It's very easy to make some words **bold** and other words *italic* with Markdown. You can even do [inline](http://google.com) links!

![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png) with words after
> block quote here
Inline `code is right` here.

Code block:
```
preformatted text should be here
another line of it



there should be three spaces above
```

There should be a long thematic break here

---

Table testing:

| foo | bar |
| ---: | :---: |
| baz | bim |
| testdfsdfsdf | yeah
Line under a table
"""

out = md2gemini(md, jekyll=True)
print(out, end="")

correct = """# Heading 1
## Heading 2
### Heading 3
#### Heading 4 - not supported by gemini
Sometimes you want numbered lists:

1. One
2. Two
3. Three

Sometimes you want bullet points:

* Start a line with a star
* Profit!

Alternatively,

* Dashes work just as well
* And if you have sub points, put two spaces before the dash or star:
  * Like this
  * And this

1. Item 1
  1. Item 1a
3. Item 2
4. Item 3
  1. Item 3a
  2. Item 3b

This is a single line. This is another line, it SHOULD be joined with the one above.

This line should be separate.

It's very easy to make some words bold and other words italic with Markdown. You can even do  
=> http://google.com inline
links!


=> https://octodex.github.com/images/yaktocat.png Image of Yaktocat [IMG]
with words after

> block quote here

Inline `code is right` here.

Code block:

```
preformatted text should be here
another line of it



there should be three spaces above
```
There should be a long thematic break here

--------------------------------------------------------------------------------

Table testing:

```table
┌──────────────┬──────┐
│     foo      │ bar  │
╞══════════════╪══════╡
│          baz │ bim  │
├──────────────┼──────┤
│ testdfsdfsdf │ yeah │
└──────────────┴──────┘
```
Line under a table"""

# Verify the output was what was expected
if out.replace(NEWLINE, "\n") == correct:
    print("\n\nTEST PASSED", file=sys.stderr)
else:
    print("\n\nTEST FAILED", file=sys.stderr)
    sys.exit(1)
