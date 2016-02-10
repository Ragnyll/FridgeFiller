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


@python_2_unicode_compatible
class Item(models.Model):
    name = models.CharField(max_length=64)
    in_list = models.ForeignKey('List')
    cost = models.DecimalField(default=0, max_digits= 8, decimal_places=2)
    location_purchased = models.CharField(max_length=64)
    description = models.TextField()
    # barcode should be moved to its own entity once we gather what we need from it
    barcode = models.IntegerField()
    

    def __str__(self):
       return str(self.name)

@python_2_unicode_compatible
class Ingredient(models.Model):
    name = models.ForeignKey('Item')
    recipe = models.ForeignKey('Recipe')
    unit = models.CharField(max_length=10, null=True)
    amount = models.FloatField(default=0)


    def __str__(self):
       return str(self.name)

@python_2_unicode_compatible
class Recipe(models.Model):
    recipe_name = models.CharField(max_length=250)
    serving_size = models.IntegerField(default=0)
    bigoven_id = models.IntegerField(unique=True)
    nutrition_info = models.OneToOneField('Nutrition', null=True)

    def __str__(self):
        return str(self.recipe_name)

class Nutrition(models.Model):
    calories = models.IntegerField(default=0)
    total_fat = models.IntegerField(default=0)
    sodium = models.IntegerField(default=0)
    sugar = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)
