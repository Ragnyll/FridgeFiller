from django.shortcuts import render
from django.views.generic import TemplateView

from models import Ingredient, Recipe, Nutrition



class RecipesView(TemplateView):
    """
    This view will display a list of recipes that belong to the user
    """
    template_name = "food/recipes.html"


class NewRecipeView(TemplateView):
    """
    This view will display a form for a user to define and add a new recipe to their list of recipes
    """
    template_name = "food/new_recipe.html"
