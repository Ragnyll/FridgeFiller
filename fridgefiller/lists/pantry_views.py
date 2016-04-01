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

class PantryView(TemplateView):
    """
    This view displays the user's pantry
    """
    template_name = "lists/pantry.html"

    def get_context_data(self, **kwargs):
        context = super(PantryView, self).get_context_data(**kwargs)

        user = UserProfile.objects.get(user=self.request.user)

        party = Party.objects.get(name=user.name+"'s Personal Party")
        pantry = Pantry.objects.get(party=party)

        context['party'] = party
        context['pantry'] = pantry
        context['pantry_items'] = pantry.items.all()
        return context

class PartyPantryView(TemplateView):
    """
    This view displays the pantry for a party
    """

    template_name = "lists/pantry.html"

    def dispatch(self, *args, **kwargs):
        user = self.request.user.profile
        party_id = kwargs['party_id']

        try:
            party_obj = Party.objects.get(id=party_id)
            party_users = party_obj.users.all()
            party_owner = party_obj.owner
        except :
            return redirect("/")

        # Only allow access to page if user is owner or user of party
        if party_owner == user or user in party_users:
            return super(PartyPantryView, self).dispatch(*args, **kwargs)
        else:
            messages.add_message(self.request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>:&nbsp;&nbsp;Sorry, you aren't allowed to access that pantry." + ALERT_CLOSE)
            return redirect("/")


    def get_context_data(self, **kwargs):
        context = super(PartyPantryView, self).get_context_data(**kwargs)

        party_id = kwargs['party_id']
        party = Party.objects.get(id=party_id)
        pantry = Pantry.objects.get(party=party)

        context['party'] = party
        context['pantry'] = pantry
        context['pantry_items'] = pantry.items.all()
        return context

class AddItemToPantryView(View):
    """
    This view adds an item from a shopping list to a user's Pantry
    """

    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('add-item-to-pantry-name', False).title()
        item_description = request.POST.get('add-item-to-pantry-desc', False).capitalize()
        list_id = request.POST.get('list_id', False)
        from_url = request.POST.get('from_url', False)
        party_id = request.POST.get('party-id', False)

        if from_url == "/pantry/" or from_url == "/pantry/" + str(party_id) + "/":
            list_id = str(-1)

        # Don't allow blank item names
        if item_name == "":
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  You must supply a name to add an item to your pantry!" + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect(from_url + "#" + list_id)

        try:
            item_detail_obj, c = ItemDetail.objects.get_or_create(name=item_name,
                                                                  description=item_description)

            # User's pantry object
            user_userprofile = UserProfile.objects.get(name=request.user.username)
            user_party = Party.objects.get(id=party_id)
            pantry_obj = Pantry.objects.get(party=user_party)

            # don't add duplicate items
            if item_detail_obj.name in [x.name for x in pantry_obj.items.all()]:
                messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  That item already exists in your pantry!" + ALERT_CLOSE, extra_tags=int(list_id))
                return redirect(from_url + "#" + list_id)

            pantry_obj.items.add(item_detail_obj)

            # successful, return to lists page with success message
            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS:&nbsp;" + str(item_name) + "</strong>&nbsp;&nbsp;has been added to your pantry!" + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect(from_url + "#" + list_id)

        # Something went wront creating the Item Detail, give them an error
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  Unable to create ItemDetail for that item.  Please let a developer know!" + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect(from_url + "#" + list_id)


class EditItemInPantryView(View):
    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('edit-item-in-pantry-name', False)
        item_description = request.POST.get('edit-item-in-pantry-desc', False)
        amount = request.POST.get('edit-item-in-pantry-stock', False)
        units = request.POST.get('edit-item-in-pantry-unit', False)
        cost = request.POST.get('edit-item-in-pantry-cost', False)
        location_purchased = request.POST.get('edit-item-in-pantry-location-purchased', False)
        list_id = request.POST.get('list_id', False)
        from_url = request.POST.get('from_url', False)
        party_id = request.POST.get('party-id', False)

        date_pattern = re.compile('(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.](19|20)\d\d')

        last_purchased_str = request.POST.get('edit-item-in-pantry-last-purchased', False)
        expiration_date_str = request.POST.get('edit-item-in-pantry-expiration-date', False)


        if from_url == "/pantry/" or from_url == "/pantry/" + str(party_id) + "/":
            list_id = str(-1)

        # convert empty values to zero for non-required data
        if amount == "":
            amount = float(0)
        else:
            amount = float(amount)

        if cost == "" or cost == "---":
            cost = float(0)
        else:
            cost = float(cost)


        # Don't let user supply zero amount
        if amount == float(0):
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;: You must fill out the amount field to add <strong>&nbsp;" + item_name + "</strong>&nbsp;&nbsp;to your pantry.  Try again!" + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect(from_url + "#" + list_id)


        # If last_purchased and expiration_date are proper dates, make datetime objects for them
        # else, create minimum datetime objects
        if date_pattern.match(last_purchased_str):
            month, day, year = map(int,last_purchased_str.split("/"))
            last_purchased = datetime(month=month, day=day, year=year)
        else:
            last_purchased = datetime.min

        if date_pattern.match(expiration_date_str):
            month, day, year = map(int,expiration_date_str.split("/"))
            expiration_date = datetime(month=month, day=day, year=year)
        else:
            expiration_date = datetime.min

        # Get ItemDetail object from pantry and update the values
        try:
            # User's pantry object
            user_userprofile = UserProfile.objects.get(name=request.user.username)
            user_party = Party.objects.get(id=party_id)
            pantry_obj = Pantry.objects.get(party=user_party)
            pantry_items = pantry_obj.items.all()

            item_detail_obj = pantry_items.filter(name=item_name, description=item_description)

            item_detail_obj.update(name=item_name,
                                   description=item_description,
                                   cost=cost,
                                   last_purchased=last_purchased,
                                   location_purchased=location_purchased,
                                   barcode=-1,
                                   unit=units,
                                   amount=amount,
                                   expiration_date=expiration_date)


            # successful, return to lists page with success message
            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;:  " + str(amount) + " " + str(units) + " of " + str(item_name) + " has been added to your pantry!" + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect(from_url + "#" + list_id)

        # Something went wront creating the Item Detail, give them an error
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  Unable to update the values for <strong>&nbsp;" + item_name + "</strong>&nbsp;.  Please let a developer know!" + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect(from_url + "#" + list_id)


class RemoveItemFromPantryView(View):
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id', False)
        from_url = request.POST.get('from_url', False)
        party_id = request.POST.get('party-id', False)

        # Get the user's pantry object
        party_obj = Party.objects.get(id=party_id)
        pantry_obj = Pantry.objects.get(party=party_obj)
        item_obj = pantry_obj.items.get(id=item_id)

        # remove the item from the pantry
        try:
            pantry_obj.items.remove(item_obj)

            if 'Personal' in party_obj.name:
                messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;:  Removed <strong>&nbsp;" + item_obj.name + "</strong>&nbsp; from " + pantry_obj.party.owner.name + "'s pantry." + ALERT_CLOSE, extra_tags=int(item_id))
            else:
                messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;:  Removed <strong>&nbsp;" + item_obj.name + "</strong>&nbsp; from " + pantry_obj.party.name + "'s pantry." + ALERT_CLOSE, extra_tags=int(item_id))

            return redirect(from_url + "#" + item_id)
        except:
            if 'Personal' in party_obj.name:
                messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  Unable to remove <strong>&nbsp;" + item_obj.name + "</strong>&nbsp; from " + pantry_obj.party.owner.name + "'s pantry.  Please let a developer know!" + ALERT_CLOSE, extra_tags=int(item_id))
            else:
                messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  Unable to remove <strong>&nbsp;" + item_obj.name + "</strong>&nbsp; from " + pantry_obj.party.name + "'s pantry.  Please let a developer know!" + ALERT_CLOSE, extra_tags=int(item_id))
            return redirect(from_url + "#" + item_id)
