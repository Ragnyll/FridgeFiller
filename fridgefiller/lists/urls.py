# urls for the list application

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.disp_info, name='disp_info'),
]
