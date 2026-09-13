"""Tests built from realistic emoji sequences rather than synthetic ones.

Each case spells out the code points it's built from in a comment, since
the actual characters are hard to tell apart by eye once pasted into a
diff or a terminal.
"""

import unittest

from emojiseqlint.linter import scan_line, scan_text

ZWJ = "‍"
VS16 = "️"

GRINNING_FACE = "\U0001F600"
SUN = "☀"
THUMBS_UP = "\U0001F44D"
SKIN_LIGHT = "\U0001F3FB"
SKIN_MED_LIGHT = "\U0001F3FC"
REGIONAL_U = "\U0001F1FA"

MAN = "\U0001F468"
WOMAN = "\U0001F469"
BOY = "\U0001F466"
HEAVY_HEART = "❤"
KISS_MARK = "\U0001F48B"
PERSON = "\U0001F9D1"
MALE_SIGN = "♂"
FEMALE_SIGN = "♀"
BLACK_FLAG = "\U0001F3F4"
SKULL = "☠"
MICROSCOPE = "\U0001F52C"


def codes(findings):
    return [f.code for f in findings]


class DanglingZwjTests(unittest.TestCase):
    def test_zwj_truncated_at_end_of_cluster(self):
        # a base emoji followed by a ZWJ that never got its second half,
        # the "script truncated a string mid-sequence" case from the README
        findings = scan_line(GRINNING_FACE + ZWJ, 1)
        self.assertEqual(codes(findings), ["ZWJ001"])

    def test_bare_zwj_with_no_emoji_at_all(self):
        findings = scan_line("oops" + ZWJ + "sorry", 1)
        self.assertEqual(codes(findings), ["ZWJ001"])

    def test_well_formed_zwj_is_not_flagged(self):
        # man ZWJ woman ZWJ boy: a real, well-formed family sequence
        seq = MAN + ZWJ + WOMAN + ZWJ + BOY
        self.assertEqual(scan_line(seq, 1), [])


class ZwjShapeTests(unittest.TestCase):
    def test_two_known_components_in_an_unrecognized_shape(self):
        # boy ZWJ boy: every component is known, but it isn't a family,
        # couple, gender variant, or flag overlay
        findings = scan_line(BOY + ZWJ + BOY, 1)
        self.assertEqual(codes(findings), ["ZWJ002"])

    def test_gender_variant_is_not_flagged(self):
        # person ZWJ male sign + VS16, e.g. "man scientist"
        seq = PERSON + ZWJ + MALE_SIGN + VS16
        self.assertEqual(scan_line(seq, 1), [])

    def test_gender_variant_with_skin_tone_is_not_flagged(self):
        # the skin tone modifier sits directly before the ZWJ here
        seq = PERSON + SKIN_LIGHT + ZWJ + FEMALE_SIGN + VS16
        self.assertEqual(scan_line(seq, 1), [])

    def test_couple_with_heart_is_not_flagged(self):
        seq = MAN + ZWJ + HEAVY_HEART + VS16 + ZWJ + MAN
        self.assertEqual(scan_line(seq, 1), [])

    def test_kiss_is_not_flagged(self):
        seq = MAN + ZWJ + HEAVY_HEART + VS16 + ZWJ + KISS_MARK + ZWJ + WOMAN
        self.assertEqual(scan_line(seq, 1), [])

    def test_pirate_flag_overlay_is_not_flagged(self):
        seq = BLACK_FLAG + ZWJ + SKULL + VS16
        self.assertEqual(scan_line(seq, 1), [])

    def test_profession_sequence_is_a_known_false_negative(self):
        # person ZWJ microscope: an open-ended "role: object" sequence.
        # Not in KNOWN_ZWJ_COMPONENTS yet, so it's silently let through
        # rather than guessed at wrong. See README "Status".
        seq = PERSON + ZWJ + MICROSCOPE
        self.assertEqual(scan_line(seq, 1), [])


class SkinToneTests(unittest.TestCase):
    def test_tone_on_emoji_without_modifier_support(self):
        findings = scan_line(GRINNING_FACE + SKIN_LIGHT, 1)
        self.assertEqual(codes(findings), ["TONE001"])

    def test_two_tones_stacked_on_one_base(self):
        seq = THUMBS_UP + SKIN_LIGHT + SKIN_MED_LIGHT
        findings = scan_line(seq, 1)
        self.assertEqual(sorted(codes(findings)), ["TONE001", "TONE002"])

    def test_single_valid_tone_is_not_flagged(self):
        self.assertEqual(scan_line(THUMBS_UP + SKIN_LIGHT, 1), [])


class FlagTests(unittest.TestCase):
    def test_lone_regional_indicator(self):
        findings = scan_line(REGIONAL_U, 1)
        self.assertEqual(codes(findings), ["FLAG001"])

    def test_regional_indicator_mixed_with_other_emoji(self):
        findings = scan_line(REGIONAL_U + GRINNING_FACE, 1)
        self.assertEqual(codes(findings), ["FLAG002"])

    def test_complete_flag_pair_is_not_flagged(self):
        regional_s = "\U0001F1F8"
        self.assertEqual(scan_line(REGIONAL_U + regional_s, 1), [])


class VariationSelectorTests(unittest.TestCase):
    def test_text_default_symbol_missing_vs16(self):
        findings = scan_line(SUN, 1)
        self.assertEqual(codes(findings), ["VS001"])

    def test_text_default_symbol_with_vs16_is_not_flagged(self):
        self.assertEqual(scan_line(SUN + VS16, 1), [])


class ScanTextTests(unittest.TestCase):
    def test_line_and_column_track_a_realistic_multiline_document(self):
        lines = [
            "# release notes",
            "",
            "fixed the truncated string bug " + GRINNING_FACE + ZWJ,
            "",
            "look at the sun: " + SUN,
        ]
        findings = scan_text("\n".join(lines))
        self.assertEqual([(f.line, f.code) for f in findings], [(3, "ZWJ001"), (5, "VS001")])
        zwj_finding = findings[0]
        self.assertEqual(zwj_finding.col, len("fixed the truncated string bug ") + len(GRINNING_FACE) + 1)

    def test_clean_document_has_no_findings(self):
        lines = [
            "no emoji here at all",
            "family outing: " + MAN + ZWJ + WOMAN + ZWJ + BOY + ZWJ + BOY,
        ]
        self.assertEqual(scan_text("\n".join(lines)), [])


if __name__ == "__main__":
    unittest.main()
