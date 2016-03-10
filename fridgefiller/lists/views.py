from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views.generic import TemplateView, UpdateView, View, DetailView, CreateView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

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
        user_party = Party.objects.get(owner=user)
        user_pantry = Pantry.objects.get(party=user_party)
        
        user_pantry_item_names = [x.name for x in user_pantry.items.all()]

        context['user_pantry_item_names'] = user_pantry_item_names
        context['user_pantry'] = user_pantry
        context['user_shopping_lists'] = ShoppingList.objects.filter(owners__in=[user])
        
        return context
    
    
class ListView(TemplateView):
    """
    This view displays a singular list with id <list_id> and the items in that list
    """
    template_name = "lists/list.html"


class NewListView(TemplateView):
    """
    This view lets a user add new items to a list, and submit that tentative list as a new list object
    """
    template_name = "lists/new_list.html"


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

        return redirect("/lists")

class PartyView(TemplateView):
    """
    This view displays a party with <party-id> and the party's users 
    """
    template_name = "lists/party.html"

    def get_context_data(self, **kwargs):
        context = super(PartyView, self).get_context_data(**kwargs)

        party = Party.objects.get(id=kwargs['party_id'])
        user = UserProfile.objects.get(user=self.request.user)
        context['party'] = party
        context['cuser'] = user
        context['users'] = party.users.all()
        context['party_lists'] = party.shoppinglists.all()
        context['party_pantry'] = Pantry.objects.filter(party__in=[party])
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
        try:
            party_obj.users.remove(user)
            messages.add_message(request, messages.SUCCESS, "<span class='alert alert-success'>Successfully left " + party_obj.name + "</span>")
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'> Error in leaving " + party_obj.name + "</span>")
       
        return redirect("/lists/parties")

class InvitetoParty(View):
    """
    This view contains logic to invite a person to a party
    """
    def post(self, request, *args, **kwargs):
        party_id = request.POST.get('party-id', False)
        party_obj = Party.objects.get(id=party_id)

        return redirect("/lists/parties")

class CreateParty(View):
    """
    This view contains logic to create a new party
    """
    def post(self, request, *args, **kwargs):
        #do something
        return redirect("/lists/parties")

class AddPartyList(View):
    """
    This view contains logic to add a shopping list to a party
    """

    def post(self, request, *args, **kwargs):
        #do something?
        return redirect("/lists/parties")

class PartiesView(TemplateView):
    """
    This view displays a list of partys a user belongs too
    """
    template_name = "lists/parties.html"

    def get_context_data(self, **kwargs):
        context = super(PartiesView, self).get_context_data(**kwargs)

        user = UserProfile.objects.get(user=self.request.user)
        
        context['party_own'] = Party.objects.filter(owner__in=[user])
        context['user_parties'] = Party.objects.filter(users__in=[user])

        return context

class AddItemToPantryView(View):
    """
    This view adds an item from a shopping list to a user's Pantry
    """

    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('add-item-to-pantry-name', False)
        item_description = request.POST.get('add-item-ro-pantry-desc', False)
        amount = request.POST.get('add-item-to-pantry-stock', False)
        units = request.POST.get('add-item-to-pantry-unit', False)
        cost = request.POST.get('add-item-to-pantry-cost', False)
        location_purchased = request.POST.get('add-item-to-pantry-location-purchased', False)
        list_id = request.POST.get('list_id', False)

        date_pattern = re.compile('/(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.](19|20)\d\d/')

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

class InvitationListView(LoggedInMixin, TemplateView):
    """Lists all teams, provided that the user is logged in"""
    #template_name = 'competition/invitation/invitation_list.html'
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
        user = self.request.user
        invitations = Invitation.objects.filter(Q(sender=user) | Q(receiver=user))
        received = self.process_page(invitations.filter(receiver=user),
                                     'received_page')
        sent = self.process_page(invitations.filter(sender=user),
                                 'sent_page')
        context.update({'received': received, 'sent': sent})
        return context


