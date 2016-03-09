from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView, UpdateView, View
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from datetime import datetime

import re

from .models import *

def disp_info(request):
    users = UserProfile.objects.all()
    parties = Party.objects.all()
    shoppinglists = ShoppingList.objects.all()

    return render(request, 'lists/disp_info.html',{'users': users})


class ListsView(TemplateView):
    """
    This view displays all shopping lists that a user owns
    """
    template_name = "lists/lists.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Ensures that only authenticated users can access the view.
        """
        return super(ListsView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(ListsView, self).get_context_data(**kwargs)

        user = UserProfile.objects.get(user=self.request.user)
        user_party = Party.objects.get(owner=user)
        user_pantry = Pantry.objects.get(party=user_party)

        user_pantry_items = user_pantry.items.all()

        user_pantry_item_names = [x.name for x in user_pantry_items]

        context['user_pantry_items'] = user_pantry_items
        context['user_pantry_item_names'] = user_pantry_item_names
        context['user_pantry'] = user_pantry
        context['user_shopping_lists'] = ShoppingList.objects.filter(owners__in=[user])

        return context


class ListView(TemplateView):
    """
    This view displays a singular list with id <list_id> and the items in that list
    """
    template_name = "lists/list.html"


class EditListView(TemplateView):
    """
    This view lets a user edit a list with id <list_id>

    Similar to NewListView, but it will show the items already in the list, and allow for more items to be added, whereas NewListView is blank
    """
    template_name = "lists/edit_list.html"


class PantryView(TemplateView):
    """
    This view displays the user's pantry
    """
    template_name = "lists/pantry.html"


    def get_context_data(self, **kwargs):
        context = super(PantryView, self).get_context_data(**kwargs)

        user = UserProfile.objects.get(user=self.request.user)

        party = Party.objects.filter(owner=user)[0]
        pantry = Pantry.objects.filter(party=party)[0]

        context['party'] = party
        context['pantry'] = pantry
        context['pantry_items'] = pantry.items.all()
        return context


class NewItemView(View):
    """
    This view adds a new item to a list, and returns the user to the lists page
    """
    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('new-item-name', False).title()
        item_desc = request.POST.get('new-item-description', False).capitalize()

        list_id = request.POST.get('list-id', False)
        list_obj = ShoppingList.objects.get(id=list_id)

        # Don't make empty items!
        if item_name == "":
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>ERROR: You must provide a name for the item.</span>", extra_tags=int(list_id))
            return redirect('/lists/#' + list_id)

        # Get or create item in database
        try:
            new_item, created = Item.objects.get_or_create(name=item_name, description=item_desc)
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Error: can't create or get that item.</span>", extra_tags=int(list_id))
            return redirect('/lists/#' + list_id)

        # Don't add duplicate items
        if new_item in list_obj.items.all():
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>That item already exists in the list.</span>", extra_tags=int(list_id))
            return redirect('/lists/#' + list_id)

        # Add item to list
        try:
            list_obj.items.add(new_item)
            list_obj.save()
            messages.add_message(request, messages.SUCCESS, "<span class='alert alert-success'>Success!  Added " + item_name + " to list!</span>", extra_tags=int(list_id))
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Unable to add " + item_name + " to list.</span>", extra_tags=int(list_id))

        return redirect('/lists/#' + list_id)


class NewListView(View):
    """
    This view lets a user add new items to a list, and submit that tentative list as a new list object
    """

    def post(self, request, *args, **kwargs):
        list_id = -1

        shoppinglist_name = request.POST.get('new-shoppinglist-name', False)
        shoppinglist_desc = request.POST.get('new-shoppinglist-desc', False)

        user_obj = UserProfile.objects.get(name=request.user.username)

        if shoppinglist_name == "":
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Error you must provide a name for your new shopping list.</span>", extra_tags=int(-1))
            return redirect('/lists/#new-list-error')

        try:
            new_list = ShoppingList.objects.create(name=shoppinglist_name, description=shoppinglist_desc)
            new_list.owners.add(user_obj)
            print list_id
            list_id = new_list.id
        except:
            messages.add_message(request, messages.ERROR,"<span class='alert alert-danger'>Error: can't create or get that item.</span>", extra_tags=int(1))

        return redirect('/lists/#')

class RemoveItemFromListView(View):
    """
    This view removes an item from a list and returns the user to their lists page
    """

    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('remove-item-name', False)
        item_desc = request.POST.get('remove-item-description', False)
        list_id = request.POST.get('list-id', False)

        item_obj = Item.objects.get(name=item_name, description=item_desc)
        list_obj = ShoppingList.objects.get(id=list_id)

        # Remove the item from the list
        try:
            list_obj.items.remove(item_obj)
            messages.add_message(request, messages.SUCCESS, "<span class='alert alert-success'>Successfully removed " + item_name + " from list</span>", extra_tags=int(list_id))
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Unable to remove " + item_name + " from list.</span>", extra_tags=int(list_id))

        return redirect("/lists/#" + list_id)


class AddItemToPantryView(View):
    """
    This view adds an item from a shopping list to a user's Pantry
    """

    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('add-item-to-pantry-name', False)
        item_description = request.POST.get('add-item-to-pantry-desc', False)
        amount = request.POST.get('add-item-to-pantry-stock', False)
        units = request.POST.get('add-item-to-pantry-unit', False)
        cost = request.POST.get('add-item-to-pantry-cost', False)
        location_purchased = request.POST.get('add-item-to-pantry-location-purchased', False)
        list_id = request.POST.get('list_id', False)

        date_pattern = re.compile('(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.](19|20)\d\d')

        print date_pattern.match('12/12/1993')

        last_purchased_str = request.POST.get('add-item-to-pantry-last-purchased', False)
        expiration_date_str = request.POST.get('add-item-to-pantry-expiration-date', False)


        # convert empty values to zero for non-required data
        if amount == "":
            amount = float(0)
        else:
            amount = float(amount)

        if cost == "":
            cost = float(0)
        else:
            cost = float(cost)


        # Don't let user supply zero amount
        if amount == float(0):
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>You must fill out the amount field to add " + item_name + " to your pantry.  Try again!</span>", extra_tags=int(list_id))
            return redirect("/lists/#" + list_id)


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

        # try to create itemdetail with passed values
        try:
            item_detail_obj, created = ItemDetail.objects.get_or_create(name=item_name,
                                                                        description=item_description,
                                                                        cost=cost,
                                                                        last_purchased=last_purchased,
                                                                        location_purchased=location_purchased,
                                                                        barcode=-1,
                                                                        unit=units,
                                                                        amount=amount,
                                                                        expiration_date=expiration_date)

            # User's pantry object
            user_userprofile = UserProfile.objects.get(name=request.user.username)
            user_party = Party.objects.get(owner=user_userprofile)
            pantry_obj = Pantry.objects.get(party=user_party)

            pantry_obj.items.add(item_detail_obj)

            # successful, return to lists page with success message
            messages.add_message(request, messages.SUCCESS, "<span class='alert alert-success'>" + str(amount) + " " + str(units) + " of " + str(item_name) + " has been added to your pantry!</span>", extra_tags=int(list_id))
            return redirect("/lists/#" + list_id)

        # Something went wront creating the Item Detail, give them an error
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Unable to create ItemDetail for that item.  Please let a developer know!</span>", extra_tags=int(list_id))
            return redirect("/lists/#" + list_id)


class DeleteListView(View):
    def post(self, request, *args, **kwargs):
        list_id = request.POST.get('list_id', False)

        # Get the Shopping List object
        try:
            list_obj = ShoppingList.objects.get(id=list_id)

            # Delete the object
            try:
                list_obj.delete()
                messages.add_message(request, messages.SUCCESS, "<span class='alert alert-success'>Successfully deleted your " + list_obj.name + " list for you.", extra_tags=int(-1))
                return redirect("/lists/#new-list-error")
            except:
                messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Unable to delete that list for you, sorry!  Please let a developer know!</span>", extra_tags=int(list_id))
                return redirect("/lists/#" + list_id)
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Unable to delete that list for you, sorry!  Please let a developer know!</span>", extra_tags=int(list_id))
            return redirect("/lists/#" + list_id)
