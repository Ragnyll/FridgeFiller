# urls for the list application

from django.conf.urls import url
from . import views
from views import *

urlpatterns = [
    # List URLs
    url(r'^$', ListsView.as_view(), name="lists"),
    url(r'^(?P<list_id>\d+)', ListView.as_view()),
    url(r'^new/$', NewListView.as_view(), name="new-list"),
    url(r'^edit/(?P<list_id>\d+)', EditListView.as_view()),
    url(r'^new/item/', NewItemView.as_view(), name="new-item"),
    url(r'^remove/item/', RemoveItemFromListView.as_view(), name="remove-item"),
    url(r'^delete/list/', DeleteListView.as_view(), name="delete-list"),

    # Walmart APIs
    url(r'^walapi1', item_detail, name="item_detail"),
    url(r'^walapi2', upc, name="upc_search"),
    
    # Print URLs
    url(r'^print/', PrintListView.as_view(), name="print-list"),
    url(r'^printm/(?P<list_id>\d+)', PrintListMiniView.as_view(), name="print-m-list"),
]
