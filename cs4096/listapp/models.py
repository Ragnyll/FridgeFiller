from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class User(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    
    def __str__(self):
        return str(self.name)

@python_2_unicode_compatible
class Group(models.Model):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey('User')
    # available lists

    def __str__(self):
        return str(self.name)

@python_2_unicode_compatible
class List(models.Model):
    name = models.CharField(max_length=32)
    primary_owner = models.ForeignKey('User')
    description = models.TextField()
    # secondary_owners

    def __str__(self):
       return str(self.name)

