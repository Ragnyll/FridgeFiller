from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")

    name = models.CharField(max_length=32)
    description = models.TextField()
    lists = models.ManyToManyField('List')
    
    def __str__(self):
        return str(self.name)


class Group(models.Model):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey('User', related_name="owner")
    users = models.ManyToManyField('User')

    def __str__(self):
        return str(self.name)

# Adds owner to group's user list if they aren't already in there    
@receiver(post_save, sender=Group)
def add_owner_to_users(sender, instance, **kwargs):
    if not instance.owner in instance.users.all():
        print "owner not in users"
        instance.users.add(instance.owner)

class List(models.Model):
    name = models.CharField(max_length=32)
    primary_owner = models.ForeignKey('User', related_name="primary_owner")
    secondary_owners = models.ManyToManyField('User', related_name="secondary_owners")
    description = models.TextField()
    items = models.ManyToManyField('Item')
    

    def __str__(self):
       return str(self.name)

class Item(models.Model):
    name = models.CharField(max_length=64)
    cost = models.FloatField(default=0)
    location_purchased = models.CharField(max_length=64)
    description = models.TextField()
# barcode should be moved to its own entity once we gather what we need from it
    barcode = models.IntegerField()
    

    def __str__(self):
       return str(self.name)


