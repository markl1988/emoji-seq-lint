"""Core scanning and rule logic.

The approach: walk each line character by character, group contiguous
runs of "emoji-ish" characters (emoji code points, ZWJ, the emoji
variation selector, skin tone modifiers, regional indicators) into
clusters, then run a handful of independent checks against each cluster.
"""

from collections import namedtuple

from .data import (
    ZWJ,
    VS16,
    SKIN_TONE_MODIFIERS,
    MODIFIER_BASES,
    TEXT_DEFAULT_EMOJI,
    FAMILY_ADULTS,
    FAMILY_CHILDREN,
    FAMILY_MEMBERS,
    COUPLE_HEART,
    KISS_MARK,
    MALE_SIGN,
    FEMALE_SIGN,
    WHITE_FLAG,
    BLACK_FLAG,
    RAINBOW,
    SKULL_AND_CROSSBONES,
    TRANSGENDER_SYMBOL,
    KNOWN_ZWJ_COMPONENTS,
    is_emoji_codepoint,
    is_regional_indicator,
)

Finding = namedtuple("Finding", ["line", "col", "code", "message"])


def _is_cluster_char(ch):
    return (
        is_emoji_codepoint(ch)
        or ch == ZWJ
        or ch == VS16
        or ch in SKIN_TONE_MODIFIERS
    )


def _find_clusters(text):
    """Yield (start_index, chars) for each contiguous run of cluster chars."""
    clusters = []
    start = None
    current = []
    for i, ch in enumerate(text):
        if _is_cluster_char(ch):
            if start is None:
                start = i
            current.append(ch)
        else:
            if current:
                clusters.append((start, current))
            start = None
            current = []
    if current:
        clusters.append((start, current))
    return clusters


def _check_dangling_zwj(seq):
    findings = []
    for i, ch in enumerate(seq):
        if ch != ZWJ:
            continue
        # The component right before a ZWJ often isn't the base emoji
        # itself but a trailing VS16 (hearts) or skin tone modifier
        # (people/gestures) attached to it, e.g. the heart in the
        # couple-with-heart sequence or a role in a gender variant.
        has_prev = i > 0 and (
            is_emoji_codepoint(seq[i - 1])
            or seq[i - 1] == VS16
            or seq[i - 1] in SKIN_TONE_MODIFIERS
        )
        has_next = i < len(seq) - 1 and (
            is_emoji_codepoint(seq[i + 1]) or seq[i + 1] in SKIN_TONE_MODIFIERS
        )
        if not (has_prev and has_next):
            findings.append((i, "ZWJ001", "zero-width joiner is not joining two emoji"))
    return findings


def _check_skin_tone(seq):
    findings = []
    seen_tone = False
    for i, ch in enumerate(seq):
        if ch not in SKIN_TONE_MODIFIERS:
            continue
        if i == 0 or seq[i - 1] not in MODIFIER_BASES:
            findings.append(
                (i, "TONE001", "skin tone modifier applied to an emoji that does not support it")
            )
        if seen_tone:
            findings.append((i, "TONE002", "more than one skin tone modifier in a single cluster"))
        seen_tone = True
    return findings


def _check_flag(seq):
    findings = []
    ri_count = sum(1 for ch in seq if is_regional_indicator(ch))
    if ri_count == 0:
        return findings
    if ri_count != len(seq):
        first = next(i for i, ch in enumerate(seq) if is_regional_indicator(ch))
        findings.append((first, "FLAG002", "regional indicator mixed into a non-flag cluster"))
    elif ri_count % 2 != 0:
        findings.append((len(seq) - 1, "FLAG001", "odd number of regional indicators (incomplete flag)"))
    return findings


def _check_missing_vs16(seq):
    findings = []
    for i, ch in enumerate(seq):
        if ch in TEXT_DEFAULT_EMOJI:
            nxt = seq[i + 1] if i + 1 < len(seq) else ""
            if nxt != VS16:
                findings.append((i, "VS001", "emoji defaults to text presentation without U+FE0F"))
    return findings


