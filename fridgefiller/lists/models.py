from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.auth.models import User

from datetime import datetime

import pytz

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    name = models.CharField(max_length=32, default="")
    description = models.TextField(default="")
    lists = models.ManyToManyField('ShoppingList')

    def __str__(self):
        return str(self.name)

def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a UserProfile object for new users who sign up with allauth
    """
    if created:
        userprofile, created = UserProfile.objects.get_or_create(user=instance, name=instance.username)

post_save.connect(create_user_profile, sender=User)

def create_user_party(sender, instance, created, **kwargs):
    """
    Creates a Party object for Users that just contains themselves
    """
    if created:
        userparty, created = Party.objects.get_or_create(name=instance.name + "'s Personal Party", owner=instance)
        print "Created party for {}".format(instance.name)

post_save.connect(create_user_party, sender=UserProfile)

class Party(models.Model):
    name = models.CharField(max_length=32, default="")
    owner = models.ForeignKey('UserProfile', related_name="owner")
    users = models.ManyToManyField('UserProfile')
    shoppinglists = models.ManyToManyField('ShoppingList')



    def __str__(self):
        return str(self.name)

    def is_user_on_team(self, user):
        """
        Returns true if user is on the calling team, else false
        """
        return self.users.filter(pk=user.pk).exists()

def create_party_pantry(sender, instance, created, **kwargs):
    """
    Creates a Pantry object when a Party is saved
    """
    if created:
        partypantry, created = Pantry.objects.get_or_create(party=instance)
        print "Created pantry for {}".format(instance.name)

post_save.connect(create_party_pantry, sender=Party)


# Adds owner to group's user list if they aren't already in there
@receiver(post_save, sender=Party)
def add_owner_to_users(sender, instance, **kwargs):
    if not instance.owner in instance.users.all():
        instance.users.add(instance.owner)

class ShoppingList(models.Model):
    name = models.CharField(max_length=32, default="")
    owners = models.ManyToManyField('UserProfile', related_name="owners")
    description = models.TextField(default="")
    items = models.ManyToManyField('Item')

    def __str__(self):
       return str(self.name)

class Pantry(models.Model):
    items = models.ManyToManyField('ItemDetail', related_name='items')
    description = models.CharField(max_length=64, default="")
    party = models.ForeignKey('Party', related_name='party')

    def __str__(self):
        return str(self.party.name + "'s Pantry")

class Item(models.Model):
    name = models.CharField(max_length=64, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self):
       return str(self.name)


# use default = null for optional stuff

class ItemDetail(models.Model):
    name = models.CharField(max_length=64, default="")
    description = models.TextField(blank=True, default="")
    cost = models.FloatField(default=0)
    last_purchased = models.DateTimeField(blank=True, default=datetime.min)
    location_purchased = models.CharField(max_length=64, blank=True, default="")
# barcode should be moved to its own entity once we gather what we need from it
    barcode = models.IntegerField(default=0, blank=True)
    unit = models.CharField(default=0, max_length=64)
    amount = models.FloatField(default=0)
    expiration_date = models.DateTimeField(blank=True, default=datetime.min)

    def get_cost(self):
        if self.cost == int(self.cost):
            self.cost = int(self.cost)

        if self.cost == 0:
            return "---"
        return self.cost

    def get_amount(self):
        if self.amount == int(self.amount):
            self.amount = int(self.amount)
        return self.amount

    def get_last_purchased(self):
        return self.last_purchased if self.last_purchased not in [datetime.min.replace(tzinfo=pytz.UTC), None] else "---"

    def get_expiration_date(self):
        return self.expiration_date if self.expiration_date not in [datetime.min.replace(tzinfo=pytz.UTC), None] else "---"

    def get_location_purchased(self):
        return self.location_purchased if self.location_purchased != "" else "---"

    def get_pretty_last_purchased(self):
        """
        Returns self.last_purchased as 'mm/dd/yyyy'
        """
        date_str = str(self.last_purchased.month) + "/" + str(self.last_purchased.day) + "/" + str(self.last_purchased.year)

        if date_str != "1/1/1":
            return date_str

        return ""

    def get_pretty_expiration_date(self):
        """
        Returns self.expiration_date as 'mm/dd/yyyy'
        """
        date_str = str(self.expiration_date.month) + "/" + str(self.expiration_date.day) + "/" + str(self.expiration_date.year)

        if date_str != "1/1/1":
            return date_str

        return ""



class Invitation(models.Model):
    class Meta:
        app_label = 'lists'
        ordering = ['-sent']

    RESPONSE_CHOICES = (('A', 'Accepted'),
                        ('D', 'Declined'))

    party = models.ForeignKey(Party)
    sender = models.ForeignKey(UserProfile, related_name="sent_invitations")
    receiver = models.ForeignKey(UserProfile, related_name="received_invitations")
    message = models.TextField()
    sent = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    response = models.CharField(blank=True, null=True, max_length=2,
                                choices=RESPONSE_CHOICES)

    @models.permalink
    def get_absolute_url(self):
        return ('invitation_detail', (), {'pk': self.pk})

    def __str__(self):
        return "%s invites %s to join %s" % (self.sender.name,
                                             self.receiver.name,
                                             self.party.name)

    def has_response(self):
        """Returns True if the receiver has responded, else False"""
        return self.response is not None

    def accept(self):
        """Accepts an invitation to join a team.
        Adds the invitation's recipient to the team. If the team is
        already full, throws an instance of TeamException """
        # If the user's already responded, don't let them respond again
        if self.has_response():
            return
        self.team.add_team_member(self.receiver)
        self.read = True
        self.response = 'A'     # Accepted
        self.save()

    def decline(self):
        """Declines an invitation to join a team.
        Just marks the invitation as declined"""
        # If the user's already responded, don't let them respond again
        if self.has_response():
            return
        self.read = True
        self.response = 'D'     # Declined
        self.save()
