from django.db import models

class User(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    
    def __str__(self):
        return str(self.name)


class Group(models.Model):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey('User')
    # available lists

    def __str__(self):
        return str(self.name)


class List(models.Model):
    name = models.CharField(max_length=32)
    primary_owner = models.ForeignKey('User')
    description = models.TextField()
    # secondary_owners

    def __str__(self):
       return str(self.name)

class Item(models.Model):
    name = models.CharField(max_length=64)
    in_list = models.ForeignKey('List')
    cost = models.FloatField(default=0)
    location_purchased = models.CharField(max_length=64)
    description = models.TextField()
    # barcode should be moved to its own entity once we gather what we need from it
    barcode = models.IntegerField()
    

    def __str__(self):
       return str(self.name)


