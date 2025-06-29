
from users.models import UserProfile
from users.models import UserProfile
from users.helpers import mcuser
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.http import Http404


def update_pfp(profile: UserProfile, skip_rate_limit=False):    
    if not skip_rate_limit:
        # Check if the PFP was created and updated before...
        pfp_recently_updated = cache.has_key(f"pfp_recently_updated:{profile.user.username}")
        if pfp_recently_updated:
            return None # do nothing
    
    pfp = mcuser.create_pfp(profile.mcuuid)
    pfp = ContentFile(pfp)
    profile.pfp.save(name=f'{profile.slug}.png', content=pfp)
    
    cache.set(f"pfp_recently_updated:{profile.user.username}", True, 60) # Record the PFP Update


def get_userprofile_or_404(slug):
    try:
        profile = UserProfile.objects.get(slug=slug.lower())
    except UserProfile.DoesNotExist:
        raise Http404()
    
    return profile
