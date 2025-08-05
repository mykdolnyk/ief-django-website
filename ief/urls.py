from django.contrib import admin
from django.urls import include, path
import users.views as userviews
import blogs.views as blogviews
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_not_required
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', blogviews.index_page, name='index_page'),
    path('admin/login/', userviews.login_page, name='admin_login_page'),
    path('admin/', admin.site.urls),
    path('mediafiles/<path:filename>', blogviews.mediafiles_proxy, name='mediafiles_proxy'),
    path('user/', include('users.urls')),
    path('blog/', include('blogs.urls')),
    path('media/', blogviews.AllMediaList.as_view(), name='all_media_list'),
    path('media/<int:pk>/', userviews.UserMediaDetail.as_view(), name='media_detail'),
    path('timeline/', userviews.timeline_page, name='user_timeline'),
    path("notifications/", userviews.user_notification_list, name="user_notification_list"),
    
    path('login/', userviews.login_page, name=settings.LOGIN_PAGE_NAME),
    path('register/', userviews.register_page, name='register_page'),
    path('logout/', userviews.logout_page, name='logout_page'),
    path('reset_password/', userviews.PasswordReset.as_view(), name='reset_password'),
    path('reset_password_confirm/<uidb64>/<token>/', login_not_required(userviews.PasswordResetConfirm.as_view()), name='reset_password_confirm'),

    path('about/', blogviews.AboutPage.as_view(), name='about_page'),
    path('legal/', cache_page(3600)(login_not_required(TemplateView.as_view(template_name='blogs/legal.html'))), name='legal_page'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path("ckeditor5/", include('django_ckeditor_5.urls'))]

handler404 = 'blogs.views.handle_404'
handler500 = 'blogs.views.handle_500'
handler403 = 'blogs.views.handle_403'
handler400 = 'blogs.views.handle_400'
