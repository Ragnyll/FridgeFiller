# urls for the list application

from django.conf.urls import url
from . import views
from views import *

urlpatterns = [
    url(r'^$', ListsView.as_view(), name="lists"),
    url(r'^(?P<list_id>\d+)', ListView.as_view()),
    url(r'^new$', NewListView.as_view(), name="new-list"),
    url(r'^edit/(?P<list_id>\d+)', EditListView.as_view()),
    url(r'^new/item/', NewItemView.as_view(), name="new-item"),
    url(r'^remove/item/', RemoveItemFromListView.as_view(), name="remove-item"),
    url(r'^parties/', PartiesView.as_view(), name="parties"),
    url(r'^party/(?P<party_id>\d+)', PartyView.as_view()),
    url(r'^party/leave', LeavePartyView.as_view(), name="leave-party"),
    url(r'^party/invite', InvitetoParty.as_view(), name="invite-to-party"),
    url(r'^party/create', CreateParty.as_view(), name="create-party"),
    url(r'^party/addlist', AddPartyList.as_view(), name="add-group-list")
]
