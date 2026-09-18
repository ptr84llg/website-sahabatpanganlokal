from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import tempfile
from pathlib import Path
import sys
import unittest
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

from site_api.health import classify_server_status, classify_traffic
from site_api.tokens import TokenError, create_preflight_token, verify_preflight_token


class SiteApiCoreTests(unittest.TestCase):
    SECRET = "x" * 64

    def test_preflight_token_round_trip_and_expiry(self):
        now = datetime(2026, 9, 12, 8, 0, tzinfo=timezone.utc)
        nonce = uuid4()
        token = create_preflight_token(
            "android", "1.0.0", nonce, now, self.SECRET, 300
        )
        claims = verify_preflight_token(token, now + timedelta(seconds=299), self.SECRET)
        self.assertEqual(claims.platform, "android")
        self.assertEqual(claims.version, "1.0.0")
        self.assertEqual(claims.nonce, nonce)

        with self.assertRaises(TokenError):
            verify_preflight_token(token, now + timedelta(seconds=301), self.SECRET)

    def test_preflight_token_rejects_tampering(self):
        now = datetime(2026, 9, 12, 8, 0, tzinfo=timezone.utc)
        token = create_preflight_token(
            "windows", "1.0.0", uuid4(), now, self.SECRET, 300
        )
        body, signature = token.split(".", 1)
        tampered = ("A" if body[0] != "A" else "B") + body[1:] + "." + signature
        with self.assertRaises(TokenError):
            verify_preflight_token(tampered, now, self.SECRET)

    def test_sha256_file_hashes_real_file(self):
        module_path = ROOT / "integrity.py"
        self.assertTrue(module_path.is_file(), "integrity.py missing")

        spec = importlib.util.spec_from_file_location(
            "site_api_integrity_test",
            module_path,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        payload = b"sahabat-pangan-lokal-integrity-test"
        with tempfile.TemporaryDirectory() as temp_dir:
            sample = Path(temp_dir) / "sample.bin"
            sample.write_bytes(payload)
            expected = hashlib.sha256(payload).hexdigest()
            self.assertEqual(module.sha256_file(sample), expected)

    def test_preflight_uses_actual_package_sha256(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("from .integrity import sha256_file", source)
        self.assertIn("actual_hash = sha256_file(package_path)", source)
        self.assertIn("if actual_hash != stored_hash:", source)

    def test_traffic_thresholds(self):
        self.assertEqual(classify_traffic(0), "low")
        self.assertEqual(classify_traffic(9), "low")
        self.assertEqual(classify_traffic(10), "moderate")
        self.assertEqual(classify_traffic(49), "moderate")
        self.assertEqual(classify_traffic(50), "high")

    def test_server_status_uses_worst_indicator(self):
        self.assertEqual(classify_server_status(.20, .70, 120), "normal")
        self.assertEqual(classify_server_status(.60, .70, 120), "busy")
        self.assertEqual(classify_server_status(.20, .30, 120), "busy")
        self.assertEqual(classify_server_status(.20, .70, 500), "busy")
        self.assertEqual(classify_server_status(.91, .70, 120), "high_load")
        self.assertEqual(classify_server_status(.20, .14, 120), "high_load")
        self.assertEqual(classify_server_status(.20, .70, 1001), "high_load")

    def test_sql_schema_excludes_prohibited_persistent_identifiers(self):
        sql = (ROOT / "sql" / "001_init.sql").read_text(encoding="utf-8").lower()
        for forbidden in [
            "raw_ip", "latitude", "longitude", "imei", "mac_address",
            "android_id", "advertising_id", "device_serial", "email", "phone"
        ]:
            self.assertNotIn(forbidden, sql)
        self.assertIn("preflight_nonce uuid not null unique", sql)


if __name__ == "__main__":
    unittest.main(verbosity=2)