from django import forms
from django.http import Http404
from django.contrib import messages
from django.views.generic import View
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

import logging

logger = logging.getLogger(__name__)

class LoggedInMixin(View):
    """A mixin class for checking that a user is logged in"""
    redirect_field_name = "next"
    login_url = None

    def login_required(self, dispatch_function):
        """Wraps a function with login_required. Intended to be used
        to wrap a View's dispatch function"""
        return login_required(dispatch_function,
                              redirect_field_name=self.redirect_field_name,
                              login_url=self.login_url)

    def dispatch(self, request, *args, **kwargs):
        """Overrides dispatch by wrapping dispatch with
        login_required"""
        parent = super(LoggedInMixin, self)
        wrapped_function = self.login_required(parent.dispatch)
        return wrapped_function(request, *args, **kwargs)


class ConfirmationMixin(FormView):
    question = None
    check_box_label = "OK"

    def get_question(self):
        if self.question is None:
            raise Exception("question not set for ConfirmationMixin")
        return self.question

    def get_check_box_label(self):
        return self.check_box_label

    def get_context_data(self, **kwargs):
        kwargs['question'] = self.get_question()
        return super(FormView, self).get_context_data(**kwargs)

    def get_form_class(self):

        class ConfirmationForm(forms.Form):
            confirmed = forms.BooleanField(required=False,
                                           label=self.get_check_box_label())

        return ConfirmationForm

    def form_valid(self, form):
        if form.cleaned_data['confirmed']:
            return self.agreed()
        return self.disagreed()

    def agreed(self):
        """If the user agreed, redirect them to the success url"""
        return redirect(self.get_success_url())

    def disagreed(self):
        """If the user disagreed, redirect them to the success url"""
        return redirect(self.get_success_url())


class CheckAllowedMixin(View):
    """This mixin throws a 404 if certain conditions are not met.
    At the beginning of the request, this mixin calls
    ``check_if_allowed()`` to see if the user is allowed to view the
    page. If not, it calls ``get_error_message()``, sets an error
    message with level ``self.message_level``, and calls
    ``was_not_allowed`` to determine how to handle the error. The
    default is to throw a 404.
    If the user is allowed to view the page, everything proceeds as
    usual.
    """
    error_message = "You cannot do that"
    message_level = messages.INFO

    def dispatch(self, request, *args, **kwargs):
        is_allowed = self.check_if_allowed(request)
        if not isinstance(is_allowed, bool):
            msg = "check_if_allowed method returned something "
            msg += "other than True or False"
            logger.warning(msg)
        if not is_allowed:
            msg = self.get_error_message(request)
            messages.add_message(request, self.message_level, msg)
            return self.was_not_allowed(request)

        parent = super(CheckAllowedMixin, self)
        return parent.dispatch(request, *args, **kwargs)

    def check_if_allowed(self, request):
        """Called to see if a user is allowed to view this page. It
        should return True if they're allowed, and False otherwise.
        """
        raise Exception("check_if_allowed() is not overridden.")

    def get_error_message(self, request):
        """Called to get the user's error message. If not overridden,
        we'll just use ``self.error_message``
        """
        return self.error_message

    def was_not_allowed(self, request):
        """Called if check_if_allowed returned False. If not
        overridden, we'll just throw a 404"""
        raise Http404(self.get_error_message(request))
