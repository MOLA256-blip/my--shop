"""
Custom middleware for serving media files in production
"""
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.utils.deprecation import MiddlewareMixin


class MediaFileMiddleware(MiddlewareMixin):
    """
    Middleware to serve media files in production when WhiteNoise can't handle them.
    This is a simple solution for small to medium projects on Render.
    For larger projects, consider using cloud storage (S3, Cloudinary, etc.)
    """
    
    def process_request(self, request):
        # Only handle media file requests
        if request.path.startswith(settings.MEDIA_URL):
            # Get the file path relative to MEDIA_ROOT
            relative_path = request.path[len(settings.MEDIA_URL):]
            file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            # Check if file exists
            if os.path.isfile(file_path):
                # Determine content type based on file extension
                content_type = self._get_content_type(file_path)
                
                # Return the file
                try:
                    return FileResponse(open(file_path, 'rb'), content_type=content_type)
                except Exception:
                    raise Http404("Media file not found")
            else:
                raise Http404("Media file not found")
        
        return None
    
    def _get_content_type(self, file_path):
        """Determine content type based on file extension"""
        extension = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.bmp': 'image/bmp',
            '.ico': 'image/x-icon',
        }
        return content_types.get(extension, 'application/octet-stream')
