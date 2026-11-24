#!/usr/bin/env python3
"""One Emoji, One Dream Vacation — make.fun entry.

Writes exactly one emoji, nothing else, to the entry file.

The emoji is a desert island (U+1F3DD + U+FE0F): the postcard image of
a dream vacation — a faraway island, sun, sea and sand, readable at a
glance in any culture. It beats the obvious alternatives on the judge's
own brief: a beach-with-umbrella is the generic pick every entrant
reaches for, a lone palm tree names no place, and a plane names the
journey, not the dream. The island is one specific place, vivid as a
postcard, and instantly clear at small size.

Stdlib only. No network, no secrets, no files outside the repository.
Output path defaults to /output/entry.txt and can be overridden with
the ENTRY_OUTPUT environment variable.
"""

import os
import sys

# U+1F3DD DESERT ISLAND + U+FE0F VARIATION SELECTOR-16 (emoji presentation).
ENTRY = "\U0001F3DD\uFE0F"

DEFAULT_OUTPUT = "/output/entry.txt"

# Code points that may follow an emoji base inside one grapheme cluster:
# U+FE0F forces emoji presentation; U+200D joins a ZWJ sequence.
_EMOJI_MODIFIERS = {"\uFE0F", "\u200D"}


def _is_emoji_base(char: str) -> bool:
    """True when a single character is an emoji base code point.

    Uses the standard emoji ranges (symbols & pictographs, transport,
    flags, dingbats, emoticons, supplemental symbols) rather than a
    hard-coded allow-list, so the check stays honest about the entry.
    """
    code = ord(char)
    return (
        0x1F000 <= code <= 0x1FAFF  # symbols & pictographs, incl. U+1F3DD
        or 0x2600 <= code <= 0x27BF  # misc symbols & dingbats
        or 0x2190 <= code <= 0x21FF  # arrows
        or 0x2300 <= code <= 0x23FF  # misc technical
        or 0x2B00 <= code <= 0x2BFF  # misc symbols and arrows
        or 0xFE00 <= code <= 0xFE0F  # variation selectors
        or 0x1F1E6 <= code <= 0x1F1FF  # regional indicators (flags)
    )


def validate_entry(entry: str) -> str | None:
    """Return an error message if entry fails the competition gate.

    Gate (RULES.txt): UTF-8 text of 1 to 8 characters, not only white
    space, and — per the task and judge brief — exactly one emoji.
    A single emoji is one grapheme cluster: one emoji base code point
    followed only by presentation/join modifiers, so a two-code-point
    entry like the desert island still counts as one emoji.
    """
    chars = list(entry)
    if not 1 <= len(chars) <= 8:
        return f"entry must be 1-8 characters, got {len(chars)}"
    if entry.strip() == "":
        return "entry must not be only white space"
    if not _is_emoji_base(chars[0]):
        return "entry must start with an emoji"
    if any(c not in _EMOJI_MODIFIERS for c in chars[1:]):
        return "entry must be exactly one emoji (base + modifiers only)"
    return None


def main() -> int:
    output_path = os.environ.get("ENTRY_OUTPUT") or DEFAULT_OUTPUT

    error = validate_entry(ENTRY)
    if error is not None:
        print(error, file=sys.stderr)
        return 1

    data = ENTRY.encode("utf-8")
    parent = os.path.dirname(os.path.abspath(output_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(data)

    # Read the file back and re-check it: the graded artifact is the
    # file on disk, so a silent short write must fail loudly here
    # instead of shipping a broken entry.
    with open(output_path, "rb") as f:
        written = f.read()
    if written != data:
        print("entry file does not match the intended entry", file=sys.stderr)
        return 1
    if validate_entry(written.decode("utf-8")) is not None:
        print("written entry fails the gate on re-read", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
