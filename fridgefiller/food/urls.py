from django.conf.urls import url
from views import RecipesView, NewRecipeView

urlpatterns = [
    url(r'^$', RecipesView.as_view(), name="recipes"),
    url(r'^new-recipe', NewRecipeView.as_view(), name="new_recipe"),
]
