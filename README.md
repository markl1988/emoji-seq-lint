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

## Rule codes

| Code      | Meaning                                                        |
| --------- | --------------------------------------------------------------- |
| `ZWJ001`  | zero-width joiner not joining two valid emoji                  |
| `TONE001` | skin tone modifier on an emoji that doesn't support one         |
| `TONE002` | more than one skin tone modifier in a cluster                   |
| `FLAG001` | odd number of regional indicators (incomplete flag)             |
| `FLAG002` | regional indicator mixed into a non-flag cluster                |
| `VS001`   | text-default symbol missing the emoji variation selector        |

## Status

The emoji data tables (`emojiseqlint/data.py`) are a curated subset,
not the full Unicode emoji-data.txt. Coverage of modifier bases and
text-default symbols will grow over time; false negatives on emoji not
yet in the tables are expected for now.

## License

MIT, see LICENSE.
