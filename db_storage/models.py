from django.db import models


class StoredFile(models.Model):
    """Binary file stored in database.

    Files are keyed by a generated path-like key so Django fields can reference them.
    """

    key = models.CharField(max_length=255, unique=True)
    content_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.BinaryField()

    def __str__(self) -> str:
        return self.key

