from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os


def _resolve_media_storage():
    """Return a FileSystemStorage that writes to a writable media root.

    Prefers env MEDIA_ROOT, then settings.MEDIA_ROOT if writable,
    otherwise falls back to /tmp/media (writable on many PaaS).
    """
    media_root = os.environ.get('MEDIA_ROOT') or getattr(settings, 'MEDIA_ROOT', None)
    if media_root:
        try:
            os.makedirs(media_root, exist_ok=True)
            test_path = os.path.join(media_root, '.write-test')
            with open(test_path, 'wb') as f:
                f.write(b'1')
            os.remove(test_path)
        except Exception:
            media_root = '/tmp/media'
    else:
        media_root = '/tmp/media'
    try:
        os.makedirs(media_root, exist_ok=True)
    except Exception:
        pass
    base_url = getattr(settings, 'MEDIA_URL', '/media/')
    return FileSystemStorage(location=media_root, base_url=base_url)


_profile_media_storage = _resolve_media_storage()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics', storage=_profile_media_storage)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image only if the file exists (skip missing defaults)
        if self.avatar and os.path.isfile(getattr(self.avatar, 'path', '')):
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                # Silently skip resize if file cannot be opened
                pass
