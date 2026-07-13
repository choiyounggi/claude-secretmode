#!/usr/bin/env python3
"""Unit tests for the token-sync recency verdict (bin/secretmode-token-verdict.py).

The verdict decides whether the daemon should replace the session's RAM-disk
credential with the keychain's. The one invariant: an OLDER token must never
overwrite a NEWER one (that rollback is what logs a secret session out).
"""
import importlib.util
import json
import os
import unittest

HELPER = os.path.join(os.path.dirname(__file__), "..", "bin", "secretmode-token-verdict.py")
_spec = importlib.util.spec_from_file_location("verdict_mod", HELPER)
verdict_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verdict_mod)
verdict = verdict_mod.verdict


def tok(expires):
    return json.dumps({"claudeAiOauth": {"accessToken": "x", "expiresAt": expires}})


class TokenVerdict(unittest.TestCase):
    # ── normal path ──
    def test_keychain_newer_updates(self):
        # a concurrent normal `claude` refreshed the token → adopt it
        self.assertEqual(verdict(tok(2000), tok(1000)), "UPDATE")

    # ── core regression: the bug this fix exists for ──
    def test_session_newer_is_never_rolled_back(self):
        # this session refreshed its own token; keychain is stale → keep ours
        self.assertEqual(verdict(tok(1000), tok(2000)), "SKIP")

    def test_equal_expiry_skips(self):
        self.assertEqual(verdict(tok(1500), tok(1500)), "SKIP")

    # ── error cases (trust boundary: keychain / file contents are external) ──
    def test_unparseable_keychain_skips(self):
        self.assertEqual(verdict("not json at all", tok(1000)), "SKIP")

    def test_empty_keychain_skips(self):
        self.assertEqual(verdict("", tok(1000)), "SKIP")

    def test_unparseable_session_restores_from_keychain(self):
        # a corrupted RAM file should be repaired from the keychain
        self.assertEqual(verdict(tok(1000), "not json"), "UPDATE")

    def test_both_unparseable_skips(self):
        self.assertEqual(verdict("", ""), "SKIP")

    # ── boundary: missing / malformed expiresAt ──
    def test_missing_expiresAt_key_skips(self):
        self.assertEqual(verdict(json.dumps({"claudeAiOauth": {}}), tok(1000)), "SKIP")

    def test_non_numeric_expiresAt_skips(self):
        bad = json.dumps({"claudeAiOauth": {"expiresAt": "soon"}})
        self.assertEqual(verdict(bad, tok(1000)), "SKIP")

    def test_expiresAt_as_numeric_string_is_compared(self):
        # keychain may store the epoch as a JSON string; still comparable
        newer = json.dumps({"claudeAiOauth": {"expiresAt": "2000"}})
        self.assertEqual(verdict(newer, tok(1000)), "UPDATE")


if __name__ == "__main__":
    unittest.main()
