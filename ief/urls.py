from django.contrib import admin
from django.urls import include, path
import users.views as userviews
import blogs.views as blogviews
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    
    path('', blogviews.index_page, name='index_page'),
    
    path('login/', userviews.login_page, name=settings.LOGIN_PAGE_NAME),
    path('register/', userviews.register_page, name='register_page'),
    path('logout/', userviews.logout_page, name='logout_page'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
