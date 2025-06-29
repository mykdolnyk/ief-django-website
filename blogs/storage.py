from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os
from urllib.parse import urljoin
from uuid import uuid4


class BlogUploadsStorage(FileSystemStorage):
    """"""
    location = os.path.join(settings.MEDIA_ROOT, 'blog_uploads')
    base_url = urljoin(settings.MEDIA_URL, 'blog_uploads/')
    
    def save(self, name, content, max_length = None):
        name = str(uuid4()) + '.' + name.split('.')[-1]
        # Generate a random UUID and add the file extension in the end
        
        name = super().save(name, content, max_length)
        
        return name
