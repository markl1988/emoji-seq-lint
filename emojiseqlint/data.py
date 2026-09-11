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


# Emoji that can take a skin tone modifier (Emoji_Modifier_Base). Expressed
# as contiguous ranges plus standalone code points, mirroring the layout of
# Unicode's emoji-data.txt so it's easier to check against future updates.
MODIFIER_BASE_RANGES = (
    (0x270A, 0x270D),  # raised fist .. writing hand
    (0x1F3C2, 0x1F3C4),  # snowboarder .. person surfing
    (0x1F3CA, 0x1F3CC),  # person swimming .. person golfing
    (0x1F442, 0x1F443),  # ear, nose
    (0x1F446, 0x1F450),  # pointing hands .. open hands
    (0x1F466, 0x1F469),  # boy .. woman
    (0x1F470, 0x1F478),  # bride with veil .. princess
    (0x1F481, 0x1F483),  # person tipping hand .. woman dancing
    (0x1F485, 0x1F487),  # nail polish .. person getting haircut
    (0x1F574, 0x1F575),  # man in suit levitating .. detective
    (0x1F595, 0x1F596),  # middle finger, vulcan salute
    (0x1F645, 0x1F647),  # person gesturing NO .. person bowing
    (0x1F64B, 0x1F64F),  # person raising hand .. folded hands
    (0x1F6B4, 0x1F6B6),  # person biking .. person walking
    (0x1F918, 0x1F91F),  # sign of the horns .. love-you gesture
    (0x1F930, 0x1F939),  # pregnant woman .. person juggling
    (0x1F93D, 0x1F93E),  # person playing water polo/handball
    (0x1F9B5, 0x1F9B6),  # leg, foot
    (0x1F9B8, 0x1F9B9),  # superhero, supervillain
    (0x1F9CD, 0x1F9CF),  # person standing .. deaf person
    (0x1F9D1, 0x1F9DD),  # person .. elf
)

MODIFIER_BASE_SINGLES = {
    "☝",  # index pointing up
    "⛹",  # person bouncing ball
    "\U0001F385",  # Santa Claus
    "\U0001F3C7",  # horse racing
    "\U0001F46E",  # police officer
    "\U0001F47C",  # baby angel
    "\U0001F48F",  # kiss
    "\U0001F491",  # couple with heart
    "\U0001F4AA",  # flexed biceps
    "\U0001F57A",  # man dancing
    "\U0001F590",  # hand with fingers splayed
    "\U0001F6A3",  # person rowing boat
    "\U0001F6C0",  # person taking bath
    "\U0001F6CC",  # person in bed
    "\U0001F90C",  # pinched fingers
    "\U0001F90F",  # pinching hand
    "\U0001F926",  # person facepalming
    "\U0001F9BB",  # ear with hearing aid
}

MODIFIER_BASES = MODIFIER_BASE_SINGLES | {
    chr(cp) for lo, hi in MODIFIER_BASE_RANGES for cp in range(lo, hi + 1)
}

# Components of the closed set of ZWJ sequences we know how to validate:
# families, couples/kisses, gender variants ("role" + gender sign), and the
# flag overlays (rainbow, pirate, transgender). Profession sequences (role +
# object, e.g. "person: microscope") are open-ended and not covered yet.
FAMILY_ADULTS = {"\U0001F468", "\U0001F469"}  # man, woman
FAMILY_CHILDREN = {"\U0001F466", "\U0001F467"}  # boy, girl
FAMILY_MEMBERS = FAMILY_ADULTS | FAMILY_CHILDREN

COUPLE_HEART = "❤"  # heavy black heart
KISS_MARK = "\U0001F48B"

MALE_SIGN = "♂"
FEMALE_SIGN = "♀"
GENDER_SIGNS = {MALE_SIGN, FEMALE_SIGN}

WHITE_FLAG = "\U0001F3F3"
BLACK_FLAG = "\U0001F3F4"
RAINBOW = "\U0001F308"
SKULL_AND_CROSSBONES = "☠"
TRANSGENDER_SYMBOL = "⚧"

KNOWN_ZWJ_COMPONENTS = (
    FAMILY_MEMBERS
    | MODIFIER_BASES
    | GENDER_SIGNS
    | {
        COUPLE_HEART,
        KISS_MARK,
        WHITE_FLAG,
        BLACK_FLAG,
        RAINBOW,
        SKULL_AND_CROSSBONES,
        TRANSGENDER_SYMBOL,
    }
)

# Emoji that default to *text* presentation and need a trailing VS16 to
# render as a colored glyph instead of flat text. Curated subset of the
# ones people misuse most.
TEXT_DEFAULT_EMOJI = {
    "☀", "☁", "☂", "☃", "☄", "☎",
    "☑", "☘", "☝", "☠", "☢", "☣",
    "☦", "☪", "☮", "☯", "☸", "☹",
    "☺", "♀", "♂", "♠", "♣", "♥",
    "♦", "♨", "♻", "♿", "⚒", "⚔",
    "⚕", "⚖", "⚗", "⚙", "⚠", "⚡",
    "✂", "✉", "✍", "✏", "✒", "✔",
    "✖", "✝", "✡", "✳", "✴", "❄",
    "❇", "❣", "❤", "‼", "⁉",
    "▪", "▫", "◻", "◼",
}

# Rough ranges used to decide whether a code point belongs to an emoji
# cluster at all, as opposed to plain text. Not exhaustive.
EMOJI_RANGES = (
    (0x203C, 0x203C),  # double exclamation mark
    (0x2049, 0x2049),  # exclamation question mark
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
