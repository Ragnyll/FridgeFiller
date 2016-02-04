# urls for the list application

from django.conf.urls import url
from . import views
from views import test

urlpatterns = [
    url(r'^$', views.disp_info, name='disp_info'),
    url(r'^test', test.as_view()),
]
