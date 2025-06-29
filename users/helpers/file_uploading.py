import os
import uuid


def profile_media_upload(instance, filename: str):
    path = "users/profile_media/"
    
    name = str(uuid.uuid4()) + '.' + filename.split('.')[-1]
    
    return os.path.join(path, name)