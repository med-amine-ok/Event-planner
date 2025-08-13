import io
import mimetypes
import posixpath
import secrets
from typing import IO, Optional

from django.core.files.base import ContentFile, File
from django.core.files.storage import Storage
from django.utils._os import safe_join

from .models import StoredFile


class DatabaseStorage(Storage):
    """Django storage backend that saves files in the database.

    Generates opaque keys under provided location and serves through a custom view.
    """

    def __init__(self, location: str = 'uploads', base_url: Optional[str] = None):
        self.location = location.strip('/')
        # base_url should point to a view that can retrieve by key
        self.base_url = base_url or f"/db-media/"

    # Path helpers
    def _full_key(self, name: str) -> str:
        name = name.strip('/')
        return posixpath.join(self.location, name) if self.location else name

    def _generate_name(self, name: str) -> str:
        # Keep extension if present
        ext = ''
        if '.' in name:
            ext = '.' + name.split('.')[-1]
        return self._full_key(secrets.token_urlsafe(16) + ext)

    # Storage API
    def _open(self, name: str, mode: str = 'rb') -> File:
        key = self._full_key(name)
        try:
            obj = StoredFile.objects.get(key=key)
        except StoredFile.DoesNotExist:
            raise FileNotFoundError(name)
        return File(io.BytesIO(bytes(obj.data)), name=key)

    def _save(self, name: str, content: IO[bytes]) -> str:
        # Read bytes
        if hasattr(content, 'read'):
            data = content.read()
        else:
            data = bytes(content)

        # Determine final key
        key = self._generate_name(name or 'file')

        # Determine content type
        content_type: Optional[str] = None
        ct_attr = getattr(content, 'content_type', None)
        if isinstance(ct_attr, str) and ct_attr:
            content_type = ct_attr
        else:
            guessed, _ = mimetypes.guess_type(key)
            content_type = guessed or 'application/octet-stream'

        StoredFile.objects.create(key=key, data=data, content_type=content_type)
        return key

    def delete(self, name: str) -> None:
        key = self._full_key(name)
        StoredFile.objects.filter(key=key).delete()

    def exists(self, name: str) -> bool:
        key = self._full_key(name)
        return StoredFile.objects.filter(key=key).exists()

    def size(self, name: str) -> int:
        key = self._full_key(name)
        try:
            obj = StoredFile.objects.only('data').get(key=key)
        except StoredFile.DoesNotExist:
            raise FileNotFoundError(name)
        return len(obj.data)

    def url(self, name: str) -> str:
        key = self._full_key(name)
        return f"{self.base_url}{key}"

    def get_available_name(self, name: str, max_length: Optional[int] = None) -> str:
        # Keys are unique; we always generate a new one
        return self._generate_name(name)


