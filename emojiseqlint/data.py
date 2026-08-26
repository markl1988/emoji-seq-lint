"""Curated Unicode emoji data.

This is a small, hand-picked subset rather than the full Unicode
emoji-data.txt tables. It catches the common mistakes; widening
coverage is ongoing work (see README "Status").
"""

ZWJ = "‍"
VS16 = "️"
VS15 = "︎"

SKIN_TONE_MODIFIERS = {
    "\U0001F3FB",  # light
    "\U0001F3FC",  # medium-light
    "\U0001F3FD",  # medium
    "\U0001F3FE",  # medium-dark
    "\U0001F3FF",  # dark
}

REGIONAL_INDICATOR_START = 0x1F1E6
REGIONAL_INDICATOR_END = 0x1F1FF


def is_regional_indicator(ch):
    return REGIONAL_INDICATOR_START <= ord(ch) <= REGIONAL_INDICATOR_END


# Emoji that can take a skin tone modifier (Emoji_Modifier_Base), curated
# from the hands/people/gestures blocks that come up most often.
MODIFIER_BASES = {
    "\U0001F44B", "\U0001F44C", "\U0001F44D", "\U0001F44E",
    "\U0001F44F", "\U0001F450", "\U0001F466", "\U0001F467",
    "\U0001F468", "\U0001F469", "\U0001F46E", "\U0001F470",
    "\U0001F471", "\U0001F472", "\U0001F473", "\U0001F474",
    "\U0001F475", "\U0001F476", "\U0001F477", "\U0001F478",
    "\U0001F47C", "\U0001F481", "\U0001F482", "\U0001F483",
    "\U0001F485", "\U0001F486", "\U0001F487", "\U0001F4AA",
    "\U0001F595", "\U0001F596", "\U0001F64B", "\U0001F64C",
    "\U0001F64D", "\U0001F64E", "\U0001F64F",
    "✊", "✋", "✌", "☝",
}

# Emoji that default to *text* presentation and need a trailing VS16 to
# render as a colored glyph instead of flat text. Curated subset of the
# ones people misuse most.
TEXT_DEFAULT_EMOJI = {
    "☀", "☁", "☂", "☃", "☄", "☎",
    "☑", "☘", "☝", "☠", "☢", "☣",
    "☦", "☪", "☮", "☯", "☸", "☹",
    "☺", "♠", "♣", "♥", "♦", "♨",
    "♻", "♿", "⚒", "⚕", "⚖", "⚗",
    "⚙", "⚠", "⚡", "❤",
}

# Rough ranges used to decide whether a code point belongs to an emoji
# cluster at all, as opposed to plain text. Not exhaustive.
EMOJI_RANGES = (
    (0x2190, 0x21FF),  # arrows
    (0x2300, 0x23FF),  # misc technical
    (0x25A0, 0x27BF),  # geometric shapes, misc symbols, dingbats
    (0x2900, 0x297F),  # supplemental arrows
    (0x2B00, 0x2BFF),  # misc symbols and arrows
    (0x1F000, 0x1FAFF),  # emoji planes (includes regional indicators)
)


def is_emoji_codepoint(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in EMOJI_RANGES)
