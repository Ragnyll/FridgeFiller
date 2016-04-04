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

from .models import *
from statuses import *
from mixins import *
from invitation_forms import InvitationForm


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
