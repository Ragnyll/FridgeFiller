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

from mixins import *
from invitation_forms import InvitationForm

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
        user_party = Party.objects.get(name=user.name+"'s Personal Party")
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
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;: You must provide a name for the item." + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect('/lists/#' + list_id)

        # Get or create item in database
        try:
            new_item = Item.objects.get(name=item_name, description=item_desc)
        except Item.MultipleObjectsReturned:
            new_item = Item.objects.filter(name=item_name, description=item_desc)[0]
        except Item.DoesNotExist:
            new_item = Item.objects.create(name=item_name, description=item_desc)
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;: Can't create or get that item.  Please let a developer know!" + ALER_CLOSE, extra_tags=int(list_id))
            return redirect('/lists/#' + list_id)

        # Don't add duplicate items
        if new_item in list_obj.items.all():
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:That item already exists in the list." + ALERT_CLOSE, extra_tags=int(list_id))
            return redirect('/lists/#' + list_id)

        # Add item to list
        try:
            list_obj.items.add(new_item)
            list_obj.save()
            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;!  Added <strong>&nbsp;" + item_name + "</strong>&nbsp;&nbsp;to list!" + ALERT_CLOSE, extra_tags=int(list_id))
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:Unable to add <strong>&nbsp;" + item_name + "</strong>&nbsp;&nbsp;to list." + ALERT_CLOSE, extra_tags=int(list_id))

        return redirect('/lists/#' + list_id)


class NewListView(View):
    """
    This view lets a user add new items to a list, and submit that tentative list as a new list object
    """
    def post(self, request, *args, **kwargs):
        list_id = -1

        shoppinglist_name = request.POST.get('new-shoppinglist-name', False).title()
        shoppinglist_desc = request.POST.get('new-shoppinglist-desc', False).capitalize()

        user_obj = UserProfile.objects.get(name=request.user.username)

        if shoppinglist_name == "":
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;: You must provide a name for your new shopping list." + ALERT_CLOSE, extra_tags=int(-1))
            return redirect('/lists/#new-list-error')

        try:
            new_list = ShoppingList.objects.create(name=shoppinglist_name, description=shoppinglist_desc)
            new_list.owners.add(user_obj)
            print list_id
            list_id = new_list.id

            user_obj.lists.add(new_list)
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;: Can't create or get that item.  Please let a developer know!" + ALERT_CLOSE, extra_tags=int(1))

        return redirect('/lists/#')

class RemoveItemFromListView(View):
    """
    This view removes an item from a list and returns the user to their lists page
    """

    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('remove-item-name', False)
        item_desc = request.POST.get('remove-item-description', False)
        list_id = request.POST.get('list-id', False)

        item_obj = Item.objects.filter(name=item_name, description=item_desc)[0]
        list_obj = ShoppingList.objects.get(id=list_id)

        # Remove the item from the list
        try:
            list_obj.items.remove(item_obj)
            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;: Removed <strong>&nbsp;" + item_name + "</strong>&nbsp;&nbsp;from list." + ALERT_CLOSE, extra_tags=int(list_id))
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;: Unable to remove <strong>&nbsp;" + item_name + "</strong>&nbsp;&nbsp;from list.  Please let e developer know!" + ALERT_CLOSE, extra_tags=int(list_id))

        return redirect("/lists")


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


