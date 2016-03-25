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
    url(r'^party/remove', RemovePartyView.as_view(), name="remove-party"),
    #url(r'^party/invite', InvitetoParty.as_view(), name="invite-to-party"),
    url(r'^party/create', CreateParty.as_view(), name="create-party"),
    url(r'^party/addlist', AddPartyList.as_view(), name="add-group-list"),
    url(r'^invitations/$', InvitationListView.as_view(), name='invitation_list'),
    url(r'^invitations/invite/$', InvitationCreateView.as_view(), name='invitation_create'),
    url(r'^invitations/(?P<pk>\d+)/$', InvitationDetailView.as_view(), name='invitation_detail'),
    url(r'^invitations/(?P<pk>\d+)/accept$', InvitationAcceptView.as_view(), name='invitation_accept'),
    url(r'^invitations/(?P<pk>\d+)/decline$', InvitationDeclineView.as_view(), name='invitation_decline')
    
]
