from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout_then_login

from lists.views import PantryView, AddItemToPantryView, EditItemInPantryView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # List App
    url(r'^lists/', include('lists.urls')),

    # User's pantry
    url(r'^pantry/$', PantryView.as_view(), name="pantry"),
    url(r'^pantry/add/item/', AddItemToPantryView.as_view(), name="add-item-to-pantry"),
    url(r'^pantry/edit/item/', EditItemInPantryView.as_view(), name="edit-item-in-pantry"),

    # Home App
    url(r'^$', include('home.urls')),

    # Django AllAuth
    url(r'^accounts/logout/$', logout_then_login),
    url(r'^accounts/', include('allauth.urls')),

]
