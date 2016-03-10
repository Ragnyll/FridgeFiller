from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML
from crispy_forms.bootstrap import FormActions

from .models import Invitation


cancel_button = """
<a href="{% url 'invitation_list' %}" class="btn">
  Cancel
</a>
"""

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ('party', 'receiver', 'message',)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Send an Invitation',
                'party',
                'receiver',
                'message'
            ),
            FormActions (
                Submit('submit', 'Submit'),
                HTML(cancel_button)
            )
        )
        super(InvitationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(InvitationForm, self).clean()

        # Make sure the team has invites left
        party = cleaned_data.get('party', None)
        #if party is not None:
         #   if team.num_invites_left() <= 0:
          #      msg = "Your party has already sent all available party "
           #     msg += "invitations! Please check your pending invitations."
            #    raise ValidationError(msg)

        return cleaned_data

    def clean_receiver(self):
        receiver = self.cleaned_data['receiver']
        party = self.cleaned_data.get('party', None)

        # Make sure the user isn't already on the team they're being
        # invited to.
        if party is not None:
            if party.is_user_on_team(receiver):
                msg = "%s is already in your group"
                raise ValidationError(msg % receiver)

        return receiver

    def clean_team(self):
        party = self.cleaned_data['party']

        # Make sure the competition is open for team changes

        #if not team.competition.is_open:
         #   msg = "%s is not currently open for team changes"
          #  raise ValidationError(msg % team.competition.name)

        return party