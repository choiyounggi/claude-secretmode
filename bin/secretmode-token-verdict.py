#!/usr/bin/env python3
"""Decide whether the token-sync daemon should replace the session's RAM-disk
credential with the one currently in the macOS keychain.

Prints UPDATE only when the keychain token is strictly newer than the session's
(a larger ``claudeAiOauth.expiresAt``); otherwise SKIP. This is the guard that
stops the daemon from rolling a token *this* session just refreshed back to the
keychain's older copy — the rollback that silently logs a secret session out.

Inputs come from the environment so the token value never appears in argv:
  SECRETMODE_NEW  the keychain's current credential JSON (candidate)
  SECRETMODE_CUR  the session's RAM-disk credential JSON (in use)
"""
import json
import os
import sys


def _expires(raw):
    """Return claudeAiOauth.expiresAt as an int, or None if it can't be read.

    The values are external (keychain blob / RAM file), so any shape is possible;
    an unreadable value yields None and is treated conservatively by verdict().
    """
    try:
        return int(json.loads(raw)["claudeAiOauth"]["expiresAt"])
    except (ValueError, TypeError, KeyError):
        return None


def verdict(new, cur):
    """UPDATE iff the keychain token (new) is strictly newer than the session's (cur).

    - keychain unreadable            -> SKIP   (never overwrite with a bad value)
    - session unreadable, keychain ok -> UPDATE (repair a corrupted RAM file)
    - both readable                  -> UPDATE only when new expiry > cur expiry
    """
    n = _expires(new)
    if n is None:
        return "SKIP"
    c = _expires(cur)
    if c is None:
        return "UPDATE"
    return "UPDATE" if n > c else "SKIP"


if __name__ == "__main__":
    sys.stdout.write(
        verdict(os.environ.get("SECRETMODE_NEW", ""), os.environ.get("SECRETMODE_CUR", ""))
    )
