from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
	list_display = ('name', 'description')

class GroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'owner')

class ListAdmin(admin.ModelAdmin):
	list_display = ('name', 'primary_owner', 'description')

class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'cost', 'description')

class IngredientAdmin(admin.ModelAdmin):
	list_display = ('name', 'recipe', 'unit', 'amount')

class RecipeAdmin(admin.ModelAdmin):
	list_display = ('recipe_name', 'serving_size')

class NutritionAdmin(admin.ModelAdmin):
	list_display = ('calories', 'total_fat', 'sodium', 'sugar', 'protein')

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Nutrition, NutritionAdmin)
