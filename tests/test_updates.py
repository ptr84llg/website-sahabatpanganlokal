from pathlib import Path
from urllib.parse import urlparse
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UpdateDistributionContractTests(unittest.TestCase):
    def read_text(self, rel):
        return (ROOT / rel).read_text(encoding="utf-8")

    def read_json(self, rel):
        return json.loads(self.read_text(rel))

    @property
    def manifest(self):
        return self.read_json("updates/manifest.json")

    @property
    def schema(self):
        return self.read_json("updates/manifest.schema.json")

    def test_contract_files_exist(self):
        self.assertTrue(
            (ROOT / "updates/manifest.json").is_file(),
            "updates/manifest.json missing",
        )
        self.assertTrue(
            (ROOT / "updates/manifest.schema.json").is_file(),
            "updates/manifest.schema.json missing",
        )

    def test_manifest_and_schema_are_parseable_json(self):
        self.assertIsInstance(self.manifest, dict)
        self.assertIsInstance(self.schema, dict)
        self.assertEqual(
            self.schema.get("$schema"),
            "http://json-schema.org/draft-07/schema#",
        )

    def test_manifest_identity_contract(self):
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["channel"], "stable")
        self.assertRegex(
            self.manifest["generated_at"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$",
        )

    def test_app_version_contract(self):
        app = self.manifest["app"]
        self.assertRegex(app["version"], r"^\d+\.\d+\.\d+$")
        self.assertIsInstance(app["version_code"], int)
        self.assertGreater(app["version_code"], 0)
        self.assertIsInstance(app["min_supported_version_code"], int)
        self.assertGreater(app["min_supported_version_code"], 0)
        self.assertLessEqual(
            app["min_supported_version_code"],
            app["version_code"],
        )
        self.assertIsInstance(app["force_update"], bool)
        self.assertIsInstance(app["release_notes"], list)

    def test_save_schema_version_is_positive_integer(self):
        value = self.manifest["save"]["schema_version"]
        self.assertIsInstance(value, int)
        self.assertGreater(value, 0)

    def test_content_base_contract(self):
        content = self.manifest["content"]
        self.assertEqual(content["format"], "pck")
        self.assertRegex(
            content["version"],
            r"^\d{4}\.\d{2}\.\d{2}\.\d+$",
        )
        self.assertIsInstance(content["required_app_version_code"], int)
        self.assertGreater(content["required_app_version_code"], 0)
        self.assertLessEqual(
            content["required_app_version_code"],
            self.manifest["app"]["version_code"],
        )
        self.assertIsInstance(content["available"], bool)
        self.assertIsInstance(content["required"], bool)

    def test_content_availability_contract(self):
        content = self.manifest["content"]
        if not content["available"]:
            self.assertEqual(content["url"], "")
            self.assertEqual(content["sha256"], "")
            self.assertEqual(content["size"], 0)
            return

        parsed = urlparse(content["url"])
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "sahabatpanganlokal.id")
        self.assertTrue(parsed.path.startswith("/updates/content/"))
        self.assertGreater(content["size"], 0)
        self.assertRegex(content["sha256"], r"^[0-9a-fA-F]{64}$")

    def test_bootstrap_manifest_has_no_fake_package(self):
        content = self.manifest["content"]
        self.assertFalse(content["available"])
        self.assertFalse(content["required"])
        self.assertEqual(content["url"], "")
        self.assertEqual(content["size"], 0)
        self.assertEqual(content["sha256"], "")
        pcks = list(ROOT.rglob("*.pck"))
        self.assertEqual(pcks, [])

    def test_schema_declares_required_top_level_contract(self):
        self.assertEqual(self.schema["type"], "object")
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(
            set(self.schema["required"]),
            {
                "schema_version",
                "channel",
                "generated_at",
                "app",
                "content",
                "save",
            },
        )
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"],
            1,
        )
        self.assertEqual(
            self.schema["properties"]["channel"]["const"],
            "stable",
        )
        self.assertEqual(
            self.schema["properties"]["content"]["properties"]["format"]["const"],
            "pck",
        )

    def test_caddy_update_cache_policy(self):
        caddy = self.read_text("Caddyfile.example")
        self.assertIn(
            "@gameUpdateManifest path /updates/manifest.json",
            caddy,
        )
        self.assertRegex(
            caddy,
            r'header @gameUpdateManifest Cache-Control "no-store, max-age=0"',
        )
        self.assertIn(
            "@gameUpdateSchema path /updates/manifest.schema.json",
            caddy,
        )
        self.assertRegex(
            caddy,
            r'header @gameUpdateSchema Cache-Control "public, max-age=3600"',
        )
        self.assertIn(
            "@gameUpdatePackages path /updates/content/*",
            caddy,
        )
        self.assertRegex(
            caddy,
            r'header @gameUpdatePackages Cache-Control "public, max-age=31536000, immutable"',
        )

    def test_robots_discourages_update_indexing(self):
        robots = self.read_text("robots.txt")
        self.assertIn("Disallow: /updates/", robots)

    def test_updates_are_isolated_from_public_navigation(self):
        for rel in [
            "index.html",
            "assets/js/site-config.js",
            "sitemap.xml",
        ]:
            self.assertNotIn("/updates/", self.read_text(rel), rel)

    def test_legacy_asset_manifest_is_not_reintroduced(self):
        self.assertFalse((ROOT / "assets/asset-manifest.json").exists())
        self.assertTrue((ROOT / "updates/manifest.json").is_file())
        self.assertFalse((ROOT / "assets/updates/manifest.json").exists())

    def test_release_docs_publish_package_before_manifest(self):
        docs = self.read_text("updates/README.md")
        package_pos = docs.index("Upload package terlebih dahulu")
        manifest_pos = docs.index("Publish manifest TERAKHIR")
        self.assertLess(package_pos, manifest_pos)
        self.assertIn("jangan menimpa path/version lama", docs)
        self.assertIn("tidak mengimplementasikan self-install APK", docs)


if __name__ == "__main__":
    unittest.main(verbosity=2)