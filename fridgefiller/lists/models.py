from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    name = models.CharField(max_length=32)
    description = models.TextField()
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
    name = models.CharField(max_length=32)
    owner = models.ForeignKey('UserProfile', related_name="owner")
    users = models.ManyToManyField('UserProfile')
    shoppinglists = models.ManyToManyField('ShoppingList')

    def __str__(self):
        return str(self.name)

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
        print "owner not in users"
        instance.users.add(instance.owner)

class ShoppingList(models.Model):
    name = models.CharField(max_length=32)
    owners = models.ManyToManyField('UserProfile', related_name="owners")
    description = models.TextField()
    items = models.ManyToManyField('Item')
    
    def __str__(self):
       return str(self.name)

class Pantry(models.Model):
    items = models.ManyToManyField('ItemDetail', related_name='items')
    description = models.CharField(max_length=64)
    party = models.ForeignKey('Party', related_name='party')
    
    def __str__(self):
        return str(self.party.name + "'s Pantry")

class Item(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
       return str(self.name)


# use default = null for optional stuff

class ItemDetail(Item):
    cost = models.FloatField(default=0)
    last_purchased = models.DateTimeField(null=True)
    location_purchased = models.CharField(max_length=64)
# barcode should be moved to its own entity once we gather what we need from it
    barcode = models.IntegerField(default=0, blank=True)
    unit = models.CharField(default=0, max_length=64)
    amount = models.FloatField(default=0)
    expiration_date = models.DateTimeField(null=True)

    def get_cost(self):
        if self.cost == int(self.cost):
            self.cost = int(self.cost)
        return self.cost

    def get_amount(self):
        if self.amount == int(self.amount):
            self.amount = int(self.amount)
        return self.amount

    def get_last_purchased(self):
        return self.last_purchased if self.last_purchased != None else "---"

    def get_expiration_date(self):
        return self.expiration_date if self.expiration_date != None else "---"

    def get_location_purchased(self):
        return self.location_purchased if self.location_purchased != "" else "---"
