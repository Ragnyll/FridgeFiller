# urls for the list application

from django.conf.urls import url
from . import views
from views import ListsView, ListView, NewListView, EditListView

urlpatterns = [
    url(r'^$', ListsView.as_view(), name="lists"),
    url(r'^(?P<list_id>\d+)', ListView.as_view()),
    url(r'^new', NewListView.as_view(), name="new-list"),
    url(r'^edit/(?P<list_id>\d+)', EditListView.as_view()),
]