class PrintListMiniView(TemplateView):
    template_name = "lists/print.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Ensures that only authenticated users can access the view.
        """
        return super(PrintListMiniView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PrintListMiniView, self).get_context_data(**kwargs)
        user = UserProfile.objects.get(user=self.request.user)

        try:
            item_list = user.lists.get(pk=kwargs["list_id"])
        except :
            raise Http404

        context["id"] = kwargs["list_id"]
        context["data"] = [(i.name, i.description) for i in item_list.items.all()]
        return context


class PrintListView(View):
    """
    This view presents a list in a minimalisitic way for printing
    """
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        list_id = request.POST.get('list-id', False)
        return redirect("print-m-list", list_id=list_id)


class AddItemToPantryView(View):
    """
    This view adds an item from a shopping list to a user's Pantry
    """

    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('add-item-to-pantry-name', False).title()
        item_description = request.POST.get('add-item-to-pantry-desc', False).capitalize()
        list_id = request.POST.get('list_id', False)
        from_url = request.POST.get('from_url', False)

        if from_url == "/pantry/":
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
            user_party = Party.objects.get(owner=user_userprofile)
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

        date_pattern = re.compile('(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.](19|20)\d\d')

        last_purchased_str = request.POST.get('edit-item-in-pantry-last-purchased', False)
        expiration_date_str = request.POST.get('edit-item-in-pantry-expiration-date', False)


        if from_url == "/pantry/":
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
            user_party = Party.objects.get(owner=user_userprofile)
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

        # Get the user's pantry object
        party_obj = Party.objects.get(owner=request.user.profile)
        pantry_obj = Pantry.objects.get(party=party_obj)
        item_obj = pantry_obj.items.get(id=item_id)

        # remove the item from the pantry
        try:
            pantry_obj.items.remove(item_obj)

            messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;:  Removed <strong>&nbsp;" + item_obj.name + "</strong>&nbsp; from " + pantry_obj.party.owner.name + "'s pantry." + ALERT_CLOSE, extra_tags=int(item_id))
            return redirect(from_url + "#" + item_id)
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  Unable to remove <strong>&nbsp;" + item_obj.name + "</strong>&nbsp; from " + pantry_obj.party.owner.name + "'s pantry.  Please let a developer know!" + ALERT_CLOSE, extra_tags=int(item_id))
            return redirect(from_url + "#" + item_id)


class InvitationListView(LoggedInMixin, TemplateView):
    """Lists all teams, provided that the user is logged in"""
    template_name = 'lists/invitation/invitation_list.html'
    paginate_by = 10

    def process_page(self, items, query_param):
        paginator = Paginator(items, self.paginate_by)
        page_num = self.request.GET.get(query_param)

        try:
            return paginator.page(page_num)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def get_context_data(self, **kwargs):
        context = super(InvitationListView, self).get_context_data(**kwargs)
        user = UserProfile.objects.get(user=self.request.user)
        invitations = Invitation.objects.filter(Q(sender=user) | Q(receiver=user))
        received = self.process_page(invitations.filter(receiver=user),
                                     'received_page')
        sent = self.process_page(invitations.filter(sender=user),
                                 'sent_page')
        context.update({'received': received, 'sent': sent})
        return context


class InvitationDetailView(LoggedInMixin, DetailView):
    """Show details about a particular team"""
    template_name = 'lists/invitation/invitation_detail.html'
    context_object_name = 'invitation'


    def get_queryset(self):
        """Only show invitations for this user"""
        user = UserProfile.objects.get(user=self.request.user)
        return Invitation.objects.filter(Q(sender=user) | Q(receiver=user))

    def get_object(self, queryset=None):
        """When we fetch the invitation, mark it as read"""
        obj = super(InvitationDetailView, self).get_object(queryset)
        if UserProfile.objects.get(user=self.request.user) == obj.receiver:
            obj.read = True
            obj.save()
        return obj


class InvitationCreateView(LoggedInMixin,
                           CreateView):
    """Allow users to create invitations"""
    template_name = 'lists/invitation/invitation_create.html'
    form_class = InvitationForm

    def get_context_data(self, **kwargs):
        context = super(InvitationCreateView, self).get_context_data(**kwargs)

        try:
            party_id = self.request.GET.urlencode().split("=")[1]
        except:
            party_id = None


        if party_id:
            party = Party.objects.get(id=party_id)

            context['party'] = party

        return context

    def get_available_parties(self):
        """Returns a list of parties that the user can invite people to"""

        user = self.request.user.profile

        # Only return parties which:
        #    - User owns
        #    - Is not user's Personal Party
        parties = Party.objects.filter(owner__in=[user]).exclude(name=user.name+"'s Personal Party")

        return parties

    def get_available_invitees(self):
        """Returns a list of users who can be invited"""

        user = self.request.user.profile

        # All users can be invited to any party, except yourself.
        #   -> Logic that says 'user is already in that party' will be handled
        #      in accept invite view
        return UserProfile.objects.all().exclude(name=user)

    def get_team(self):
        """If the user provided a 'party' query parameter, look up the
        team. Otherwise return None"""
        try:
            party_id = self.request.GET.get('party')
            if party_id is not None:
                party_id = int(party_id)
                return self.get_available_teams().get(pk=party_id)
            return self.get_available_teams()[1]
        except (Party.DoesNotExist, ValueError):
            return None

    def get_invitee(self):
        """If the user provided a 'invitee' query parameter, look up the
        team. Otherwise return None"""
        try:
            invitee_id = int(self.request.GET['invitee'])
            return self.get_available_invitees().get(pk=invitee_id)
        except (UserProfile.DoesNotExist, KeyError, ValueError):
            return None

    def get_form(self, form_class):
        """Limit the teams that the user can choose from to the teams
        that they are a member of"""
        form = super(InvitationCreateView, self).get_form(form_class)
        form.fields["receiver"].queryset = self.get_available_invitees()
        form.fields["party"].queryset = self.get_available_parties()
        form.fields["party"].empty_label = None
        return form

    def get_form_kwargs(self):
        # Set up keyword arguments for a new Invitation
        invitation_kwargs = (('sender', UserProfile.objects.get(user=self.request.user)),
                             ('receiver', self.get_invitee()),
                             )#('party', self.get_team()))

        # Filter out the values that are None (e.g., if the 'team'
        # query parameter wasn't set, self.get_team() will be None, so
        # we need to filter it out)
        invitation_kwargs = dict((k, v) for (k, v) in invitation_kwargs
                                 if v is not None)

        # Get the default form keyword arguments created by CreateView
        form_kwargs = super(InvitationCreateView, self).get_form_kwargs()

        # Set our instance with our special keyword arguments and
        # return it
        form_kwargs['instance'] = Invitation(**invitation_kwargs)
        return form_kwargs


class InvitationResponseView(LoggedInMixin,
                             CheckAllowedMixin,
                             ConfirmationMixin):
    """Allows a user to accept or decline an invitation"""
    error_message = 'Cannot accept or decline this invitation at this time'

    def dispatch(self, request, *args, **kwargs):
        """Sets up self.kwargs since we don't have that by default :/"""
        self.kwargs = kwargs
        parent = super(InvitationResponseView, self)
        return parent.dispatch(request, *args, **kwargs)

    def check_if_allowed(self, request):
        # They can't accept or decline again if they've already
        # responded
        if self.invitation.has_response():
            logger.debug("Can't change invite. Already responded")
            return False
        # They can't accept or decline if the message wasn't meant for
        # them.
        if request.user.profile != self.invitation.receiver:
            logger.debug("Can't change invite. Not yours.")
            return False

        # Otherwise we're in good shape.
        return True

    @property
    def invitation(self):
        if not hasattr(self, '_invitation'):
            logger.debug("Fetching invitation")
            invitations = Invitation.objects.select_related()
            self._invitation = get_object_or_404(invitations,
                                                 pk=self.kwargs['pk'])
            logger.debug("Invitation Fetched")
        return self._invitation

    def get_check_box_label(self):
        return "Yes I'm sure"


