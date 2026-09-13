# emoji-seq-lint

A linter for malformed emoji sequences in text files.

## The problem

Emoji that render as a single glyph are often several Unicode code
points stitched together: a base character, a zero-width joiner, a skin
tone modifier, a variation selector. It's easy to end up with a
sequence that *looks* fine in your editor but is actually broken:

- a zero-width joiner left dangling at the edge of a cluster (usually
  from a bad copy-paste, or a script that truncated a string mid-sequence)
- a skin tone modifier attached to an emoji that has no modifier
  support, so it renders as two separate glyphs on strict platforms
- two skin tone modifiers stacked on the same base
- half a flag: a lone regional indicator, or an odd number of them
- a symbol like a sun or a heart that renders as flat text unless you
  remember to append the emoji variation selector (U+FE0F)

These show up in commit messages, markdown docs, chat bot templates,
i18n resource files - anywhere someone typed or pasted an emoji by
hand. They're invisible until a user on a different platform sees
boxes, or a script that counts "characters" comes out wrong.

## Usage

```
$ python -m emojiseqlint notes.md
notes.md:12:5: ZWJ001 zero-width joiner is not joining two emoji
notes.md:20:1: TONE001 skin tone modifier applied to an emoji that does not support it
notes.md:31:1: FLAG001 odd number of regional indicators (incomplete flag)
notes.md:44:1: VS001 emoji defaults to text presentation without U+FE0F
```

Each line follows the usual `path:line:col: CODE message` shape so it
plugs into editors and CI logs that already know how to parse linter
output.

Exit status is `1` if anything was flagged, `0` otherwise.

For CI or tooling that wants structured output, pass `--format json` to
get a JSON array of `{path, line, col, code, message}` objects instead:

```
$ python -m emojiseqlint --format json notes.md
[
  {
    "path": "notes.md",
    "line": 12,
    "col": 5,
    "code": "ZWJ001",
    "message": "zero-width joiner is not joining two emoji"
  }
]
```

## Install

No dependencies, no build step needed to try it:

```
python -m emojiseqlint some_file.md
```

Or install it as a command:

```
pip install -e .
emoji-seq-lint some_file.md
```

## Tests

```
python -m unittest discover
```

## Rule codes

| Code      | Meaning                                                        |
| --------- | --------------------------------------------------------------- |
| `ZWJ001`  | zero-width joiner not joining two valid emoji                  |
| `ZWJ002`  | emoji joined with ZWJ do not form a recognized sequence         |
| `TONE001` | skin tone modifier on an emoji that doesn't support one         |
| `TONE002` | more than one skin tone modifier in a cluster                   |
| `FLAG001` | odd number of regional indicators (incomplete flag)             |
| `FLAG002` | regional indicator mixed into a non-flag cluster                |
| `VS001`   | text-default symbol missing the emoji variation selector        |

## Status

The emoji data tables (`emojiseqlint/data.py`) are a curated subset,
not the full Unicode emoji-data.txt. Modifier bases now cover most of
the people/gesture blocks, and text-default symbols cover the common
dingbats and miscellaneous symbols people forget to append U+FE0F to.
False negatives on emoji not yet in the tables are still expected.

ZWJ001 only checks that a joiner has emoji on both sides. ZWJ002 goes
further and checks the *shape* of the whole joined cluster against a
closed set of known-good patterns: families (man/woman/boy/girl
combinations), couples and kisses, gender variants (a role plus
U+2642/U+2640), and the flag overlays (rainbow, pirate, transgender).
It only fires when every component in the cluster is one it
recognizes, so profession sequences ("person: microscope" and the
like) are left alone rather than guessed at - that's still a false
negative until those get their own table.

## License

MIT, see LICENSE.
