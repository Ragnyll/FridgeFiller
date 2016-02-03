from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('lists.urls')),

    # Django AllAuth
    url(r'^accounts/logout/$', logout_then_login),
    url(r'^accounts/', include('allauth.urls')),
]
