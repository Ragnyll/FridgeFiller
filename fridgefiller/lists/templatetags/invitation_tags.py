from django import template

from lists.models import Invitation

register = template.Library()

@register.filter
def has_unread_invitations(user):
    return Invitation.objects.filter(receiver=user.pk, read=False).exists()

@register.simple_tag(takes_context=True)
def unread_invitation_count(context):
    user = context['user']
    return Invitation.objects.filter(receiver=user.pk, read=False).count()
