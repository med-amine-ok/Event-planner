import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View


class MediaServeView(View):
    """Custom view to serve media files in production.

    Also remaps legacy default filenames to their correct subpaths so that
    old URLs keep working after changing default storage paths.
    """

    LEGACY_MAP = {
        # Old profile default -> new location
        'default.jpg': 'profile_pics/default.jpg',
        # Old event default -> new location/filename
        'event_default.jpg': 'event_pics/event_default.png',
    }

    def get(self, request, path):
        # Remap legacy paths if requested
        remapped_path = self.LEGACY_MAP.get(path, path)
        file_path = os.path.join(settings.MEDIA_ROOT, remapped_path)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(open(file_path, 'rb'))
        else:
            # As a fallback, try the original path if a remap was applied
            if remapped_path != path:
                original_file_path = os.path.join(settings.MEDIA_ROOT, path)
                if os.path.exists(original_file_path) and os.path.isfile(original_file_path):
                    return FileResponse(open(original_file_path, 'rb'))
            raise Http404("Media file not found")