class InvitationDetailView(LoggedInMixin, DetailView):
    """Show details about a particular team"""
    #template_name = 'competition/invitation/invitation_detail.html'
    context_object_name = 'invitation'

    def get_queryset(self):
        """Only show invitations for this user"""
        user = self.request.user
        return Invitation.objects.filter(Q(sender=user) | Q(receiver=user))

    def get_object(self, queryset=None):
        """When we fetch the invitation, mark it as read"""
        obj = super(InvitationDetailView, self).get_object(queryset)
        if self.request.user == obj.receiver:
            obj.read = True
            obj.save()
        return obj


class InvitationCreateView(LoggedInMixin,
                           CreateView):
    """Allow users to create invitations"""
   # template_name = 'competition/invitation/invitation_create.html'
    form_class = InvitationForm

    def get_available_teams(self):
        """Returns a list of competitions that are open for
        registration and team changes"""

        #Should just list all parties but not person parties
        parties = Party.objects.all()
        
        if not parties.exists():
            msg = "Can't send invites at this time. It looks"
            msg += " like there are no groups"
            messages.error(self.request, msg)
            raise Http404(msg)
        return parties

    def get_available_invitees(self):
        """Returns a list of users who can be invited"""
        return UserProfile.objects.all()

    def get_team(self):
        """If the user provided a 'party' query parameter, look up the
        team. Otherwise return None"""
        try:
            party_id = self.request.GET.get('party')
            if party_id is not None:
                party_id = int(party_id)
                return self.get_available_teams().get(pk=party_id)
            return self.get_available_teams().latest()
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
        form.fields["party"].queryset = self.get_available_teams()
        form.fields["party"].empty_label = None
        return form

    def get_form_kwargs(self):
        # Set up keyword arguments for a new Invitation
        invitation_kwargs = (('sender', self.request.user),
                             ('receiver', self.get_invitee()),
                             ('party', self.get_team()))

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
        # Competition has to be open
        #if not self.invitation.team.competition.is_open:
         #   logger.debug("Can't change invite. Competition closed")
          #  return False
        # They can't accept or decline again if they've already
        # responded
        if self.invitation.has_response():
            logger.debug("Can't change invite. Already responded")
            return False
        # They can't accept or decline if the message wasn't meant for
        # them.
        if request.user != self.invitation.receiver:
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
    #template_name = 'competition/invitation/invitation_accept.html'

    #def get_question(self):
     #   msg = "Are you sure you want to accept your invitation to join %s?"
    #    msg += " Joining another team will cause you to automatically leave"
    #    msg += " any teams that you're on right now."
    #    return msg % self.invitation.party.name

    def agreed(self):
        #competition = self.invitation.party.competition
        invitee = self.invitation.receiver
        #if not competition.is_user_registered(invitee):
            # If the user isn't registered, make them register
         #   msg = "You need to register for %s before you can join a team"
          #  messages.error(self.request, msg % competition.name)
           # url = reverse('register_for',
            #              kwargs={'comp_slug': competition.slug})
            #query = urllib.urlencode(
            #    {'next': self.invitation.get_absolute_url()}
            #)
            #return redirect(url + '?' + query)

        self.invitation.accept()

        msg = "Successfully joined %s" % self.invitation.party.name
        messages.success(self.request, msg)
        return redirect(self.invitation.party)

    def disagreed(self):
        return redirect(self.invitation.party.competition)


class InvitationDeclineView(InvitationResponseView):
    """Allows a user to decline an invitation"""
    #template_name = 'competition/invitation/invitation_decline.html'

    def get_question(self):
        msg = "Are you sure you want to decline your invitation to join %s?"
        return msg % self.invitation.party.name

    def agreed(self):
        self.invitation.decline()

        msg = "Successfully declined to join %s" % self.invitation.party.name
        messages.success(self.request, msg)
        return redirect(self.invitation.party)

    def disagreed(self):
        return redirect(self.invitation.party)