from django.contrib import admin
from . import models

    
class SectionAdmin(admin.ModelAdmin):
    model = models.Section
    

class BlogAdmin(admin.ModelAdmin):
    model = models.Blog
    list_display = ('title', 'slug')
    class Media:
        css = {'all': ('css/ckeditor5.css',)}

class AdminMessageAdmin(admin.ModelAdmin):
    model = models.AdminMessage
    class Media:
        css = {'all': ('css/ckeditor5.css',)}


admin.site.register(models.Section, SectionAdmin)

admin.site.register(models.Blog, BlogAdmin)

admin.site.register(models.AdminMessage, AdminMessageAdmin)
