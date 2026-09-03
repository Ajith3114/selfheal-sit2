#!/usr/bin/env python3
"""
Checks index.html before we deploy it.

Why this exists:
    The old health check was just `grep -q "SITE-OK"`. That only proves one
    magic word is somewhere in the file. It cannot tell a real page from a
    broken one - a file containing nothing but the word SITE-OK would pass.

    This runs four checks instead. Run it the same way locally or in CI:

        python check-html.py index.html

Uses only the Python standard library, so there is nothing to install.
"""

import sys
from html.parser import HTMLParser

MARKER = "SITE-OK"

# Tags that never need closing - <br>, <img>, <meta> and friends.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}


class TagChecker(HTMLParser):
    """Keeps a stack of open tags and reports the ones never closed."""

    def __init__(self):
        super().__init__()
        self.open_tags = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.open_tags.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if not self.open_tags:
            self.errors.append(f"stray </{tag}> at line {self.getpos()[0]}")
            return

        # Normal case: this closes the most recent open tag.
        if self.open_tags[-1][0] == tag:
            self.open_tags.pop()
            return

        # Otherwise something in between was left open. Find the matching
        # tag further down the stack and report everything above it.
        for i in range(len(self.open_tags) - 1, -1, -1):
            if self.open_tags[i][0] == tag:
                for unclosed, line in self.open_tags[i + 1:]:
                    self.errors.append(
                        f"<{unclosed}> opened at line {line} was never closed")
                del self.open_tags[i:]
                return

        self.errors.append(f"stray </{tag}> at line {self.getpos()[0]}")

    def finish(self):
        for tag, line in self.open_tags:
            self.errors.append(f"<{tag}> opened at line {line} was never closed")
        return self.errors


def main(path):
    problems = []

    # ---- check 1: the file has something in it ----
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"FAIL  {path} does not exist")
        return 1

    if not text.strip():
        problems.append(f"{path} is empty")

    # ---- check 2: the marker appears EXACTLY ONCE ----
    # "at least once" is not good enough. If the word also appears in normal
    # page text, deleting the real marker still leaves matches behind, and
    # the health check can never fail. That was the original bug.
    count = text.count(MARKER)
    if count != 1:
        problems.append(
            f"expected exactly 1 '{MARKER}', found {count}"
            + (" - the health check cannot fail" if count > 1 else ""))

    # ---- check 3: the basic page skeleton is present ----
    for needed in ("<!DOCTYPE html>", "<title>", "</head>", "</body>", "</html>"):
        if needed not in text:
            problems.append(f"missing {needed}")

    # ---- check 4: every tag that opens also closes ----
    checker = TagChecker()
    checker.feed(text)
    problems.extend(checker.finish())

    # ---- report ----
    if problems:
        print(f"FAIL  {path} - {len(problems)} problem(s):")
        for p in problems:
            print(f"        - {p}")
        return 1

    print(f"OK    {path} - {len(text)} bytes, 1 '{MARKER}', tags balanced")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    sys.exit(main(target))
