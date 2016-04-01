from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout_then_login

from lists.views import *
from lists.invitation_views import *
from lists.pantry_views import *
from lists.party_views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # List App
    url(r'^lists/', include('lists.urls')),

    # User's pantry
    url(r'^pantry/$', PantryView.as_view(), name="pantry"),
    url(r'^pantry/add/item/', AddItemToPantryView.as_view(), name="add-item-to-pantry"),
    url(r'^pantry/edit/item/', EditItemInPantryView.as_view(), name="edit-item-in-pantry"),
    url(r'^pantry/remove/item/', RemoveItemFromPantryView.as_view(), name="remove-item-from-pantry"),

    # Home App
    url(r'^$', include('home.urls')),

    # Django AllAuth
    url(r'^accounts/logout/$', logout_then_login),
    url(r'^accounts/', include('allauth.urls')),

    # Party URLs
    url(r'^parties/', PartiesView.as_view(), name="parties"),
    url(r'^party/(?P<party_id>\d+)', PartyView.as_view(), name="party"),
    url(r'^party/leave', LeavePartyView.as_view(), name="leave-party"),
    url(r'^party/remove', RemovePartyView.as_view(), name="remove-party"),
    #url(r'^party/invite', InvitetoParty.as_view(), name="invite-to-party"),
    url(r'^party/create', CreateParty.as_view(), name="create-party"),
    url(r'^party/addlist', AddPartyList.as_view(), name="add-group-list"),
    url(r'^invitations/$', InvitationListView.as_view(), name='invitation_list'),
    url(r'^invitations/invite/$', InvitationCreateView.as_view(), name='invitation_create'),
    url(r'^invitations/(?P<pk>\d+)/$', InvitationDetailView.as_view(), name='invitation_detail'),
    url(r'^invitations/(?P<pk>\d+)/accept$', InvitationAcceptView.as_view(), name='invitation_accept'),
    url(r'^invitations/(?P<pk>\d+)/decline$', InvitationDeclineView.as_view(), name='invitation_decline'),
    url(r'^delete/list/', DeleteListView.as_view(), name="delete-list"),
]
