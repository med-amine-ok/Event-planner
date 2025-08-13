import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View

from .models import StoredFile


class DbMediaServeView(View):
    def get(self, request, path: str):
        # Try DB first
        try:
            obj = StoredFile.objects.get(key=path)
            return FileResponse(bytes(obj.data))
        except StoredFile.DoesNotExist:
            pass

        # Fallback to filesystem defaults under MEDIA_ROOT for legacy defaults
        # Strip optional leading folder such as 'uploads/'
        candidates = [path]
        if path.startswith('uploads/'):
            candidates.append(path[len('uploads/'):])

        for candidate in candidates:
            file_path = os.path.join(settings.MEDIA_ROOT, candidate)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(open(file_path, 'rb'))

        raise Http404("Media not found")


