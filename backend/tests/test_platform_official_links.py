from pathlib import Path
import sys
import unittest
from urllib.parse import urlparse


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.data import ECOSYSTEMS


class PlatformOfficialLinkTests(unittest.TestCase):
    def test_all_platforms_have_unique_official_https_links(self) -> None:
        expected_domains = {
            "siemens-tia": "www.siemens.com",
            "codesys": "www.codesys.com",
            "twincat": "www.beckhoff.com",
            "rockwell": "www.rockwellautomation.com",
            "mitsubishi": "www.mitsubishielectric.com",
            "omron": "automation.omron.com",
        }
        urls = []

        for platform in ECOSYSTEMS:
            with self.subTest(platform=platform.id):
                parsed = urlparse(platform.official_url)
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, expected_domains[platform.id])
                urls.append(platform.official_url)

        self.assertEqual(len(urls), len(set(urls)))


if __name__ == "__main__":
    unittest.main()