class InvitationAcceptView(InvitationResponseView):
    """Allows a user to accept an invitation"""
    def agreed(self):
        invitee = self.invitation.receiver

        self.invitation.accept()

        messages.add_message(self.request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;: Joined&nbsp;<strong>" + self.invitation.party.name + "</strong>." + ALERT_CLOSE)

        return redirect("/parties/")

    def disagreed(self):
        return redirect("/parties")


class InvitationDeclineView(InvitationResponseView):
    """Allows a user to decline an invitation"""

    def get_question(self):
        msg = "Are you sure you want to decline your invitation to join %s?"
        return msg % self.invitation.party.name

    def agreed(self):
        self.invitation.decline()

        messages.add_message(self.request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;: Declined invitation to&nbsp;<strong>" + self.invitation.party.name + "</strong>." + ALERT_CLOSE)

        return redirect(self.invitation.party)

    def disagreed(self):
        return redirect(self.invitation.party)


class DeleteListView(View):
    def post(self, request, *args, **kwargs):
        list_id = request.POST.get('list_id', False)

        # Get the Shopping List object
        try:
            list_obj = ShoppingList.objects.get(id=list_id)

            # Delete the object
            try:
                list_obj.delete()
                messages.add_message(request, messages.SUCCESS, ALERT_SUCCESS_OPEN + "<strong>SUCCESS</strong>&nbsp;:  Deleted your <strong>&nbsp;" + list_obj.name + "</strong>&nbsp;&nbsp;list for you." + ALERT_CLOSE, extra_tags=int(-1))
                return redirect("/lists/#new-list-error")
            except:
                messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  Unable to delete that list for you, sorry!  Please let a developer know!" + ALERT_CLOSE, extra_tags=int(list_id))
                return redirect("/lists/#" + list_id)
        except:
            messages.add_message(request, messages.ERROR, ALERT_ERROR_OPEN + "<strong>ERROR</strong>&nbsp;:  Unable to delete that list for you, sorry!  Please let a developer know!</span>", extra_tags=int(list_id))
            return redirect("/lists/#" + list_id)
