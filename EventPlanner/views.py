import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View


class MediaServeView(View):
    """Custom view to serve media files in production"""
    
    def get(self, request, path):
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(open(file_path, 'rb'))
        else:
            raise Http404("Media file not found")
