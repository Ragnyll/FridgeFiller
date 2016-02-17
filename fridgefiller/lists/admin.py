from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(List)
admin.site.register(Item)
