import os
import subprocess
import sys

from django.test import SimpleTestCase


class DatabaseSettingsTests(SimpleTestCase):
    def run_settings_import(self, database_url):
        env = os.environ.copy()
        for name in (
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
        ):
            env.pop(name, None)
        env.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "SECRET_KEY": "settings-test-key",
                "DEBUG": "False",
                "CLOUDINARY_URL": (
                    "cloudinary://test-key:test-secret@example-cloud"
                ),
                "DATABASE_URL": database_url,
            }
        )
        return subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from django.conf import settings; "
                    "print(settings.DATABASES['default']['ENGINE'])"
                ),
            ],
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )

    def test_postgres_database_url_sets_explicit_postgresql_engine(self):
        for scheme in ("postgres", "postgresql"):
            with self.subTest(scheme=scheme):
                result = self.run_settings_import(
                    f"{scheme}://db-user:test-password@db-host:5432/home_nest"
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    result.stdout.strip(),
                    "django.db.backends.postgresql",
                )
                self.assertNotIn("test-password", result.stdout + result.stderr)

    def test_missing_database_url_fails_with_clear_safe_error(self):
        result = self.run_settings_import("")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "DATABASE_URL is required in production",
            result.stderr,
        )
        self.assertNotIn("test-password", result.stderr)

    def test_non_postgres_database_url_fails_with_clear_safe_error(self):
        result = self.run_settings_import(
            "mysql://db-user:test-password@db-host:3306/home_nest"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL is invalid", result.stderr)
        self.assertNotIn("test-password", result.stderr)

    def test_management_command_uses_project_settings_when_env_is_overridden(self):
        env = os.environ.copy()
        for name in (
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
        ):
            env.pop(name, None)
        env.update(
            {
                "SECRET_KEY": "settings-test-key",
                "DEBUG": "False",
                "CLOUDINARY_URL": (
                    "cloudinary://test-key:test-secret@example-cloud"
                ),
                "DATABASE_URL": (
                    "postgresql://db-user:test-password@db-host:5432/home_nest"
                ),
                "DJANGO_SETTINGS_MODULE": "django.conf.global_settings",
            }
        )
        result = subprocess.run(
            [sys.executable, "manage.py", "check"],
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("System check identified no issues", result.stdout)
        self.assertNotIn("test-password", result.stdout + result.stderr)
