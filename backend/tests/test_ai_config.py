import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pydantic import ValidationError


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.intelligence.config import AISettings, LOCAL_ENV_FILE, REPOSITORY_ROOT
from app.intelligence.dependencies import _safe_validation_errors, clear_ai_settings_cache
from app.main import app
from fastapi.testclient import TestClient


FAKE_KEY = "fake-openai-key-for-tests-only"
OPENAI_ENV = {
    "AI_PROVIDER": "openai",
    "OPENAI_API_KEY": FAKE_KEY,
    "OPENAI_BASE_URL": "https://example.invalid/v1",
    "AI_MODEL_FAST": "fake-fast-model",
    "AI_MODEL_BALANCED": "fake-balanced-model",
    "AI_MODEL_QUALITY": "fake-quality-model",
    "AI_REQUEST_TIMEOUT_SECONDS": "45",
    "AI_MAX_RETRIES": "2",
    "AI_FALLBACK_ENABLED": "true",
}


class AISettingsTests(unittest.TestCase):
    def test_default_env_file_is_repository_root_local_env(self) -> None:
        self.assertEqual(LOCAL_ENV_FILE, REPOSITORY_ROOT / ".env.local")
        self.assertEqual(REPOSITORY_ROOT, Path(__file__).resolve().parents[2])

    def test_placeholder_is_configured_without_key(self) -> None:
        with patch.dict(os.environ, {"AI_PROVIDER": "placeholder"}, clear=True):
            settings = AISettings(_env_file=None)

        status = settings.to_status()
        self.assertTrue(status.configured)
        self.assertEqual(status.provider, "placeholder")
        self.assertEqual(status.quality_profiles, [])
        self.assertTrue(status.fallback_enabled)
        self.assertEqual(status.configuration_errors, [])
        self.assertNotIn("openai_api_key", settings.model_dump())

    def test_openai_is_configured_with_fake_values(self) -> None:
        with patch.dict(os.environ, OPENAI_ENV, clear=True):
            settings = AISettings(_env_file=None)

        status = settings.to_status()
        self.assertTrue(status.configured)
        self.assertEqual(status.provider, "openai")
        self.assertEqual(status.quality_profiles, ["fast", "balanced", "quality"])
        self.assertEqual(status.configuration_errors, [])

    def test_missing_quality_model_is_reported_safely(self) -> None:
        fields = {
            "AI_MODEL_FAST": "fast",
            "AI_MODEL_BALANCED": "balanced",
            "AI_MODEL_QUALITY": "quality",
        }
        for env_name, profile in fields.items():
            with self.subTest(profile=profile):
                values = dict(OPENAI_ENV)
                values.pop(env_name)
                with patch.dict(os.environ, values, clear=True):
                    status = AISettings(_env_file=None).to_status()

                self.assertFalse(status.configured)
                self.assertNotIn(profile, status.quality_profiles)
                self.assertTrue(any(env_name in message for message in status.configuration_errors))
                self.assertNotIn(FAKE_KEY, json.dumps(status.model_dump()))

    def test_process_environment_overrides_env_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env.local"
            env_file.write_text(
                "\n".join(
                    [
                        "AI_PROVIDER=placeholder",
                        "AI_MODEL_FAST=file-fast-model",
                        "AI_FALLBACK_ENABLED=false",
                    ]
                ),
                encoding="utf-8",
            )
            with patch.dict(os.environ, OPENAI_ENV, clear=True):
                settings = AISettings(_env_file=env_file)

        self.assertEqual(settings.provider, "openai")
        self.assertEqual(settings.ai_model_fast, "fake-fast-model")
        self.assertTrue(settings.ai_fallback_enabled)
        self.assertTrue(settings.configured)

    def test_validation_messages_do_not_contain_api_key(self) -> None:
        values = dict(OPENAI_ENV)
        values["AI_MAX_RETRIES"] = "99"
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaises(ValidationError) as raised:
                AISettings(_env_file=None)

        safe_errors = _safe_validation_errors(raised.exception)
        self.assertNotIn(FAKE_KEY, str(raised.exception))
        self.assertNotIn(FAKE_KEY, json.dumps(safe_errors))
        self.assertEqual(safe_errors, ["Invalid value for AI_MAX_RETRIES."])


class AIStatusEndpointTests(unittest.TestCase):
    def tearDown(self) -> None:
        clear_ai_settings_cache()

    def test_status_endpoint_exposes_only_safe_metadata(self) -> None:
        with (
            patch.dict(os.environ, OPENAI_ENV, clear=True),
            patch.dict(AISettings.model_config, {"env_file": None}),
        ):
            clear_ai_settings_cache()
            with TestClient(app) as client:
                response = client.get("/api/intelligence/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "configured": True,
                "provider": "openai",
                "quality_profiles": ["fast", "balanced", "quality"],
                "fallback_enabled": True,
                "configuration_errors": [],
            },
        )
        serialized = response.text
        self.assertNotIn(FAKE_KEY, serialized)
        self.assertNotIn("fake-fast-model", serialized)
        self.assertNotIn("OPENAI_API_KEY", serialized)


if __name__ == "__main__":
    unittest.main()
