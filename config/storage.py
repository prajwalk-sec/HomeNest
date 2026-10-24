import logging
import posixpath
import traceback

import cloudinary
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


class HomeNestMediaCloudinaryStorage(MediaCloudinaryStorage):
    property_prefix = "properties/"
    image_extensions = {
        ".avif",
        ".bmp",
        ".gif",
        ".heic",
        ".heif",
        ".jpeg",
        ".jpg",
        ".png",
        ".svg",
        ".tif",
        ".tiff",
        ".webp",
    }

    def _property_public_id(self, name):
        name = self._normalise_name(name)
        if name.startswith(self.property_prefix):
            asset_path = name[len(self.property_prefix):]
            version, separator, public_id = asset_path.partition("/")
            if separator and version.startswith("v") and version[1:].isdigit():
                return public_id

            public_id = asset_path
            public_id, extension = posixpath.splitext(public_id)
            if extension.lower() in self.image_extensions:
                return public_id
            return public_id + extension
        return None

    def _property_version(self, name):
        name = self._normalise_name(name)
        if not name.startswith(self.property_prefix):
            return None

        version, separator, _ = name[len(self.property_prefix):].partition("/")
        if separator and version.startswith("v") and version[1:].isdigit():
            return int(version[1:])
        return None

    def _save(self, name, content):
        name = self._normalise_name(name)
        if not name.startswith(self.property_prefix):
            return super()._save(name, content)

        upload_name = name[len(self.property_prefix):]
        content = UploadedFile(content, upload_name)
        try:
            response = self._upload(upload_name, content)
            public_id = response["public_id"]
            version = int(response["version"])
            if not public_id:
                raise CloudinaryError(
                    "Cloudinary upload response did not include a public ID."
                )
        except Exception as exc:
            credentials = cloudinary.config()
            logger.error(
                "Cloudinary property upload failed "
                "(exception_type=%s, cloud_name_configured=%s, "
                "api_key_configured=%s, api_secret_configured=%s); "
                "traceback follows:\n%s",
                type(exc).__name__,
                bool(credentials.cloud_name),
                bool(credentials.api_key),
                bool(credentials.api_secret),
                "".join(traceback.format_tb(exc.__traceback__)),
            )
            raise

        return f"{self.property_prefix}v{version}/{public_id}"

    def _get_url(self, name):
        public_id = self._property_public_id(name)
        if public_id is None:
            return super()._get_url(name)

        resource_type = self._get_resource_type(name)
        return cloudinary.CloudinaryResource(
            public_id,
            version=self._property_version(name),
            default_resource_type=resource_type,
        ).url

    def delete(self, name):
        public_id = self._property_public_id(name)
        return super().delete(public_id if public_id is not None else name)
