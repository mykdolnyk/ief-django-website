from django.contrib import admin
from . import models
# Register your models here.

    
class SectionAdmin(admin.ModelAdmin):
    model = models.Section
    


class BlogAdmin(admin.ModelAdmin):
    model = models.Blog
    list_display = ('title', 'slug')


admin.site.register(models.Section, SectionAdmin)

admin.site.register(models.Blog, BlogAdmin)