from django.contrib import admin
from . import models
from django.utils.html import strip_tags


class SectionAdmin(admin.ModelAdmin):
    model = models.Section
    list_display = ('name', 'blog_count')
    
    def blog_count(self, obj):
        return obj.blogs.count()
    

class BlogAdmin(admin.ModelAdmin):
    model = models.Blog
    list_display = ('title', 'section', 'author', 'like_count')
    list_filter = ('section', 'author')
    
    class Media:
        css = {'all': ('css/ckeditor5.css',)}
        
    def like_count(self, obj):
        return obj.likes.count()


class AdminMessageAdmin(admin.ModelAdmin):
    model = models.AdminMessage
    list_display = ('stripped_text', 'created_at', 'is_pinned')
    
    class Media:
        css = {'all': ('css/ckeditor5.css',)}
        
    def stripped_text(self, obj):
        return strip_tags(obj.text)


admin.site.register(models.Section, SectionAdmin)

admin.site.register(models.Blog, BlogAdmin)

admin.site.register(models.AdminMessage, AdminMessageAdmin)
