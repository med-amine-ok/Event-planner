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

        candidate_roots = []
        # 1) settings.MEDIA_ROOT
        if getattr(settings, 'MEDIA_ROOT', None):
            candidate_roots.append(settings.MEDIA_ROOT)
        # 2) Env-provided MEDIA_ROOT or /tmp/media (writable on many PaaS)
        env_media_root = os.environ.get('MEDIA_ROOT')
        if env_media_root:
            candidate_roots.append(env_media_root)
        candidate_roots.append('/tmp/media')
        # 3) Repo media folder (read-only)
        base_dir = getattr(settings, 'BASE_DIR', None)
        if base_dir:
            candidate_roots.append(os.path.join(str(base_dir), 'media'))

        # Try to serve from the first existing file
        for root in candidate_roots:
            file_path = os.path.join(root, remapped_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(open(file_path, 'rb'))

        # As a fallback, try the original path across roots if a remap was applied
        if remapped_path != path:
            for root in candidate_roots:
                original_file_path = os.path.join(root, path)
                if os.path.exists(original_file_path) and os.path.isfile(original_file_path):
                    return FileResponse(open(original_file_path, 'rb'))

        raise Http404("Media file not found")
