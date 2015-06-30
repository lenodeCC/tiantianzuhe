from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = patterns('',
    url(r'^createtoken/$', views.CreateToken.as_view()),
    url(r'^reg/$', views.Reg.as_view()),
    url(r'^login/$', views.Login.as_view()),

    url(r'^admin/', include(admin.site.urls)),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = format_suffix_patterns(urlpatterns)