def _split_on_zwj(spine):
    """Split a ZWJ-joined spine into the groups it links together.

    Each group is a tuple of the chars between one ZWJ and the next (a base,
    optionally followed by U+FE0F). A dangling ZWJ produces an empty group.
    """
    groups = []
    current = []
    for ch in spine:
        if ch == ZWJ:
            groups.append(tuple(current))
            current = []
        else:
            current.append(ch)
    groups.append(tuple(current))
    return groups


def _is_family(groups):
    if any(len(g) != 1 or g[0] not in FAMILY_MEMBERS for g in groups):
        return False
    adults = sum(1 for g in groups if g[0] in FAMILY_ADULTS)
    children = sum(1 for g in groups if g[0] in FAMILY_CHILDREN)
    return 1 <= adults <= 2 and 1 <= children <= 2 and adults + children == len(groups)


def _is_couple_or_kiss(groups):
    heart = (COUPLE_HEART, VS16)
    if len(groups) == 3:
        adult1, h, adult2 = groups
        return (
            len(adult1) == 1 and adult1[0] in FAMILY_ADULTS
            and h == heart
            and len(adult2) == 1 and adult2[0] in FAMILY_ADULTS
        )
    if len(groups) == 4:
        adult1, h, kiss, adult2 = groups
        return (
            len(adult1) == 1 and adult1[0] in FAMILY_ADULTS
            and h == heart
            and kiss == (KISS_MARK,)
            and len(adult2) == 1 and adult2[0] in FAMILY_ADULTS
        )
    return False


def _is_gender_variant(groups):
    if len(groups) != 2:
        return False
    role, sign = groups
    role_ok = (
        len(role) in (1, 2)
        and role[0] in MODIFIER_BASES
        and (len(role) == 1 or role[1] == VS16)
    )
    return role_ok and sign in ((MALE_SIGN, VS16), (FEMALE_SIGN, VS16))


def _is_flag_overlay(groups):
    if len(groups) != 2:
        return False
    base, overlay = groups
    if base == (WHITE_FLAG, VS16):
        return overlay in ((RAINBOW,), (TRANSGENDER_SYMBOL, VS16))
    if base == (BLACK_FLAG,):
        return overlay == (SKULL_AND_CROSSBONES, VS16)
    return False


def _check_zwj_sequence(seq):
    if ZWJ not in seq:
        return []
    # Skin tone modifiers can attach to a family/role member without
    # changing which sequence it is, so ignore them for shape matching.
    spine = [ch for ch in seq if ch not in SKIN_TONE_MODIFIERS]
    groups = _split_on_zwj(spine)
    if any(len(g) == 0 for g in groups):
        return []  # dangling ZWJ, already reported by _check_dangling_zwj
    plain = [ch for ch in spine if ch != ZWJ]
    if any(ch != VS16 and ch not in KNOWN_ZWJ_COMPONENTS for ch in plain):
        return []  # involves a component we don't have curated data for
    if (
        _is_family(groups)
        or _is_couple_or_kiss(groups)
        or _is_gender_variant(groups)
        or _is_flag_overlay(groups)
    ):
        return []
    return [(seq.index(ZWJ), "ZWJ002", "emoji joined with ZWJ do not form a recognized sequence")]


_CHECKS = (
    _check_dangling_zwj,
    _check_zwj_sequence,
    _check_skin_tone,
    _check_flag,
    _check_missing_vs16,
)


def scan_line(text, lineno):
    findings = []
    for start, seq in _find_clusters(text):
        for check in _CHECKS:
            for offset, code, message in check(seq):
                findings.append(Finding(lineno, start + offset + 1, code, message))
    return findings


def scan_text(text):
    findings = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        findings.extend(scan_line(line, lineno))
    return findings
