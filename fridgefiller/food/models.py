from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Ingredient(models.Model):
    name = models.ForeignKey('Item')
    recipe = models.ForeignKey('Recipe')
    unit = models.CharField(max_length=10, null=True)
    amount = models.FloatField(default=0)

    def __str__(self):
       return str(self.name)

class Recipe(models.Model):
    recipe_name = models.CharField(max_length=250)
    serving_size = models.IntegerField(default=0)
    bigoven_id = models.IntegerField(unique=True) # For BigOven Recipe API
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
