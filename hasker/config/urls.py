from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.documentation import include_docs_urls

from hasker.core import views as core_views


urlpatterns = [
    path('', include('hasker.account.urls')),
    path('', include('hasker.question.urls')),
    path('api/v1/', include('hasker.api.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('403/', core_views.handler403),
        path('404/', core_views.handler404),
        path('500/', core_views.handler500),
    ] + urlpatterns

handler403 = core_views.handler403
handler404 = core_views.handler404
handler500 = core_views.handler500