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
        
class Party(models.Model):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey('UserProfile', related_name="owner")
    users = models.ManyToManyField('UserProfile')
    shoppinglists = models.ManyToManyField('ShoppingList')

    def __str__(self):
        return str(self.name)

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

class Item(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
       return str(self.name)


# use default = null for optional stuff

class ItemDetail(Item):
    cost = models.FloatField(default=0)
    last_purchased = models.DateTimeField(blank=True)
    location_purchased = models.CharField(max_length=64)
# barcode should be moved to its own entity once we gather what we need from it
    barcode = models.IntegerField(default=0, blank=True)
    unit = models.CharField(default=0, max_length=64)
    amount = models.FloatField(default=0)
    expiration_date = models.DateTimeField(blank=True)

    
