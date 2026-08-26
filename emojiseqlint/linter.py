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
        has_prev = i > 0 and is_emoji_codepoint(seq[i - 1])
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


_CHECKS = (_check_dangling_zwj, _check_skin_tone, _check_flag, _check_missing_vs16)


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
