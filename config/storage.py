import posixpath

import cloudinary
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.uploadedfile import UploadedFile


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
            public_id = name[len(self.property_prefix):]
            public_id, extension = posixpath.splitext(public_id)
            if extension.lower() in self.image_extensions:
                return public_id
            return public_id + extension
        return None

    def _save(self, name, content):
        name = self._normalise_name(name)
        if not name.startswith(self.property_prefix):
            return super()._save(name, content)

        upload_name = name[len(self.property_prefix):]
        content = UploadedFile(content, upload_name)
        response = self._upload(upload_name, content)
        return f"{self.property_prefix}{response['public_id']}"

    def _get_url(self, name):
        public_id = self._property_public_id(name)
        if public_id is None:
            return super()._get_url(name)

        resource_type = self._get_resource_type(name)
        return cloudinary.CloudinaryResource(
            public_id,
            default_resource_type=resource_type,
        ).url

    def delete(self, name):
        public_id = self._property_public_id(name)
        return super().delete(public_id if public_id is not None else name)
