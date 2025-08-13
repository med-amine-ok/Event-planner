from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize only when stored on local filesystem
        try:
            if self.avatar and isinstance(self.avatar.storage, FileSystemStorage):
                image_path = self.avatar.path
                if os.path.isfile(image_path):
                    img = Image.open(image_path)
                    if img.height > 300 or img.width > 300:
                        output_size = (300, 300)
                        img.thumbnail(output_size)
                        img.save(image_path)
        except Exception:
            # Silently skip resize if storage has no path or image cannot be processed
            pass
