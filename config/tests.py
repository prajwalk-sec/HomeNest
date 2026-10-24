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
            "CLOUDINARY_CONFIG_SOURCE",
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


    def test_postgres_database_url_sets_production_ssl(self):
        env = os.environ.copy()
        for name in (
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
            "CLOUDINARY_CONFIG_SOURCE",
        ):
            env.pop(name, None)
        env.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "SECRET_KEY": "settings-test-key",
                "DEBUG": "False",
                "CLOUDINARY_URL": (
                    "cloudinary://"
                    + "test-key"
                    + ":"
                    + "test-secret"
                    + "@example-cloud"
                ),
                "DATABASE_URL": (
                    "postgresql://"
                    + "db-user"
                    + ":"
                    + "test-password"
                    + "@db-host:5432/home_nest"
                ),
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from django.conf import settings; "
                    "database = settings.DATABASES['default']; "
                    "print(database['ENGINE']); "
                    "print(database.get('OPTIONS', {}).get('sslmode'))"
                ),
            ],
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            ["django.db.backends.postgresql", "require"],
        )
        self.assertNotIn("test-password", result.stdout + result.stderr)


class CloudinarySettingsTests(SimpleTestCase):
    cloudinary_url = (
        "cloudinary://"
        + "url-key"
        + ":"
        + "url-secret"
        + "@url-cloud"
    )

    def run_settings_import(self, source, cloudinary_url, individual):
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "SECRET_KEY": "settings-test-key",
                "DEBUG": "False",
                "DATABASE_URL": (
                    "postgresql://db-user:test-password@db-host:5432/home_nest"
                ),
                "CLOUDINARY_URL": cloudinary_url,
                "CLOUDINARY_CONFIG_SOURCE": source,
                "CLOUDINARY_CLOUD_NAME": individual.get(
                    "CLOUDINARY_CLOUD_NAME", ""
                ),
                "CLOUDINARY_API_KEY": individual.get(
                    "CLOUDINARY_API_KEY", ""
                ),
                "CLOUDINARY_API_SECRET": individual.get(
                    "CLOUDINARY_API_SECRET", ""
                ),
            }
        )
        return subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from django.conf import settings; "
                    "source = settings.CLOUDINARY_CONFIG_SOURCE; "
                    "import cloudinary; "
                    "config = cloudinary.config(); "
                    "print(source); "
                    "print(config.cloud_name == 'url-cloud'); "
                    "print(config.api_key == 'url-key'); "
                    "print(config.api_secret == 'url-secret'); "
                    "print(config.cloud_name == 'individual-cloud'); "
                    "print(config.api_key == 'individual-key'); "
                    "print(config.api_secret == 'individual-secret')"
                ),
            ],
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )

    def test_explicit_url_selection_ignores_individual_credentials(self):
        result = self.run_settings_import(
            "url",
            self.cloudinary_url,
            {
                "CLOUDINARY_CLOUD_NAME": "individual-cloud",
                "CLOUDINARY_API_KEY": "individual-key",
                "CLOUDINARY_API_SECRET": "individual-secret",
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            ["url", "True", "True", "True", "False", "False", "False"],
        )
        self.assertNotIn("url-secret", result.stdout + result.stderr)
        self.assertNotIn("individual-secret", result.stdout + result.stderr)

    def test_explicit_individual_selection_ignores_cloudinary_url(self):
        result = self.run_settings_import(
            "individual",
            self.cloudinary_url,
            {
                "CLOUDINARY_CLOUD_NAME": "individual-cloud",
                "CLOUDINARY_API_KEY": "individual-key",
                "CLOUDINARY_API_SECRET": "individual-secret",
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "individual",
                "False",
                "False",
                "False",
                "True",
                "True",
                "True",
            ],
        )
        self.assertNotIn("url-secret", result.stdout + result.stderr)
        self.assertNotIn("individual-secret", result.stdout + result.stderr)

    def test_both_methods_require_explicit_selection(self):
        result = self.run_settings_import(
            "",
            self.cloudinary_url,
            {
                "CLOUDINARY_CLOUD_NAME": "individual-cloud",
                "CLOUDINARY_API_KEY": "individual-key",
                "CLOUDINARY_API_SECRET": "individual-secret",
            },
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Set CLOUDINARY_CONFIG_SOURCE=url or "
            "CLOUDINARY_CONFIG_SOURCE=individual",
            result.stderr,
        )
        self.assertNotIn("url-secret", result.stdout + result.stderr)
        self.assertNotIn("individual-secret", result.stdout + result.stderr)

    def test_incomplete_selected_individual_credentials_fail_safely(self):
        result = self.run_settings_import(
            "individual",
            "",
            {"CLOUDINARY_CLOUD_NAME": "individual-cloud"},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "CLOUDINARY_CONFIG_SOURCE=individual requires all of",
            result.stderr,
        )
        self.assertNotIn("individual-cloud", result.stdout + result.stderr)

class DatabaseSettingsValidationTests(SimpleTestCase):
    def run_settings_import(self, database_url):
        env = os.environ.copy()
        for name in (
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
            "CLOUDINARY_CONFIG_SOURCE",
        ):
            env.pop(name, None)
        env.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "SECRET_KEY": "settings-test-key",
                "DEBUG": "False",
                "CLOUDINARY_URL": (
                    "cloudinary://"
                    + "test-key"
                    + ":"
                    + "test-secret"
                    + "@example-cloud"
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

    def test_postgres_database_url_without_host_or_database_fails_safely(self):
        for database_url in (
            "postgresql:///home_nest",
            "postgresql://db-host",
        ):
            with self.subTest(database_url=database_url):
                result = self.run_settings_import(database_url)

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
