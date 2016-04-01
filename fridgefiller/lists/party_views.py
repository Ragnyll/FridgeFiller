from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.generic import TemplateView, UpdateView, View, DetailView, CreateView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from statuses import *
from datetime import datetime
import re
from .models import *


class PartyView(TemplateView):
    """
    This view displays a party with <party-id> and the party's users
    """
    template_name = "lists/party.html"

    def dispatch(self, *args, **kwargs):
        user = self.request.user.profile
        party_id = kwargs['party_id']

        # Get party object
        try:
            party_obj = Party.objects.get(id=party_id)
            party_users = party_obj.users.all()
            party_owner = party_obj.owner
        except :
            return redirect("/parties/")

        # Only allow access to page if user is owner or user of party
        if party_owner == user or user in party_users:
            return super(PartyView, self).dispatch(*args, **kwargs)
        else:
            return redirect("/parties/")


    def get_context_data(self, **kwargs):
        context = super(PartyView, self).get_context_data(**kwargs)

        party = Party.objects.get(id=kwargs['party_id'])
        user = UserProfile.objects.get(user=self.request.user)
        partylists = party.shoppinglists.all()

        context['party'] = party
        context['cuser'] = user
        context['party_users'] = party.users.all()
        context['party_lists'] = partylists
        context['user_lists'] = ShoppingList.objects.filter(owners__in=[user]).exclude(id__in=partylists.values_list('id'))
        context['party_pantry'] = Pantry.objects.filter(party__in=[party])
        context['personal_party'] = Party.objects.filter(name__contains='Personal Party').get(owner = user)
        return context

class LeavePartyView(View):
    """
    This view removes you from a party and redirects back to your parties page
    """

    def post(self, request, *args, **kwargs):
        party_id = request.POST.get('leave-group-id', False)

        party_obj = Party.objects.get(id=party_id)
        user = UserProfile.objects.get(user=self.request.user)

        # Shouldn't be able to leave party if you are the owner
        # Remove user from party
        if user == party_obj.owner:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;You cannot leave a group that you own." + ALERT_CLOSE)
            return redirect("/party/" + str(party_obj.id))

        try:
            party_obj.users.remove(user)
            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>:&nbsp;&nbsp;Left&nbsp;<strong>" + party_obj.name + "</strong>" + ALERT_CLOSE)
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;Unable to leave&nbsp;<strong>" + party_obj.name +"</strong>" + ALERT_CLOSE)

        return redirect("/parties")


class CreateParty(View):
    """
    This view contains logic to create a new group
    """
    template_name = 'lists/party/create.html'
    def post(self, request, *args, **kwargs):
        party_name = request.POST.get('group-name', False)
        party_owner = UserProfile.objects.get(user=self.request.user)

        if party_name == "":
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;You must provide a name for the group." + ALERT_CLOSE)
            return redirect('/parties')

        if Party.objects.filter(name=party_name).exists():
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;A group with that name already exists." + ALERT_CLOSE)
            return redirect('/parties')

        try:
            party_obj = Party(name=party_name, owner=party_owner)
            party_obj.save()
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;Could not create party." + ALERT_CLOSE)
            return redirect("/parties/")
        return redirect("/party/" + str(party_obj.id))

class AddPartyList(View):
    """
    This view contains logic to add an existing shopping list to a party
    """

    def post(self, request, *args, **kwargs):
        party_id = request.POST.get('party-id', False)
        party_obj = Party.objects.get(id=party_id)
        list_name = request.POST.get('add-list-select', False)

        # If user didn't select a list to add, yell at them
        if not list_name:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;You must select a list to add!" + ALERT_CLOSE)
            return redirect('/party/' + party_id)

        list_obj = ShoppingList.objects.get(name=list_name)


        try:
            party_obj.shoppinglists.add(list_obj)
            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>:&nbsp;&nbsp;added list&nbsp;<strong>" + list_obj.name + "</strong>&nbsp;to group&nbsp;<strong>" + party_obj.name + "</strong>" + ALERT_CLOSE)

        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;Could not add list to group&nbsp;<strong>" + list_obj.name + "</strong>" + ALERT_CLOSE)
            return redirect("/party/" + str(party_id))

        return redirect("/party/" + str(party_id))

class PartiesView(TemplateView):
    """
    This view displays a list of partys a user belongs too
    """
    template_name = "lists/parties.html"

    def get_context_data(self, **kwargs):
        context = super(PartiesView, self).get_context_data(**kwargs)

        user = UserProfile.objects.get(user=self.request.user)
        user_personal_party = Party.objects.get(name=user.name+"'s Personal Party")

        # All parties where the user is an owner, except their personal party
        user_owned_parties = Party.objects.filter(owner__in=[user]).exclude(id=user_personal_party.id)
        context['owned_parties'] = user_owned_parties

        # Parties where the user is a 'user' of the party
        #  -> user is in Party.users but not Party.owner
        user_parties = Party.objects.filter(users__in=[user]).exclude(owner__in=[user])
        context['user_parties'] = user_parties

        return context

class RemovePartyView(View):
    """
    This view contains logic to remove a group from existence.
    """
    template_name = 'lists/party/remove.html'

    def post(self, request, *args, **kwargs):
        party_id = request.POST.get('remove-group-id', False)
        party_obj = Party.objects.get(id=party_id)

        try:
            Party.objects.filter(id=party_id).delete()
            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>:&nbsp;&nbsp;deleted&nbsp;<strong>" + party_obj.name + "</strong>" + ALERT_CLOSE)
            return redirect("/parties/")

        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;Unable to delete <strong>" + party_obj.name + "</strong>." + ALERT_CLOSE)
            return redirect("/party/" + str(party_obj.id))
