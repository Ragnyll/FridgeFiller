from django.shortcuts import render
from django.views.generic import TemplateView
from .models import User, Party, ShoppingList


def disp_info(request):
    users = User.objects.all()
    parties = Party.objects.all()
    shoppinglists = ShoppingList.objects.all()
    return render(request, 'lists/disp_info.html',{'users': users})


class ListsView(TemplateView):
    """
    This view displays all shopping lists that a user owns
    """
    template_name = "lists/lists.html"


class ListView(TemplateView):
    """
    This view displays a singular list with id <list_id> and the items in that list
    """
    template_name = "lists/list.html"


class NewListView(TemplateView):
    """
    This view lets a user add new items to a list, and submit that tentative list as a new list object
    """
    template_name = "lists/new_list.html"


class EditListView(TemplateView):
    """
    This view lets a user edit a list with id <list_id>

    Similar to NewListView, but it will show the items already in the list, and allow for more items to be added, whereas NewListView is blank
    """
    template_name = "lists/edit_list.html"

