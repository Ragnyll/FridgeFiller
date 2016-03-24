from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'description')

class PartyAdmin(admin.ModelAdmin):
	list_display = ('name', 'owner')

class ListAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'created', 'updated')

class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'description')

class PantryAdmin(admin.ModelAdmin):
	list_display = ('description','party')

class ItemDetAdmin(admin.ModelAdmin):
	list_display = ('name', 'cost', 'last_purchased', 'location_purchased', 'unit', 'amount', 'expiration_date')

admin.site.register(UserProfile, UserAdmin)
admin.site.register(Party, PartyAdmin)
admin.site.register(ShoppingList, ListAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Pantry, PantryAdmin)
admin.site.register(ItemDetail, ItemDetAdmin)


