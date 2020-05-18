from md2gemini import md2gemini, NEWLINE
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
Another sentence, with [another](gemini://gus.guru/) link.

![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png) with words after

https://example.com/link/with/no/text
[Alone link with text](https://example.com/) and text after
https://example.com/
some text here.

[Alone link with text, separate](https://example.com)

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

out = md2gemini(md, jekyll=True, links="paragraph")
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

It's very easy to make some words **bold** and other words *italic* with Markdown. You can even do inline[1] links! Another sentence, with another[2] link.

=> http://google.com 1: http://google.com
=> gemini://gus.guru/ 2: gemini://gus.guru/

Image of Yaktocat[3] with words after

=> https://octodex.github.com/images/yaktocat.png 3: https://octodex.github.com/images/yaktocat.png

https://example.com/link/with/no/text[4] Alone link with text[5] and text after https://example.com/[6] some text here.

=> https://example.com/link/with/no/text 4: https://example.com/link/with/no/text
=> https://example.com/ 5: https://example.com/
=> https://example.com/ 6: https://example.com/

=> https://example.com Alone link with text, separate

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

```
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
